import os
import asyncio
import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import yt_dlp

# Cargar el token del bot desde el archivo .env
load_dotenv()
TOKEN = os.getenv('discord_token')

# Configurar las intenciones del bot
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Listas para gestionar las canciones en cola
lista_canciones = []
cola_reproduccion = asyncio.Queue()


# Opciones para FFMPEG
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

# Evento de bot listo


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name='Con ! usas los comandos'))
    print('El Bot Está Listo')


# Función para descargar la canción
async def descargar_cancion(url):
    ytdlp_options = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    # Obtener la URL de reproducción usando yt-dlp y descargar la canción
    with yt_dlp.YoutubeDL(ytdlp_options) as ydl:
        info = ydl.extract_info(url, download=True)
        playUrl = info['url']

    return discord.FFmpegPCMAudio(source=playUrl, **FFMPEG_OPTIONS)

# Función para reproducir una canción descargada


async def reproducir_cancion(ctx, source):
    voice_client = ctx.voice_client

    if voice_client and voice_client.is_playing():
        await ctx.send("Canción agregada a la cola de reproducción.")
        await cola_reproduccion.put(source)
    else:
        await ctx.send("Canción en reproducción.")
        lista_canciones.append(source)

        if not voice_client and lista_canciones:
            voice_channel = ctx.author.voice.channel
            voice_client = await voice_channel.connect()
            player = voice_client.play(
                lista_canciones[0],
                after=lambda e: bot.loop.create_task(cancion_terminada(e, ctx))
            )

# Comando para reproducir una canción


@bot.command()
async def play(ctx, url):
    voice_channel = ctx.author.voice.channel

    if not voice_channel:
        await ctx.send("No estás conectado a un canal de voz.")
        return

    try:
        # Descargar la canción
        source = await descargar_cancion(url)

        # Reproducir la canción
        await reproducir_cancion(ctx, source)

    except Exception as e:
        await ctx.send(f"Ocurrió un error al reproducir la canción: {e}")


# Función para manejar la terminación de una canción


async def cancion_terminada(error, ctx):
    if error:
        print(f"Error en la canción: {error}")

    if lista_canciones:
        lista_canciones.pop(0)

    if lista_canciones:
        source = discord.FFmpegPCMAudio(
            lista_canciones[0],
            before_options=FFMPEG_OPTIONS['before_options'],
            options=FFMPEG_OPTIONS['options']
        )
        ctx.voice_client.play(
            source, after=lambda e: bot.loop.create_task(cancion_terminada(e, ctx)))
    elif not lista_canciones and not cola_reproduccion.empty():
        cancion = await cola_reproduccion.get()
        lista_canciones.append(cancion)
        source = discord.FFmpegPCMAudio(
            lista_canciones[0],
            before_options=FFMPEG_OPTIONS['before_options'],
            options=FFMPEG_OPTIONS['options']
        )
        ctx.voice_client.play(
            source, after=lambda e: bot.loop.create_task(cancion_terminada(e, ctx)))
    else:
        await ctx.voice_client.disconnect()


@bot.command()
async def stop(ctx):  # función para parar el bot
    playing_audio = bot.playing_audio  # obtiene el objeto de audio
    if playing_audio:  # si el objeto de audio está activo
        player = playing_audio['player']  # obtiene el objeto de audio
        if player.is_playing():  # si el objeto de audio está activo
            player.pause()  # pausa el objeto de audio


@bot.command()
async def resume(ctx):  # función para reanudar el bot
    playing_audio = bot.playing_audio  # obtiene el objeto de audio
    if playing_audio:  # si el objeto de audio está activo
        player = playing_audio['player']  # obtiene el objeto de audio
        if player.is_paused():  # si el objeto de audio está pausado
            player.resume()  # reanuda el objeto de audio


@bot.command()
async def skip(ctx, amount: int = 1):
    if not ctx.voice_client:  # si no esta conectado a un canal de voz
        # envia el mensaje de error
        return await ctx.send("No estoy conectado a un canal de voz.")

    if not cola_reproduccion:  # si no hay canciones en la cola de reproducción
        # envia un mensaje de error
        return await ctx.send("No hay canciones en la cola de reproducción.")

    else:  # si hay canciones en la cola de reproducción
        ctx.voice_client.stop()  # parar el bot
        for i in range(amount - 1):  # para cada canción en la cola de reproducción
            # obtiene el siguiente elemento de la cola de reproducción y si no hay da una exepcion
            cola_reproduccion.get_nowait()
        await ctx.send(f"Saltando la cancion.")


@bot.command()
async def hola(ctx):
    return await ctx.send("Hola gracias por usar mi bot!!")


@bot.command()
async def ayuda(ctx):
    return await ctx.send('Puedes usar los comandos:!play y la url de una cancion ,!stop frena la cancion,!resume resume la cancion,!skip salta la cancion,!conectar conectar a un canal de voz')

bot.run(TOKEN)
