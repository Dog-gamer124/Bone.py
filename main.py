import json
import math
import os
import random
import time

import discord
from discord import Guild
from discord.utils import get
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import sys
import discord.utils
import asyncio
from dotenv import load_dotenv

#### Colour intizalizations ####
class bcolors:
    HEADER = '\033[95m'
    CONSOLE = '\033[32m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'


#### Config initialization ####
with open("config.json") as f:
    config = json.load(f)

with open("tags.json") as f:
    tags = json.load(f)

trusted = config["trusted"]
owner = config["owner"]
spamchannel = config["spam_channel"]

prefix = ["$"]
bot = commands.Bot(command_prefix=prefix, case_insensitive=True, intents=discord.Intents.all(), help_command=None)
log_channel = 823874054180044811

#### Logging events ####


@bot.event
async def on_command(ctx):
    user = ctx.message.author
    command = ctx.message.system_content
    log = f"{user} Did command `{command}` in server {ctx.guild.name}/{ctx.guild.id}"
    await bot.get_channel(823874054180044811).send(log)
    print(bcolors.OKCYAN + log + bcolors.ENDC)


@bot.event
async def on_message(message):
    user = message.author.mention
    if not message.guild:
        if message.author != bot.user:
            await bot.get_channel(823874054180044811).send(f"{user} sent message: `{message.content}`")
            await bot.process_commands(message)
            print(f"{bcolors.OKCYAN}{user}/{message.author} sent message: `{message.content}`  {bcolors.ENDC}")
        else:
            return
    else:
        await bot.process_commands(message)
    if f"<@{bot.user.id}>" in message.content or f"<@!{bot.user.id}>" in message.content:
       await message.add_reaction("<:PING:796424651374985266>")


#### Error handler ####
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        user = ctx.message.author
        command = ctx.message.system_content
        log = f"{user} tried to do command `{command}`"
        await ctx.message.add_reaction("<:questionmarkemoji:828964827803287613>")
        await bot.get_channel(823874054180044811).send(log)
        print(bcolors.WARNING   + log + bcolors.ENDC)
    else:
        try:
            embed = discord.Embed(colour=0xff0000, timestamp=ctx.message.created_at,
                                  title="**An error occurred!** My owner was probably dumb again")
            embed.add_field(name="Error:", value=f"```{error}```")
            embed.set_footer(text=f"Caused by {ctx.author}")
            await ctx.send(embed=embed)
            print(bcolors.FAIL + f"An error occured: {error}" + bcolors.ENDC)
        except Exception as criticalexception:
            print(bcolors.FAIL + f" Couldnt send error message: {criticalexception}" + bcolors.ENDC)
        finally:
            print(f"error: {error}")

#### Bot initialization ####
@bot.event
async def on_ready():
    print(f"{bcolors.CONSOLE} Ready for password! {bcolors.ENDC}")
    password = str(input())
    if password:
        print(f"{bcolors.CONSOLE}| User authorized! Connecting to discord! {bcolors.ENDC}")
        print(f"{bcolors.CONSOLE}{bcolors.BOLD}| Connected to discord... {bcolors.ENDC}")
        print(f"{bcolors.CONSOLE}{bcolors.BOLD}| Logged in as {bcolors.OKGREEN}{bot.user.id} {bcolors.ENDC}")
        await bot.change_presence(activity=discord.Game(name='Attempting to get a bigger brain'))
        print(f"{bcolors.CONSOLE}{bcolors.BOLD}| Username is: {bcolors.OKGREEN}{bot.user.name} {bcolors.ENDC}")
        print(f"{bcolors.CONSOLE}{bcolors.BOLD}| Started {bcolors.OKGREEN}command {bcolors.CONSOLE}and {bcolors.OKGREEN}dm{bcolors.CONSOLE} logging events {bcolors.ENDC}")
        print(f"{bcolors.CONSOLE}{bcolors.BOLD}───────────────────────────────────────────────────────{bcolors.ENDC}")
    else:
        print(f"{bcolors.BOLD}{bcolors.FAIL} Unauthorized user detected stopping bot... {bcolors.ENDC}")
        sys.exit(0)
    channel = bot.get_channel(783944376711381005)
    await channel.send('I am going brrr')
    discord.AllowedMentions(everyone=False, users=True, roles=True, replied_user=True)

