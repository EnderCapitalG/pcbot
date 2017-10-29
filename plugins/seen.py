#keeps track of last message of a user to see when they last spoke
#use server + id to track their info, so it's server independent

import plugins
import discord
import plugins
client = plugins.client

import sqlite3
import arrow

seendb = "data/Seen.db"

def makedb():
	global seendb
	db = sqlite3.connect(seendb)
	cur = db.cursor()
	query = "CREATE TABLE IF NOT EXISTS seen (user TEXT PRIMARY KEY, server TEXT, time TEXT, message TEXT);"
	cur.execute(query)
	db.commit()
	db.close()

makedb()


@plugins.event()
async def on_message(message: discord.Message):
	text = message.clean_content
	user = message.author.mention
	time = arrow.utcnow()
	server = message.server

	global seendb
	db = sqlite3.connect(seendb)
	cur = db.cursor()
	cur.execute("INSERT OR REPLACE INTO seen VALUES(?, ?, ?, ?)", (user, str(server), str(time), text))
	db.commit()
	db.close()

@plugins.command(name="seen")
async def Seen(message: discord.Message):
	text = message.content.split(' ', 1)[-1]
	global seendb
	db = sqlite3.connect(seendb)
	cur = db.cursor()
	cur.execute("SELECT * FROM seen WHERE user IS ?", (text,))
	array = cur.fetchall()
	try:
		print(array[0][0], array[0][1], array[0][2], array[0][3])
	except IndexError:
		return

	arrowobj = arrow.get(array[0][2])
	arrowobj = arrowobj.format('YYYY-MM-DD HH:mm:ss')

	#multiline
	#await client.say(message, array[0][0] + " was last seen on server ```" + array[0][1] + "``` at " + arrowobj + "UTC saying: ```" + array[0][3] + "```")
	#single line
	await client.say(message, array[0][0] + " was last seen on server `" + array[0][1] + "` at `" + arrowobj + " UTC` saying: `" + array[0][3] + "`")

	db.close()
	
