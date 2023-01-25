import os
import time
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pushbullet import Pushbullet
from phue import Bridge

load_dotenv()  # Ladataan ympäristömuuttujat

ip = discover_ip()  # Haetaan oman Hue Bridgen IP
b = Bridge(ip)  # Luodaan objekti Hue Bridgelle
b.get_api()  # Luodaan yhteys Hue Bridgeen
# Luodaan Pushbullet-objekti API-avaimella
pb = Pushbullet(os.getenv('PUSHBULLET_API_KEY'))
# Lisätään kaikki oikeudet, myös oikeus lukea viestit
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_message(message):  # Suoritetaan koodi aina kun uusi viesti lähetetään
    channel = message.channel  # Haetaan tieto mille kanavalle viesti lähetettiin
    for mention in message.mentions:  # Käydään läpi kaikki maininnat viesteissä
        if mention.name == "[Discord-käyttäjätunnuksesi]":  # Jos mainitaan käyttäjä
            # Lähetetään viesti samalle kanavalle
            await channel.send('Käyttäjä mainittu')
            # Lähetetään ilmoitus
            pb.push_note('Ilmoituksen otsikko', 'Ilmoituksen sisältö')
            b.set_light(14, 'on', True)  # Sytytetään valo #14
    await bot.process_commands(message)  # Ilman tätä botin komennot ei toimi


@bot.command()
async def pelataanko(ctx):  # Luodaan komento !pelataanko
    # Lähetetään viesti samalle kanavalle
    await ctx.send('Pelikutsu lähetetty')
    # Lähetetään ilmoitus
    pb.push_note('Ilmoituksen otsikko', 'Ilmoituksen sisältö')
    b.set_light(14, 'on', True)  # Sytytetään valo #14


@bot.command()
async def tulossa(ctx):  # Luodaan komento !tulossa
    await ctx.send('Käyttäjä tulossa')  # Lähetetään viesti kanavalle
    b.set_light(14, 'on', False)  # Sammutetaan valo #14

# Käynnistetään botti halutulla tokenilla
bot.run(os.getenv('ILMOITUSBOTTI_TOKEN'))


def discover_ip():  # Haetaan Hue Bridgen IP lähiverkossa
    # Haetaan sivuston discovery.meethue.com sisältö
    response = requests.get('https://discovery.meethue.com')
    if response and response.status_code == 200:  # Varmistetaan että sivusto vastasi
        data = response.json()  # Haetaan sivuston JSON-sisältö
        # Etsitään JSON-sisällöstä internalipaddress -avain
        if 'internalipaddress' in data[0]:
            # Palautetaan JSON-sisällöstä internalipaddress -arvo
            return data[0]['internalipaddress']
    return None  # Palautetaan None, jos sivusto ei vastaa