#### Commands ####
@bot.command(help="Makes the bot say things, OWNER ONLY", aliases=["c"])
async def copy(ctx, *, arg):
    if ctx.author.id in owner:
        await ctx.message.delete()
        await ctx.send(arg)
    else:
        await ctx.send("Only my owner can say that. L")
        await ctx.message.add_reaction(":Denied:786997173820588073")


@bot.command(help="Tests the bot to see if its working or something")
async def test(ctx):
    await ctx.send('Test received')
    await ctx.message.add_reaction("👍")


@bot.command(help="Shows the bots latency")
async def ping(ctx):
    bot_ping = round(bot.latency * 1000, 2)
    if bot_ping >= 1000:
        ping_color = 0x000000
    elif 500 <= bot_ping < 1000:
        ping_color = 0xC70039
    elif 350 <= bot_ping < 500:
        ping_color = 0xFF5900
    elif 200 <= bot_ping < 350:
        ping_color = 0x08E01C
    elif bot_ping < 200:
        ping_color = 0x0051FF
    embed = discord.Embed(title="Ping:", description=f"The ping is {bot_ping}ms!", colour=ping_color)
    await ctx.send(embed=embed)


@bot.command(help="Mass pings the person who did the command")
async def massping(ctx):
    user = ctx.message.author.id
    channel = ctx.message.channel.id
    if channel in spamchannel:
        await ctx.send(f"ping <@!{user}>")
        await ctx.send(f"ping <@!{user}>")
        await ctx.send(f"ping <@!{user}>")
        await ctx.send(f"ping <@!{user}>")
        await ctx.send(f"ping <@!{user}>")
    else:
        await ctx.send(f"This command only works in <#789195444957609994>")


@bot.command(help="Shows all guilds the bot is in, OWNER ONLY")
async def findguild(ctx):   #Stolen from @Discord_#1521
    if ctx.author.id in owner:
        guildcount = len(bot.guilds)
        discordguy = await bot.fetch_user(565515090171002901)
        q = []
        async for guild in bot.fetch_guilds():
            q.append(guild.name)
        embedVar = discord.Embed(color=0x00ff00)
        embedVar.add_field(name="Servers", value="\n".join(q))
        embedVar.add_field(name="Number of guilds", value=f"     {guildcount}", inline=True)
        embedVar.set_footer(text=f"Command copied from {discordguy.name}")
        await ctx.channel.send(embed=embedVar)
    else:
        await ctx.message.add_reaction(":Denied:786997173820588073")


@bot.command(help="Changes the bots staus, OWNER ONLY")
async def changestatus(ctx,thing, *, status):
    if ctx.author.id in owner:
        if thing == "game":
            await ctx.message.delete()
            await ctx.send("Changed status")
            await bot.change_presence(activity=discord.Game(name=f'{status}'))
        elif thing == "watch":
            await ctx.message.delete()
            await ctx.send("Changed status")
            await bot.change_presence(activity=discord.Activity(name=f'{status}', type=discord.ActivityType.watching))
        elif thing == "stream":
            await ctx.message.delete()
            await ctx.send("Changed status")
            await bot.change_presence(activity=discord.Streaming(name=f'{status}', url="https://discordpy.readthedocs.io/en/latest/", type=1))
        elif thing == "listening":
            await ctx.message.delete()
            await ctx.send("Changed status")
            await bot.change_presence(activity=discord.Activity(name=f'{status}', type=discord.ActivityType.listening))
    else:
        await ctx.message.add_reaction("<:WeeWooRed:771082566874169394>")


