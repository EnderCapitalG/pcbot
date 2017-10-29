#Made for cloudbot
#Created by ender.capitalg@gmail.com

import discord
import plugins
import requests
import arrow

client = plugins.client

@plugins.command(name="tq", aliases="eve tranquility")
async def tqstatus(message: discord.Message):
	url_tq = "https://crest-tq.eveonline.com/"
	json = requests.get(url_tq).json()
	if json is None:
		return "Tranquility server status: Offline."

	status = json["serviceStatus"]
	if "online" in status:
		players = json["userCount_str"]
		await client.say(message, "Tranquility server status: Online. Players online: " + players)
		return
	
	await client.say(message, "Tranqulity server status: Offline.")

@plugins.command(name="sisi")
async def sisistatus(message: discord.Message):
	url_tq = "http://crest-sisi.testeveonline.com/"
	json = requests.get(url_tq).json()
	if json is None:
		await client.say(message, "Singularity server status: Offline.")
		return

	status = json["serviceStatus"]["eve"]
	if "online" in status:
		players = json["userCounts"]["eve_str"]
		await client.say(message, "Singularity server status: Online. Players online: " + players)
		return
	
	await client.say(message, "Singularity server status: Offline.")


@plugins.command(name="evetime")
async def evetime(message: discord.Message):
        now = arrow.utcnow()
        await client.say(message, "Current Eve time: " + now.format("HH:mm:ss"))

