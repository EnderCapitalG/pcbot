#Made for cloudbot
#Created by ender.capitalg@gmail.com

import discord
import plugins
client = plugins.client

import requests
import lxml.html

fml_array = []
array_count = 0
array_total = 0

def fml_parse():
	global array_total, array_count, fml_array
	fml_array = []
	array_count = 0
	array_total = 0

	req = requests.get("http://www.fmylife.com/random").text
	html = lxml.html.fromstring(req)
#	table = html.xpath("//a[@class='fmllink']/@href")
#	table = html.xpath("//a[@class='fmllink']/text()")
#	table = html.xpath("//p[@class='block-min']/a/text()")
#	table = html.xpath("//div[@class='panel-content']/p[@class='block']/a/text()")
	table = html.xpath("//div[@class='panel-content']/p[@class='block hidden-xs']/a/text()")
	

	ar = []
	for element in table:
		ar.append(element.strip('\n').strip('\r'))
		array_total += 1
	fml_array = ar
	print("fml_array updated.")

#so we can have the array filled when the bot starts
fml_parse()


@plugins.command(name="fml")
async def fml(message: discord.Message):
	global fml_array, array_count, array_total
	if not fml_array or array_count >= array_total:
		await fml_parse()
	fmylife = ret_fml()
	await client.say(message, fmylife)


def ret_fml():
	global array_count, array_total, fml_array

#	retval = ''

#	while "FML" not in fml_array[array_count]:
#		retval = retval + fml_array[array_count]
#		array_count += 1

	retval = fml_array[array_count]

	if retval is None or retval is "":
		array_count += 1
		retval = fml_array[array_count]

	array_count += 1
	return retval
