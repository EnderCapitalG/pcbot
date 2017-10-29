import discord
import plugins
client = plugins.client

import requests
import lxml.html
import pickle
import arrow
import time
import asyncio

#holy crap stop spamming me
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
header = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36' }

title = alert_type = desc = starttime = endtime = faction = lastUpdate = 0
mesObj = []
alert_types = ['Kavat', 'Catalyst', "Reactor", 'Vauban', 'Lotus', 'Forma', 'Nitain', 'Corrosive', 'Syphon']

def check_alert(check):
	global alert_types
	for item in alert_types:
		if item in check:
			return True
	return False

async def get_data():
	global title, alert_type, desc, starttime, endtime, faction, lastUpdate
	global header

	req = requests.get("http://content.warframe.com/dynamic/rss.php", headers=header)
	html = lxml.html.fromstring(req.content)

	title = html.xpath("//item/title/text()")
	alert_type = html.xpath("//item/author/text()")
	desc = html.xpath("//item/description/text()")
	starttime = html.xpath("//item/pubdate/text()")
	endtime = html.xpath("//item/*[local-name()='expiry']/text()")
	faction = html.xpath("//item/*[local-name()='faction']/text()")


@plugins.command(name="setwfchan", owner="true")
async def setwfchan(message: discord.Message):
	global mesObj
	mesObj.append(message)
	ofile = "data/test.wf"
	with open(ofile, 'wb') as output:
		pickle.dump(mesObj, output, pickle.HIGHEST_PROTOCOL)

	output.close()
	await client.say(message, "Channel set.")

@plugins.command(name="givewfalerts")
async def wfpmalerts(message: discord.Message):
	global mesObj
	if "Direct Message" not in str(message.channel):
		await client.say(message, "givewfalerts must be used in a private message")
		return

	#iterate for duplicates
	for item in mesObj:
		if message.channel ==  item.channel:
			await client.say(message, "You are already recieving pms.")
			return
	mesObj.append(message)
	ofile = "data/test.wf"
	with open(ofile, 'wb') as output:
		pickle.dump(mesObj, output, pickle.HIGHEST_PROTOCOL)

	output.close()
	await client.say(message, "You will recieve pms.")

@plugins.command(name="noalerts")
async def noalerts(message: discord.Message):
	global mesObj
	i = 0
	for item in mesObj:
		if message.channel == item.channel and message.server == item.server:
			print("Deleted `" + str(message.channel) + " " + str(message.server) + "` from receiving alerts.")
			await client.say(message, "Deleted `" + str(message.channel) + "` from receiving alerts.")
			del mesObj[i]
		i += 1
	ofile = "data/test.wf"
	with open(ofile, 'wb') as output:
		pickle.dump(mesObj, output, pickle.HIGHEST_PROTOCOL)

	output.close()

@plugins.command(name="wfchannels", owner="true")
async def wfchanlist(message: discord.Message):
	global mesObj
	for item in mesObj:
		mes = "`Server: " + str(item.server) + " -- Channel: " + str(item.channel) + "`"
		await client.say(message, mes)

@plugins.command(name="alerts")
async def WFAlerts(message: discord.Message):
	global mesObj, title, alert_type, desc, starttime, endtime, faction
	it = -1
	for item in endtime:
		it += 1
		start = arrow.get(starttime[it], 'ddd, DD MMM YYYY HH:mm:ss ZZ')
		end = arrow.get(endtime[it], 'ddd, DD MMM YYYY HH:mm:ss ZZ')
		start = start.to('US/Eastern')
		end = end.to('US/Eastern')

		efaction = faction[it][3:]
		mes = "```c\n" + efaction + " " + alert_type[it] + ": `" + title[it] + "` " + desc[it] + " `Starting at: " + start.format('YYYY-MM-DD HH:mm:ss') + " Eastern - Ending at: " + end.format('YYYY-MM-DD HH:mm:ss') + " Eastern```"
		await client.say(message, mes)

async def Message_Channel():
	global mesObj, title, alert_type, desc, starttime, endtime, faction, alert_types
	it = -1
	now = arrow.utcnow()
	if not endtime:
		return
	for item in endtime:
		it += 1
		start = arrow.get(starttime[it], 'ddd, DD MMM YYYY HH:mm:ss Z')
		end = arrow.get(endtime[it], 'ddd, DD MMM YYYY HH:mm:ss Z')
		start = start.to('US/Eastern')
		end = end.to('US/Eastern')
		efaction = faction[it][3:]
	#	if 'Nitain' in title[it] or 'Catalyst' in title[it] or 'Reactor' in title[it] or 'Kavat' in title[it] or 'Lotus' in title[it] or 'Vauban' in title[it]:
		if check_alert(title[it]):
			if (now - start).seconds < 60:
				mes = "```c\nNew " + efaction + " " + alert_type[it] + ": `" + title[it] + "` " + desc[it] + " `Starting at: " + start.format('YYYY-MM-DD HH:mm:ss') + " Eastern - Ending at: " + end.format('YYYY-MM-DD HH:mm:ss') + " Eastern```"
				for item in mesObj:
					await client.say(item, mes)

async def mainloop():
	while(1):
		await get_data()
		await Message_Channel()
		await asyncio.sleep(60)

def start():
	global mesObj
	ifile = "data/test.wf"

	try:
		with open(ifile, 'rb') as input:
			mesObj.append(pickle.load(input))
			mesObj = mesObj[0]
	except FileNotFoundError:
		return
	input.close()
	asyncio.ensure_future(mainloop())

start()
