import gvars
gvars.init()

from discord import Activity
from discord import ActivityType
from discord import Embed
from discord import FFmpegPCMAudio
from discord import errors
from discord import Guild
from discord import User
from discord import TextChannel
from discord import ClientException
from Key import *
from bs4 import BeautifulSoup
from random import choice
from math import ceil
from mutagen.mp3 import MP3
from glob import glob
from Currency import Currency
from Logging import *

import dbl

import string
import asyncio
import traceback
import os
import datetime
import urllib3
urllib3.disable_warnings()


client = gvars.client

token = DBLKey
dblpy = dbl.Client(client, token)

audio_dir = os.path.dirname(os.path.realpath(__file__)) + "/audio_files/"
audio_files = glob(audio_dir + "*.mp3")

juul = 15.99/4
updateTime = 3600

def botPrint(s, process=False):
	if (not process):
		print("[" + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] " + str(s))
	else:
		print("[" + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] " + str(s), end="")

def updateCurrencyConversions():
	pool = urllib3.PoolManager()
	Content = pool.request('GET', 'https://www.x-rates.com/table/?from=USD&amount=1')
	soup = BeautifulSoup(Content.data, 'html.parser')

	currenciesElements = soup.find_all('td', {'class': 'rtRates'})

	currenciesElements = currenciesElements[:20]
	for k, v in enumerate(currenciesElements):
		if (k % 2 != 0 or k != 0):
			del currenciesElements[k]

	if (gvars.currencyPrices == []):
		for k, v in enumerate(currenciesElements):
			gvars.currencyPrices.append(float(v.contents[0].decode_contents()) * juul)
	else:
		for k, v in enumerate(currenciesElements):
			gvars.currencyPrices[k] = float(v.contents[0].decode_contents()) * juul
	
@client.event
async def timerTask(time):
	await asyncio.sleep(time)
	updateCurrencyConversions()
	currencyTimer = asyncio.ensure_future(timerTask(updateTime))

@client.event
async def update_stats():
	while not client.is_closed():
		try:
			await dblpy.post_guild_count()
		except Exception as e:
			ErrorHandler(None, exception=e)
		await asyncio.sleep(1800)

@client.event
async def on_ready():
	botPrint('------')
	botPrint('Logged in as')
	botPrint(client.user.name)
	botPrint(client.user.id)
	botPrint('------')

	print("")
	initLogs()
	print("")

	await client.change_presence(activity=Activity(type=ActivityType.watching, name="!jp help"))

	client.loop.create_task(update_stats())

	currencyTimer = asyncio.ensure_future(timerTask(updateTime))
	updateCurrencyConversions()

	Currency("Euros", ["euro", "€"])
	Currency("British Pounds", ["pound", "£"])
	Currency("Indian Rupees", ["rupee", "₹"])
	Currency("Australian Dollars", "aud")
	Currency("Canadian Dollars", "cad")
	Currency("Singapore Dollars", "sgd")
	Currency("Swiss Francs", ["franc", "fr."])
	Currency("Malaysian Ringgits", ["ringgit", "rm", "myr"])
	Currency("Japanese Yen", ["yen", "yen", "¥"])
	Currency("Chinese Yuan", ["yuan", "cny", "元"])
	Currency("US Dollars", ["dollar", "usd", "$"], 3.99)
	Currency("Riot Points", ["riot points", "rp"], 518.7)
	Currency("V-Bucks", ["v bucks", "v-bucks"], 399)
	Currency("Robux", ["robux", "rbx"], 322.4)
	Currency("Big Macs", "big mac", 3.99)
	Currency("Chicken McNuggets", ["nugget", "mcnuggets", "nuggies"], 8.886)

