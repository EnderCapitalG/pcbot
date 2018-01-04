#new hotness

import discord
import plugins
from pcbot import utils
client = plugins.client

import emoji
import os
from random import shuffle
from PIL import Image, ImageDraw, ImageFont
import base64
import requests
import json
from datetime import datetime
from io import BytesIO
import random

mcache = dict()

font_file = "fonts/ComicBD.ttf"
emoji_font_file = "fonts/Symbola_hint.ttf"
font_size = 14
buffer_size = 30

@plugins.event()
async def on_message(message: discord.Message):
	if str(message.clean_content).startswith(".") is False and str(message.clean_content).startswith("!") is False:
		key = (message.channel, message.server)
		if key not in mcache:
			mcache[key] = []
	
		value = (datetime.now(), message.author.mention, str(message.clean_content))
		mcache[key].append(value)
		mcache[key] = mcache[key][-1*buffer_size:]

@plugins.command(name="comic")
async def comic(message: discord.Message):
	try:
		messages = mcache[(message.channel, message.server)]
	except KeyError:
		return "Not enough messages."
	stackpointer = 0
	nicks = set()

	#makes sure the first sentence is added
	nicks.add(messages[0][1])

	for msg in range(len(messages)-1, 0, -1):
		stackpointer += 1
		previous = messages[msg][0] - messages[msg-1][0]
		nicks.add(messages[msg][1])
		if stackpointer > 10 or previous.total_seconds() > 1800 or len(nicks) > 8:
			break

	#fixes first line disappearing when it shouldn't
	if stackpointer is not 0:
		stackpointer += 1
	messages = messages[-1*stackpointer:]

	#make sure that isn't a message that isn't in nicks (bugfix)
	for msg in messages:
		if msg[1] not in nicks:
			messages.remove(msg)

	panels = []
	panel = []
	
	for (time, nick, messagel) in messages:
		if len(panel) == 2 or len(panel) == 1 and panel[0][0] == nick:
			panels.append(panel)
			panel = []
		if messagel.count('\x01') >= 2:
			ctcp = messagel.split('\x01', 2)[1].split(' ', 1)
			if len(ctcp) == 1:
				ctcp += ['']
			if ctcp[0] == 'ACTION':
				message = '*' + ctcp[1] + '*'

		panel.append((nick, messagel))

	panels.append(panel)
	#debug info
	print(repr(nicks))
	print(repr(panels))


	image_comic = make_comic(nicks, panels)

	image_comic = utils.convert_image_object(image_comic)
	await client.send_file(message.channel, image_comic, filename="comic.png")

def wrap(string, font, draw, panelwidth):
	string = string.split()
	messageWidth = 0
	messageHeight = 0
	temp = []

	while len(string) > 0:
		#track iterator position
		char = 1
		while True and char < len(string):
			width, height = draw.textsize(" ".join(string[:char]), font=font)
			if width > panelwidth:
				char -= 1
				break
			else:
				char += 1

		#case where current line is wider than the screen
		if char == 0 and len(string) > 0:
			char = 1

		width, height = draw.textsize(" ".join(string[:char]), font=font)
		messageWidth = max(messageWidth, width)
		messageHeight += height
		temp.append(" ".join(string[:char]))
		string = string[char:]

	return temp, (messageWidth, messageHeight)

def char_is_emoji(character):
	return character in emoji.UNICODE_EMOJI

def rendertext(string, font, draw, position):
	global font_file, emoji_font_file, font_size
	normal_font = ImageFont.truetype(font_file, font_size)
	emoji_font = ImageFont.truetype(emoji_font_file, 20)
	charHeight = position[1]
	for char in string:
		if char_is_emoji(char):
			font = emoji_font
		else:
			font = normal_font
		width, height = draw.textsize(char, font=font)

		#test dropshadows
		shadowcolor = (0x00, 0x00, 0x00, 0xff)

		draw.text((position[0]-1, charHeight-1), char, font=font, fill=shadowcolor)
		draw.text((position[0]+1, charHeight-1), char, font=font, fill=shadowcolor)
		draw.text((position[0]-1, charHeight+1), char, font=font, fill=shadowcolor)
		draw.text((position[0]+1, charHeight+1), char, font=font, fill=shadowcolor)

		draw.text((position[0], charHeight), char, font=font, fill=(0xff, 0xff, 0xff, 0xff))
#		draw.text((position[0], charHeight), char, font=font, fill=(0x00, 0x00, 0x00, 0xff))
		
		charHeight += height

def fitimg(image, width, height):
	scale1 = float(width) / image.size[0]
	scale2 = float(height) / image.size[1]

	testcase1 = (image.size[0] * scale1, image.size[1] * scale1)
	testcase2 = (image.size[0] * scale2, image.size[1] * scale2)

	if testcase1[0] > width or testcase1[1] > height:
		value = testcase2
	else:
		value = testcase1

	return image.resize((int(value[0]), int(value[1])), Image.ANTIALIAS)

def make_comic(nicks, panels):
	panelHeight = 300
	panelWidth = 450

	filenames = os.listdir('chars/')
	shuffle(filenames)
	filenames = map(lambda x: os.path.join('chars', x), filenames[:len(nicks)])
	nicks = list(nicks)
	nicks = zip(nicks, filenames)
	nickmap = dict()

	for nick, filehandle in nicks:
		nickmap[nick] = Image.open(filehandle)

	imageWidth = panelWidth
	imageHeight = panelHeight * len(panels)

	background = Image.open(os.path.join('backgrounds', random.choice(os.listdir('backgrounds'))))

	temp = Image.new("RGBA", (imageWidth, imageHeight), (0xff, 0xff, 0xff, 0xff))
	font = ImageFont.truetype(font_file, font_size)

	for panel in range(len(panels)):
		panelImage = Image.new("RGBA", (panelWidth, panelHeight), (0xff, 0xff, 0xff, 0xff))
		panelImage.paste(background, (0, 0))
		draw = ImageDraw.Draw(panelImage)

		string1width = 0
		string1height = 0
		string2width = 0
		string2height = 0
		(string1, (string1width, string1height)) = wrap(panels[panel][0][1], font, draw, 2*panelWidth/3.0)
		rendertext(string1, font, draw, (10, 10))
		if len(panels[panel]) == 2:
			(string2, (string2width, string2height)) = wrap(panels[panel][1][1], font, draw, 2*panelWidth/3.0)
			rendertext(string2, font, draw, (panelWidth-10-string2width, string1height + 10))

		textHeight = string1height + 10
		if string2height > 0:
			textHeight += string2height + 10 + 5

		maxHeight = panelHeight - textHeight
		image1 = fitimg(nickmap[panels[panel][0][0]], 2*panelWidth/5.0-10, maxHeight)
		panelImage.paste(image1, (10, panelHeight-image1.size[1]), image1)

		if len(panels[panel]) == 2:
			image2 = fitimg(nickmap[panels[panel][1][0]], 2*panelWidth/5.0-10, maxHeight)
			image2 = image2.transpose(Image.FLIP_LEFT_RIGHT)
			panelImage.paste(image2, (panelWidth-image2.size[0]-10, panelHeight-image2.size[1]), image2)
		draw.line([(0, 0), (0, panelHeight-1), (panelWidth-1, panelHeight-1), (panelWidth-1, 0), (0, 0)], (0, 0, 0, 0xff))

		del draw
		temp.paste(panelImage, (0, panelHeight * panel))

	for item in nickmap:
		del item
	del nicks
	del background

	return temp
