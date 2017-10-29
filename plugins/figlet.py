import discord
import plugins
from pcbot import Annotate, utils
client = plugins.client

from pyfiglet import Figlet

@plugins.command(name="figlet")
async def digifiglet(message: discord.Message, text: Annotate.CleanContent):
	f = Figlet()
	ret = f.renderText(text)
	await client.say(message, "```" + ret + "```")