@client.event
async def on_message(message):
	try:
		if (not message.author.bot):
			if (message.content.lower().startswith("!juulpod rip") or message.content.lower().startswith("!jp rip") and type(message.channel) == TextChannel):
				logWrite(message.guild, "COMMAND CALLED \"rip\" BY USER: " + str(message.author) + "(" + str(message.author.id) + ") IN TEXT CHANNEL: " + message.channel.name + "(" + str(message.channel.id) + ")")
				if (message.author.voice):
					try:
						if (message.author.voice.channel.permissions_for(message.guild.me).connect):
							vc = await message.author.voice.channel.connect()
							logWrite(message.guild, "\tJoined VoiceChannel: " + message.author.voice.channel.name + "(" + str(message.author.voice.channel.id) + ")")
						else:
							raise Exception("Don't have permission to join channel")
					except Exception as e:
						logWrite(message.guild, "\tAttempted to join VoiceChannel: " + message.author.voice.channel.name + "(" + str(message.author.voice.channel.id) + ") but failed because: " + str(e))
						if (type(e) == ClientException):
							await message.channel.send(message.author.mention + " I'm busy rippin' rn...")
						else:
							await message.channel.send(message.author.mention + " Bruh I don't have permissions to join...")
						return
					
					await message.delete()

					audio_file = choice(audio_files)
					try:
						vc.play(FFmpegPCMAudio(audio_file))
					except:
						vc.play(FFmpegPCMAudio(executable="C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe", source=audio_file))
					
					logWrite(message.guild, "\tPlaying audio file: " + audio_file.replace("\\", "/"))
					await asyncio.sleep(ceil(MP3(audio_file).info.length))

					vc.stop()
					await vc.disconnect()
					logWrite(message.guild, "\tDisconnected from VoiceChannel")
				else:
					await message.channel.send(message.author.mention + " You aren't currently in a voice channel bro.")
					logWrite(message.guild, "\tUser is not connected to a VoiceChannel")

				return

			if (message.content.lower().startswith("!juulpod help") or message.content.lower().startswith("!jp help")):
				logWrite(message.guild, "COMMAND CALLED \"help\" BY USER: " + str(message.author) + "(" + str(message.author.id) + ") IN TEXT CHANNEL: " + ["DM", str(message.channel)][hasattr(message.channel, 'name')] + "(" + str(message.channel.id) + ")")
				
				desc = "This bot was created in the hopes to normalize all world wide currencies into one essential value. The Cucumber Juul Pod has been a staple of modern day society, and thus it should be the basis for all world wide economies. This bot converts most prominent currencies found around the world into JP (Juul Pods). Below is a list of the supported currencies that can be converted into JP and their recognizable namespaces. -Nullvalue#8123"

				emb = Embed(title="Juul Pod Help", color=0x8ACC8A, description=desc)
				currencyText = ""
				namespaceText = ""
				for cur in gvars.currencies:
					currencyText += cur.name + "\n"
					if (type(cur.nameSpaces) is str):
						namespaceText += "(\'" + cur.nameSpaces + "\')\n"
					elif (type(cur.nameSpaces) is list):
						namespaceText += "("
						for nameSpace in cur.nameSpaces:
							if (nameSpace != cur.nameSpaces[len(cur.nameSpaces) - 1]):
								namespaceText += "\'" + nameSpace + "\', "
							else:
								namespaceText += "\'" + nameSpace + "\')\n"

				emb.add_field(name="Commands", value="`!jp rip`\n`!jp convert (namespace)`\n", inline=False)
				emb.add_field(name="Currencies", value=currencyText, inline=True)
				emb.add_field(name="Name Spaces", value=namespaceText, inline=True)
				await message.channel.send(embed=emb)
				logWrite(message.guild, "\tSent help message for user: " + str(message.author) + "(" + str(message.author.id) + ") in TextChannel: " + ["DM", str(message.channel)][hasattr(message.channel, 'name')] + "(" + str(message.channel.id) + ")")
				return

			if (message.content.lower().startswith("!juulpod convert") or message.content.lower().startswith("!jp convert")):
				logWrite(message.guild, "COMMAND CALLED \"convert\" BY USER: " + str(message.author) + "(" + str(message.author.id) + ") IN TEXT CHANNEL: " + ["DM", str(message.channel)][hasattr(message.channel, 'name')] + "(" + str(message.channel.id) + ")")
				for currency in gvars.currencies:
					if (currency.parseMessage(message)):
						logWrite(message.guild, "\tMatched currency: " + currency.name)
						if (any(char.isdigit() for char in message.content)):
							await currency.sendConverstion(message)
							logWrite(message.guild, "\tSent conversion")
						else:
							logWrite(message.guild, "\tNo number given in message.")
							await message.channel.send(message.author.mention + " You did not include a numberto convert!")
							logWrite(message.guild, "\tSent message indicating no digits in string.")
						return

				await message.channel.send(message.author.mention + " Unknown currency, `!jp help` for a list of supported currencies.")
				logWrite(message.guild, "\tNo currency recognized in message: \"" + message.content + "\"")
				return
	except Exception as e:
		if (message.guild):
			ErrorHandler(location=message.guild, member=message.author, exception=e)
		else:
			ErrorHandler(location=message.author, exception=e)

		raise

client.run(Key)