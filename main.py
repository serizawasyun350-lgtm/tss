import os
import discord
from discord.ext import commands
from gtts import gTTS
from keep_alive import keep_alive

# intentsの設定（メッセージ内容とボイスステータスを取得するため）
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")

@bot.command(name="tts")
async def tts(ctx, *, text: str):
    # ユーザーがボイスチャンネルに入っているか確認
    if not ctx.author.voice:
        await ctx.send("先にボイスチャンネルに参加してください！")
        return

    voice_channel = ctx.author.voice.channel

    # すでに別のチャンネルに接続している場合は移動、していなければ接続
    if ctx.voice_client:
        if ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)
    else:
        await voice_channel.connect()

    # gTTSで音声ファイル（MP3）を生成
    tts_obj = gTTS(text=text, lang='ja')
    audio_file = "sound.mp3"
    tts_obj.save(audio_file)

    # 再生中の音声が重ならないようにチェック
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    # 再生終了後にファイルを削除するコールバック
    def after_playing(error):
        if os.path.exists(audio_file):
            os.remove(audio_file)

    source = discord.FFmpegPCMAudio(audio_file)
    ctx.voice_client.play(source, after=after_playing)
    await ctx.send(f"読み上げ中: {text}")

@bot.command(name="leave")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("ボイスチャンネルから切断しました。")
    else:
        await ctx.send("ボイスチャンネルに参加していません。")

# Flaskサーバーを起動してからボットを起動
keep_alive()
bot.run(os.environ["DISCORD_BOT_TOKEN"])
