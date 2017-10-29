#Made for cloudbot
#Created by ender.capitalg@gmail.com
import discord
import plugins

client = plugins.client

import requests

def get_bitcoin():
	data = requests.get("https://www.bitstamp.net/api/ticker/").json()
	t = {
		'low':  float(data['low']),
		'high': float(data['high']),
		'last':  float(data['last']),
	}
	return t

@plugins.command(name="bitcoin", aliases="btc bit butt buttcoin")
async def bitcoin(message: discord.Message):
	t = get_bitcoin()
	msg = "```js\n"
	msg += "Bitcoin - Current: " + str(t['last']) + " - 24h High: " + str(t['high']) + " - 24h Low: " + str(t['low']) + "\n```"
	await client.say(message, msg)

def get_litecoin():
	data = requests.get("https://btc-e.com/api/2/ltc_usd/ticker").json()
	l = {
		'low': float(data['ticker']['low']),
		'high': float(data['ticker']['high']),
		'last': float(data['ticker']['last']),
	}
	return l

#@plugins.command(name="litecoin", aliases="ltc lite")
async def litecoin(message: discord.Message):
	l = get_litecoin()
	msg = "Litecoin - Current: " + str(l['last']) + " - 24h High: " + str(l['high']) + " - 24h Low: " + str(l['low'])
	await client.say(message, msg)

