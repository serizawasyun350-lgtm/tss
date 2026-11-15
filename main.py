import os
import discord
from discord import app_commands
from discord.ext import commands
from gtts import gTTS
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True  # メッセージの内容を読むために必須
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}個のコマンドを同期しました！")
    except Exception as e:
        print(f"コマンド同期エラー: {e}")
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")

# --- 自動読み上げ機能（特定のチャンネル用） ---
@bot.event
async def on_message(message):
    # ボット自身のメッセージは無視する
    if message.author.bot:
        return

    # 「いのちゃんねる」という名前のチャンネルでの発言かチェック
    if message.channel.name == "いのちゃんねる":
        # ボットがボイスチャンネルに参加しているか確認
        voice_client = message.guild.voice_client
        if voice_client and voice_client.is_connected():
            # 音声ファイル生成
            tts_obj = gTTS(text=message.content, lang='ja')
            audio_file = f"sound_auto_{message.guild.id}.mp3"
            tts_obj.save(audio_file)

            if voice_client.is_playing():
                voice_client.stop()

            def after_playing(error):
                if os.path.exists(audio_file):
                    os.remove(audio_file)

            source = discord.FFmpegPCMAudio(audio_file)
            voice_client.play(source, after=after_playing)

    # コマンド機能も動かすために必要（これを書かないと /tts や /leave が動かなくなります）
    await bot.process_commands(message)

# /tts コマンド（手動用）
@bot.tree.command(name="tts", description="ボットをボイスチャンネルに参加させます")
async def tts(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("先にボイスチャンネルに参加してください！", ephemeral=True)
        return

    await interaction.response.defer()
    voice_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    if voice_client:
        if voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)
    else:
        await voice_channel.connect()

    await interaction.followup.send("ボイスチャンネルに参加しました！「いのちゃんねる」に文字を打つと自動で読み上げます。")

# /leave コマンド
@bot.tree.command(name="leave", description="ボイスチャンネルから切断します")
async def leave(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await interaction.response.send_message("ボイスチャンネルから切断しました。")
    else:
        await interaction.response.send_message("ボイスチャンネルに参加していません。", ephemeral=True)

keep_alive()
bot.run(os.environ["DISCORD_BOT_TOKEN"])
