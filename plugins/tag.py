import sqlite3

import discord
import plugins
from pcbot import Annotate

client = plugins.client

tagdb = "data/Tag.db"

#for regex triggers
def syncDB():
	global tagdb
	db = sqlite3.connect(tagdb)
	cur = db.cursor()
	query = "SELECT * FROM tags;"
	cur.execute(query)
	table = cur.fetchall()

	db.close()
	global tagName
	tagName = table
	return table

tagName = syncDB()

def addtoDB(text):
	global tagdb
	db = sqlite3.connect(tagdb)
	cur = db.cursor()
	Name = text.split(' ', 1)[0]
	Tag = text.split(' ', 1)[1]
	Name = Name.replace('"', r'\"')
	Tag = Tag.replace('"', r'\"')
	#make sure it's not tagged
	query = "SELECT tags FROM tags WHERE name IS ? COLLATE NOCASE;"
	cur.execute(query, (Name,))
	table = cur.fetchall()
	for item in table:
		if Tag in item[0]:
			return 1

	query = "INSERT INTO tags VALUES (?, ?);"
	cur.execute(query, (Name, Tag))
	db.commit()
	db.close()
	syncDB()
	print("Added to tag %s: %s" % (Name, Tag))
	return 0

def delfromDB(name, text):
	global tagdb
	db = sqlite3.connect(tagdb)
	cur = db.cursor()
	name.replace('"', '\"')
	text.replace('"', '\"')
	query = "SELECT tags FROM tags WHERE name IS ? COLLATE NOCASE;"
	cur.execute(query, (name,))
	table = cur.fetchall()

	for item in table:
		if text in item[0]:
			query = "DELETE FROM tags WHERE name IS ? AND tags IS ?;"
			cur.execute(query, (name, text))
			db.commit()

	db.close()
	syncDB()
	print("Deleting from tag %s: %s" % (name, text))
	return 0

def getfromDB(text):
	global tagdb
	db = sqlite3.connect(tagdb)
	cur = db.cursor()
	text.replace('"', '\"')
	query = "SELECT tags FROM tags WHERE name IS ? COLLATE NOCASE;"
	cur.execute(query, (text,))
	table = cur.fetchall()
	retv = ""
	i = 0
	for item in table:
		retv += item[0]
		if i + 1 is not len(table):
			retv += ", "
		i += 1

	db.close()
	if retv is "" or retv is None:
		return 1
	return retv

@plugins.command(name="tag")
async def setTag(message: discord.Message, text: Annotate.CleanContent):
	if addtoDB(text) is 0:
		await client.say(message, "Tag added.")
		return
	await client.say(message, "Tag already exists.")

@plugins.command(name="tags")
async def getTag(message: discord.Message, text: Annotate.CleanContent):
	retv = getfromDB(text)
	if retv is 1:
		temp = "No tags found for: " + text
	else:
		temp = "Tags for " + text + ": " + retv
	await client.say(message, temp)

#this is for searching by TAG, not keyword
@plugins.command(name="tagged")
async def getTagged(message: discord.Message, text: Annotate.CleanContent):
	global tagName
	retv = ""
	listv = []
	i = 0
	for item in tagName:
		if text.lower() == item[1].lower():
			listv.append(item[0])
	for item in listv:
		retv += item
		if i + 1 is not len(listv):
			retv += ", "
		i += 1
	if retv is "":
		return
	await client.say(message, "Tagged " + text + ": " + retv)

@plugins.command(name="untag")
async def remTag(message: discord.Message, text: Annotate.CleanContent):
	result = delfromDB(text.split(' ',1)[0], text.split(' ',1)[1])
	if result is 0:
		await client.say(message, "Tag removed.")
		return
	await client.say(message, "Tag doesn't exist.")

@plugins.event()
async def on_message(message: discord.Message):
	if not message.content.startswith("?"):
		return
	tag = message.content.split('?',1)[-1]
	if tag is None:
		return
	retv = getfromDB(tag)
	if retv is 1:
#		return "No tags found for: " + tag
		#silently fail instead
		return
	temp = "Tags for " + tag + ": " + retv
	await client.say(message, temp)

def dropTagDB():
	global tagdb
	db = sqlite3.connect(tagdb)
	cur = db.cursor()
	query = "DROP TABLE IF EXISTS tags"
	cur.execute(query)
	db.commit()

	query = "CREATE TABLE tags(name TEXT, tags TEXT);"
	cur.execute(query)
	db.commit()
	db.close()
	return "Table dropped."
