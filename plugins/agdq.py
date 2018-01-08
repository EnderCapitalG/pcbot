import discord
import plugins
import requests

client = plugins.client

import lxml.html
import arrow
import pickle
import asyncio

schedule = []
mesObj = []

oauth_token = ""

@plugins.command(name="gdq", aliases="agdq sgdq")
async def agdq(message: discord.Message):
	global oauth_token
	url = "https://api.twitch.tv/kraken/streams/gamesdonequick?oauth_token=" + oauth_token
	obj = requests.get(url).json()
	if obj['stream'] is None:
		await client.say(message, "Stream is OFFLINE.")
		return

	stream = "Twitch Streamer: gamesdonequick" + " -=- Status: Online -=- Game: " + obj['stream']['game'] + " -=- Title: " + obj['stream']['channel']['status'] + " -=- Viewers: " + str(obj['stream']['viewers'])
	await client.say(message, "{} Watch LIVE: <http://www.twitch.tv/gamesdonequick>".format(stream))

async def parse_gdq_schedule():
	global schedule, oauth_token

	h_t = requests.get("https://gamesdonequick.com/schedule").text
	html = lxml.html.fromstring(h_t)
	table = html.xpath("//table[@id='runTable']//tbody//tr[not(contains(@class, 'second-row'))]")
	table = table

	gs = []
	for element in table:
		try:
			gtime = arrow.get(element.getchildren()[0].text)
		except arrow.parser.ParserError:
			continue
		game = element.getchildren()[1].text
		runners = element.getchildren()[2].text
		gs.append([gtime, game, runners])

	schedule = gs

@plugins.command(name="upnext", aliases="schedule sched")
async def sched(message: discord.Message):
	global schedule

	now = arrow.utcnow()
	for i, (tm, gm, ru) in enumerate(schedule[1:]):
		if tm > now:
			current = schedule[i][1]
			runner = schedule[i][2]
			nextgame = gm
			nextrunner = ru
			await client.say(message, "```c\nGDQ Currently Playing: '{}' Ran By: {} || Up Next: '{}' Ran By: {}```".format(current, runner, nextgame, nextrunner))
			break

async def automated_gdq():
	global schedule, mesObj

	now = arrow.utcnow()
	for i, (tm, gm, ru) in enumerate(schedule[1:]):
		if (tm - now).seconds < 300 and (tm - now).days is 0:
			time = tm.to('US/Eastern')
			mes = "```c\nGDQ Up Next: '" + gm + "' Ran By: '" + ru + "' Starting Tentatively: '" + time.format('YYYY-MM-DD HH:mm:ss') + "'```"
			for item in mesObj:
				await client.say(item, mes)

@plugins.command(name="setgdqchan", owner="true")
async def setgdqchan(message: discord.Message):
	global mesObj
	mesObj.append(message)
	ofile = "data/gdq.wf"
	with open(ofile, 'wb') as output:
		pickle.dump(mesObj, output, pickle.HIGHEST_PROTOCOL)

	output.close()
	await client.say(message, "Channel set.")

@plugins.command(name="nogdq", owner="true")
async def unsetgdq(message: discord.Message):
	global mesObj
	i = 0
	for item in mesObj:
		if message.channel == item.channel and message.server == item.server:
			print("Deleted `" + str(message.channel) + " " + str(message.server) + "` from receiving alerts.")
			await client.say(message, "Deleted `" + str(message.channel) + "` from receiving alerts.")
			del mesObj[i]
		i += 1
	ofile = "data/gdq.wf"
	with open(ofile, 'wb') as output:
		pickle.dump(mesObj, output, pickle.HIGHEST_PROTOCOL)

	output.close()


@plugins.command(name="donations")
async def agdq_donation(message: discord.Message):
	h_t = requests.get("https://gamesdonequick.com/tracker/22").text
	html = lxml.html.fromstring(h_t)
	donation = html.xpath("//small")
	await client.say(message, "```c\nGames Done Quick" + donation[0].text.replace('\n', ' ').replace('\r', ' ').replace('\u2014', '-') + "```")

async def mainloop():
	while(1):
		await parse_gdq_schedule()
		await automated_gdq()
		await asyncio.sleep(300)

def start():
	global mesObj
	inputFile = "data/gdq.wf"

	try:
		with open(inputFile, 'rb') as input:
			mesObj.append(pickle.load(input))
			mesObj = mesObj[0]
		input.close()
	except FileNotFoundError:
		pass

	asyncio.ensure_future(mainloop())

start()
