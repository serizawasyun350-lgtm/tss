import os
import discord
from discord import app_commands
from discord.ext import commands
from gtts import gTTS
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    # スラッシュコマンドをDiscordに同期（登録）する
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}個のコマンドを同期しました！")
    except Exception as e:
        print(f"コマンド同期エラー: {e}")
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")

# /tts コマンドの定義
@bot.tree.command(name="tts", description="入力したテキストをボイスチャンネルで読み上げます")
@app_commands.describe(text="読み上げたい文章")
async def tts(interaction: discord.Interaction, text: str):
    if not interaction.user.voice:
        await interaction.response.send_message("先にボイスチャンネルに参加してください！", ephemeral=True)
        return

    # 音声生成に時間がかかる場合があるため、先に応答を保留（考え中...）にする
    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    if voice_client:
        if voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)
    else:
        voice_client = await voice_channel.connect()

    # 音声ファイル生成
    tts_obj = gTTS(text=text, lang='ja')
    audio_file = f"sound_{interaction.guild.id}.mp3"
    tts_obj.save(audio_file)

    if voice_client.is_playing():
        voice_client.stop()

    def after_playing(error):
        if os.path.exists(audio_file):
            os.remove(audio_file)

    source = discord.FFmpegPCMAudio(audio_file)
    voice_client.play(source, after=after_playing)
    await interaction.followup.send(f"読み上げ中: {text}")

# /leave コマンドの定義
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
