#Made for cloudbot
#Created by ender.capitalg@gmail.com

import discord
import plugins
import requests

client = plugins.client

import lxml.html
from datetime import datetime, timedelta
import time
import arrow

schedule = []
current_game = ''
epoch = 0

oauth_token = ""

@plugins.command(aliases="agdq sgdq gdq")
async def agdq_(message: discord.Message):
	global oauth_token
	url = "https://api.twitch.tv/kraken/streams/gamesdonequick?oauth_token=" + oauth_token
	obj = requests.get(url).json()
	if obj['stream'] is None:
		await client.say(message, "Stream is OFFLINE.")

	stream = "Twitch Streamer: gamesdonequick" + " -=- Status: Online -=- Game: " + obj['stream']['game'] + " -=- Title: " + obj['stream']['channel']['status'] + " -=- Viewers: " + str(obj['stream']['viewers'])
	await client.say(message, "{} Watch LIVE: <http://www.twitch.tv/gamesdonequick>".format(stream))

def parse_agdq_schedule():
	global schedule, current_game, oauth_token
	obj = requests.get("https://api.twitch.tv/kraken/streams/gamesdonequick?oauth_token=" + oauth_token).json()
	current_game = obj['stream']['game']

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
#		runners = element.getchilden()[2].text
#		gs.append([gtime, game, runners])
		gs.append([gtime, game])

	schedule = gs
	print("Updating AGDQ schedule. ")

@plugins.command(name="upnext", aliases="schedule sched")
async def sched(message: discord.Message):
	global oauth_token
	global schedule, current_game, epoch
	#update game for comparison later
	obj = requests.get("https://api.twitch.tv/kraken/streams/gamesdonequick?oauth_token=" + oauth_token).json()
	try:
		current_game = obj['stream']['game']
	except TypeError as e:
		await client.say(message, "Stream offline.")

	#used to reparse the schedule in case of game overruns/short runs (15min)
	curtime = arrow.utcnow()
	if epoch is 0:
		#force update
		timediff = 900
	else:
		timediff = (curtime - epoch).seconds
	if not schedule or timediff > 900:
		parse_agdq_schedule()
		epoch = curtime

	current = None
	game = schedule[0][1]
	for i, (tm, gm) in enumerate(schedule[1:]):
		if current_game is gm:
			current = gm
			game = schedule[i+2][1]
			await client.say(message, 'GDQ Currently Playing: {} | Up Next: {}'.format(current, game))
		game = gm

	#game didn't match, find game via time
	now = arrow.utcnow()
	for i, (tm, gm) in enumerate(schedule[1:]):
		if tm > now:
			current = schedule[i][1]
			game = gm
			await client.say(message, 'GDQ Currently Playing: {} | Up Next: {}'.format(current, game))
			break

@plugins.command(name="donations")
async def agdq_donation(message: discord.Message):
	h_t = requests.get("https://gamesdonequick.com/tracker/22").text
	html = lxml.html.fromstring(h_t)
	donation = html.xpath("//small")
	await client.say(message, "```c\nGames Done Quick" + donation[0].text.replace('\n', ' ').replace('\r', ' ').replace('\u2014', '-') + "```")
