import asyncio
import os
from datetime import datetime, tzinfo, time, timedelta
import json
from time import sleep
import discord
from discord.ext import commands
from discord.utils import get



with open("config.json","r") as f:
    config = json.load(f)

channel_id = None


with open("schedule.json", "r") as fp:
    schedule = json.load(fp)



activity = discord.Game(name="Office Hour Calculator Sim 2023 GOTY Special Anniversary Edition")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="officehours ", intents=intents, activity=activity,help_command=None)

def is_maintainer(ctx):
    return ctx.message.author.id == maintainer.id


async def add_timeslot_to_embed(embed, timeslot):
    embed.add_field(name="Office", value=timeslot['office'], inline=False)
    embed.add_field(name="Start Time", value=timeslot['start_time'], inline=True)
    embed.add_field(name="End Time", value=timeslot['end_time'], inline=True)


@bot.command()
@commands.check(is_maintainer)
async def reloadschedule(ctx):
    global schedule
    with open("schedule.json", "r") as fp:
        schedule = json.load(fp)
    await ctx.message.delete()

@bot.command()
async def help(ctx):
    help_text = f"Office Hours Bot Help\nSubcommands:\nallhours [professor]: get all office hours for a certain professor\nhourstoday [professor]: get all office hours today for a certain professor\nnexthours [professor]: get next office hours for a certain professor\n"
    await ctx.message.author.send(help_text)


@bot.command(description="Get all office hours for a professor")
async def allhours(ctx, *args):
    global maintainer
    professor = ' '.join(args)
    professor = professor.strip()

    if professor in schedule.keys():

        for day in schedule[professor].keys():
            embed = discord.Embed(title=f"Professor {professor}'s Office Hours For {day}", url="")
            for timeslot in schedule[professor][day]:
                await add_timeslot_to_embed(embed, timeslot)
            await ctx.message.author.send(embed=embed)

    else:
        await ctx.message.author.send(
            f"I don't know that professor. Please ask <@{maintainer.id}> to add office hours for Professor {professor}")
    await ctx.message.delete()


@bot.command()
async def hourstoday(ctx, *args):
    global maintainer
    professor = ' '.join(args)
    professor = professor.strip()

    tz = datetime.utcnow().astimezone().tzinfo
    current_day = datetime.now(tz).date().strftime("%A")
    if professor in schedule.keys():
        if current_day in schedule[professor].keys():
            embed = discord.Embed(title=f"Professor {professor}'s Office Hours Today", url="")
            for timeslot in schedule[professor][current_day]:
                embed.add_field(name="Office", value=timeslot['office'], inline=False)
                embed.add_field(name="Start Time", value=timeslot['start_time'], inline=True)
                embed.add_field(name="End Time", value=timeslot['end_time'], inline=True)
            await ctx.message.author.send(embed=embed)
            await ctx.message.delete()
        else:
            await ctx.message.author.send(f"Professor {professor} has no office hours today")
    else:
        await ctx.message.author.send(
            f"I don't know that professor. Please ask <@{maintainer.id}> to add office hours for Professor {professor}")
    await ctx.message.delete()


@bot.command()
async def nexthours(ctx, *args):
    arg = ' '.join(args)
    arg = arg.strip()

    tz = datetime.utcnow().astimezone().tzinfo
    current_day = datetime.now(tz).date().strftime("%A")
    current_time = datetime.now(tz).time()
    sent = False
    if arg not in schedule:
        await ctx.message.author.send(
            f"I don't know that professor. Please ask <@{maintainer.id}> to add office hours for Professor {arg}")
        await ctx.message.delete()
        return
    if current_day in schedule[arg].keys():
        for timeslot in schedule[arg][current_day]:
            if current_time < datetime.strptime(timeslot["start_time"], "%H:%M").time():
                embed = discord.Embed(title=f"Professor {arg}'s Next Office Hours Today", url="")
                await add_timeslot_to_embed(embed,timeslot)
                await ctx.message.author.send(embed=embed)
                sent = True
                break
            elif datetime.strptime(timeslot["start_time"], "%H:%M").time() < current_time < datetime.strptime(
                    timeslot["end_time"], "%H:%M").time():
                embed = discord.Embed(title=f"Professor {arg}'s Current Office Hours Today", url="")
                await add_timeslot_to_embed(embed,timeslot)

                await ctx.message.author.send(embed=embed)

                sent = True
                break
    if not sent:
        next_day_raw = datetime.combine(datetime.now(tz).date() + timedelta(days=1), time(0, 0, 0))
        next_day_name = next_day_raw.strftime("%A")

        day = 1
        while next_day_name not in schedule[arg]:
            day += 1
            next_day_raw = datetime.combine(datetime.now(tz).date() + timedelta(days=1), time(0, 0, 0))
            next_day_name = next_day_raw.strftime("%A")

        embed = discord.Embed(title=f"Professor {arg}'s Next Office Hours", url="")
        embed.add_field(name="Day", value=next_day_raw.strftime("%A, %m/%d/%Y"),
                        inline=True)
        await add_timeslot_to_embed(embed,schedule[arg][next_day_name][0])
        await ctx.message.author.send(embed=embed)

    await ctx.message.delete()
    # await ctx.send(current_day)


# @tasks.loop(seconds=10)
# async def background_task():
#     while True:
#         e = datetime.now()
#         channel = bot.get_channel(1067602544827846676)
#         currenttime = e.strftime("%a, %I:%M:%S %p")
#         if currenttime == "Wed, 10:17:00 PM":
#             await channel.send("<@&1067958167167848558> <@786806826762240031> is now hosting office hours until 8:30PM")
#             await asyncio.sleep(1)
#

@bot.event
async def on_ready():
    global channel_id
    global maintainer
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'

    )
    channel_id = get(bot.guilds[0].channels, name="office-hours-bot")
    maintainer = bot.guilds[0].get_member_named("gnations#5314")
    # await bot.change_presence(activity=discord.Game(name="Office Hour Calculator Sim 2023 GOTY"))


# bot.loop.create_task(background_task)
bot.run(config["token"])
