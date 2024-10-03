import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True


bot = commands.Bot(command_prefix='(hewy ', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Sorry, I am unable to understand.')
    else:
        print(error)
        await ctx.send('Internal Error')


@bot.event
async def setup_hook():
    await bot.load_extension('cogs.music')


@bot.command()
async def hello(ctx):
    user_display_name = ctx.author.display_name
    await ctx.send(f'Hi {user_display_name}')


bot.run(os.getenv('DISCORD_TOKEN'))
