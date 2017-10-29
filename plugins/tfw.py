import plugins
import discord
from pcbot import Annotate, utils
client = plugins.client

import sqlite3

tfwdb = "data/tfw.db"

#@hook.regex(r'(?i)tfw(.*)')
#def tfwadd(match, nick, host):
@plugins.event()
async def on_message(message: discord.Message):
	if not message.content.startswith("tfw"):
		return
	author = message.author.mention
	if '@333360572974497794' in str(author):
		return
	global tfwdb
	db = sqlite3.connect(tfwdb)
	cur = db.cursor()
	query = "CREATE TABLE IF NOT EXISTS tfw (text TEXT);"
	cur.execute(query)
	query = "INSERT INTO tfw VALUES(?);"
	print("Adding tfw:", message.content)
	cur.execute(query, (message.clean_content,))
	db.commit()
	db.close()

#@hook.command('tfw')
@plugins.command(name="tfw")
async def tfwgrab(message: discord.Message):
	global tfwdb
	db = sqlite3.connect(tfwdb)
	cur = db.cursor()
	query = "SELECT * FROM tfw ORDER BY RANDOM() LIMIT 1;"
	cur.execute(query)
	ret = cur.fetchone()[0]
	db.close()
	await client.say(message, ret)

#@hook.command('deltfw', permissions=["botcontrol"])
@plugins.command(name="deltfw", owner="True")
async def deletetfw(message: discord.Message, text: Annotate.CleanContent):
	global tfwdb
	db = sqlite3.connect(tfwdb)
	cur = db.cursor()
	query = "DELETE FROM tfw WHERE text IS ?;"
	cur.execute(query, (text,))
	db.commit()
	db.close()
	await client.say(message, "Removed.")

#@hook.command('counttfw', permissions=["botcontrol"])
@plugins.command(name="counttfw", owner="True")
async def counttfw(message: discord.Message):
	global tfwdb
	db = sqlite3.connect(tfwdb)
	cur = db.cursor()
	query = "SELECT * FROM tfw;"
	cur.execute(query)
	x = 0
	obj = cur.fetchall()
	for item in obj:
		x += 1
	db.close()
	await client.say(message, x)
