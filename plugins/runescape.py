import discord
import plugins
client = plugins.client

import requests
import re

@plugins.command(name="runescape", aliases="rune rs")
async def runescape(message: discord.Message):
	url_us = requests.get("http://www.runescape.com/player_count.js?varname=iPlayerCount&callback=jQuery000000000000000_0000000000&_=0")
	s = "u'" + url_us.text + "'"
	online = re.search('\((.*?)\)', s).group(1)
	await client.say(message, "Runescape players online: " + online)