@bot.command(help="Stops the bot, OWNER AND ADMIN ONLY", aliases=["s"]) #W.I.P
@commands.has_role(765809794732261417 or 823850584011833344)
async def stop(ctx):
    role = discord.utils.find(lambda r: r.name == 'test', ctx.message.guild.roles)
    if ctx.author.id in owner:
        await ctx.message.delete()
        await ctx.send("Stopping the bot...")
        sys.exit(0)
    elif ctx.message.author.top_role in role:
        await ctx.message.delete()
        await ctx.send("Stopping the bot...")
        sys.exit(0)
    else:
        await ctx.message.add_reaction(":Denied:786997173820588073")
        await ctx.send("Why do you want me to stop, ;(.")


@bot.command()
async def findroles(ctx):
    e = [r.mention for r in ctx.message.author.roles[1:]]
    e.reverse()
    highestrole = [e[0]]
    truee =", ".join(e)
    embed = discord.Embed(title="", colour=0x7553d4)
    embed.add_field(value="".join(truee),name="Your roles")
    embed.add_field(value="".join(highestrole), name="Highest role", inline=False)
    embed.set_footer(text=f"Command issued by {ctx.message.author.display_name}")
    await ctx.send(embed=embed)

@bot.command()
async def embedTest(ctx):
        embed = discord.Embed(description="Hello this is an embbed lol", title="kekw")
        await ctx.message.delete()
        await ctx.send(embed=embed)


@bot.command(aliases=["usrdm"])
async def senddmtousr(ctx, user, *, content):
    if ctx.author.id in owner:
        user = await bot.fetch_user(user)
        await user.send(content)
        await ctx.message.add_reaction(":yes:786997173845622824")
    else:
     await ctx.message.add_reaction("WeeWooRed:771082566874169394")

@bot.command(aliases=["dmhis"])
async def dmhistory(ctx, user,limit):
    if ctx.author.id in owner:
        user = await bot.fetch_user(user)
        channel = user.dm_channel
        async for message in channel.history(limit=limit):
            print(message)

@bot.command()
async def getrektkid(ctx):
   await ctx.message.add_reaction("<:skulk:798614713645662238>")

@bot.command()
async def members(ctx):
    totalmember = len(ctx.guild.members)
    normalmember = len([m for m in ctx.guild.members if not m.bot])
    botmember = totalmember - normalmember
    memberslist =[totalmember, normalmember, botmember]
    embed = discord.Embed(title="Server member list", colour=0x7553d4)
    embed.add_field(name="Total members", value=f"{totalmember}", inline=True)
    embed.add_field(name="Normal members", value=f"{normalmember}", inline=True)
    embed.add_field(name="Bot members", value=f"{botmember}", inline=True)
    embed.set_footer(text=f"Command done by {ctx.message.author} showing members for {ctx.guild.name}")
    await ctx.send(embed=embed)

@bot.command()
async def token(ctx):
   await ctx.message.delete()
   message = await ctx.send("Fetching token pls wait")
   time.sleep(3.75)
   await message.delete()
   await ctx.send("lyBvnJ3xfLPgCQdlTWwg7TMPenya0DzBKi6i90tIfkOXRY2g9LwgDl2yj4t")

@bot.command()
async def help(ctx):
    commandButList = ''
    for command in bot.walk_commands():
        if len(command.aliases) == 0:
            commandButList += f"{command} - **{command.help}** \n"
        else:
            e = ", ".join(command.aliases)
            commandButList += f"{command}(**{e}**) - **{command.help}** \n"
    embed = discord.Embed(title="Help")
    embed.add_field(value=commandButList, name="e")
    await ctx.send(embed=embed)

@bot.command()
async def punch(ctx, puncheduser):
    usertopunch = puncheduser.display_name
    await ctx.send(f"{ctx.message.author.display_name} punched {usertopunch}")

@bot.command()
async def Panda(ctx):
   await ctx.send("https://minecraft.fandom.com/wiki/Panda <:panda_happy:825483587595403324>")

@bot.command(aliases=["dice", "die"])
async def roll(ctx, number = 6):
    e = await ctx.send("🎲 rolling die!")
    await ctx.message.delete()
    await asyncio.sleep(1.69)
    await e.delete()
    await ctx.send(f"The random number is: {random.randint(1, number)}")


load_dotenv()
bot.run(os.getenv('TOKEN'))
