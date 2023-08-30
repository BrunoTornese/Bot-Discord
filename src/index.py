import os
import asyncio
import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import pytube

# Cargar el token del bot desde el archivo .env
load_dotenv()
TOKEN = os.getenv('discord_token')

# Configuración de las intenciones del bot
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Listas para manejar la cola de reproducción
lista_canciones = []
cola_reproduccion = asyncio.Queue()

# Evento que se ejecuta cuando el bot está listo


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name='Con ! usas los comandos'))
    print('El Bot Está Listo')

# Comando para conectar el bot a un canal de voz


@bot.command(pass_context=True)
async def conectar(ctx):
    canal = ctx.author.voice
    if not canal:
        await ctx.send('Debes estar en un canal de voz')
        return

    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected():
        await voice_client.move_to(canal)
    else:
        voice_client = await canal.connect()

# Comando para reproducir una canción


@bot.command()
async def play(ctx, url):
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        await ctx.send("No estás conectado a un canal de voz.")
        return

    # Obtener información del video de YouTube
    video = pytube.YouTube(url)
    audio = video.streams.filter(only_audio=True).first()
    audio_file = audio.download()

    # Manejo de la cola de reproducción
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.send("Canción agregada a la cola de reproducción.")
        await cola_reproduccion.put(audio_file)
    else:
        await ctx.send("Canción en reproducción.")
        lista_canciones.append(audio_file)
        if not ctx.voice_client and lista_canciones:
            voice_client = await voice_channel.connect()
            source = discord.FFmpegPCMAudio(lista_canciones[0])
            player = voice_client.play(
                source, after=lambda e: bot.loop.create_task(cancion_terminada(e, ctx)))

# Función para manejar la finalización de una canción


async def cancion_terminada(error, ctx):
    if error:
        print(f"Error en la canción: {error}")

    if lista_canciones:
        lista_canciones.pop(0)

    if lista_canciones:
        source = discord.FFmpegPCMAudio(lista_canciones[0])
        ctx.voice_client.play(
            source, after=lambda e: bot.loop.create_task(cancion_terminada(e, ctx)))
    elif not lista_canciones and not cola_reproduccion.empty():
        cancion = await cola_reproduccion.get()
        lista_canciones.append(cancion)
        source = discord.FFmpegPCMAudio(lista_canciones[0])
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
