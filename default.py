import asyncio
import time
from tabulate import tabulate
import discord
from discord.ext import commands, tasks
import random
import math
import os
import requests

client = commands.Bot(command_prefix='.', case_insensitive=True)

playerList = []

# Weather api
api_key = "64c25ea20b450ab59e4e0f5cd2158176"
base_url = "http://api.openweathermap.org/data/2.5/weather?"


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="type .help for commands ¯\\_(ツ)_/¯"))
    print('LarryBot is ready')


@client.event
async def on_member_join(member):
    print(f'Welcome {member}')


@client.event
async def on_member_remove(member):
    print(f'See ya {member}')


@client.command()
async def ping(ctx):
    await ctx.send('Pong')


# NHL Api

nhlResponse = requests.get("https://statsapi.web.nhl.com/api/v1/teams")


@client.command()
async def getNHLTeams(ctx):
    nhlteams = nhlResponse.json()['teams']
    teamArr = []
    for t in nhlteams:
        newArr = [str(t['id']), t['name']]
        teamArr.append(newArr)
    await ctx.send(tabulate(teamArr), headers=['Team ID', "Team Name"], tablefmt='fancy_grid')

@client.command()
async def getTeamDetails(ctx, teamId):
    channel = ctx.message.channel
    team = requests.get("https://statsapi.web.nhl.com/api/v1/teams/" + str(id)).json()
    teamName = team['teams'][0]['name']
    teamVenue = team['teams'][0]['venue']['name']
    teamDivision = team['teams'][0]['division']['name']
    teamId = team['teams'][0]['id']
    embed = discord.Embed(title=f"{teamName}",
                          color=ctx.guild.me.top_role.color,
                          timestamp=ctx.message.created_at, )
    embed.add_field(name="Team Id", value=f"{str(teamId)}", inline=False)
    embed.add_field(name="Venue", value=f"**{teamVenue}**", inline=False)
    embed.add_field(name="Division", value=f"{teamDivision}", inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await channel.send(embed=embed)

@client.command()
async def getPlayerDetails(ctx, teamId, playerNum):
    channel = ctx.message.channel
    roster = requests.get("https://statsapi.web.nhl.com/api/v1/teams/" + str(teamId) + "/roster").json()['roster']
    for i in roster:
        if (int(i['jerseyNumber']) == playerNum):
            link = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(i['person']['id'])).json()
            playerName = i['person']['fullName']
            playerNumber = i['jerseyNumber']
            playerPos = i['position']['name']
            playerRole = i['position']['type']
            playerCity = link['people']['birthCity']
            playerCountry = link['people']['birthStateProvince']
            playerNationality = link['people']['nationality']
            playerHeight = link['people']['height']
            playerWeight = link['people']['weight']
            handness = link['people']['shootCatches']
            if link['people']['alternateCaptain'] == True:
                playerIsAlt = True
            else:
                playerIsAlt = False
            if link['people']['captain'] == True:
                playerIsCap = True
            else:
                playerIsCap = False
            embed = discord.Embed(title=f"{playerName}",
                                  color=ctx.guild.me.top_role.color,
                                  timestamp=ctx.message.created_at, )
            embed.add_field(name="Jersey Number", value=f"{playerNumber}", inline=False)
            embed.add_field(name="Position", value=f"**{playerPos}**", inline=False)
            embed.add_field(name="Type", value=f"{playerRole}", inline=False)
            embed.add_field(name="Hand", value=f"{handness}", inline=False)
            embed.add_field(name="Birth City", value=f"{playerNumber}", inline=False)
            embed.add_field(name="Country", value=f"**{playerPos}**", inline=False)
            embed.add_field(name="Nationality", value=f"{playerRole}", inline=False)
            embed.add_field(name="Height", value=f"**{playerPos}**", inline=False)
            embed.add_field(name="Weight", value=f"{playerRole}", inline=False)
            if playerIsCap == True:
                embed.add_field(name="Captain", value=f"True", inline=False)
            if playerIsAlt == True:
                embed.add_field(name="Alternate Captain", value=f"True", inline=False)
            if link['people']['rookie'] == True:
                embed.add_field(name="Rookie", value=f"True", inline=False)
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await channel.send(embed=embed)


@client.command()
async def getNHLRoster(ctx, teamId):
    team = requests.get("https://statsapi.web.nhl.com/api/v1/teams/" + str(teamId)).json()
    roster = requests.get("https://statsapi.web.nhl.com/api/v1/teams/" + str(teamId) + "/roster").json()
    rosterArr = []
    for p in range(len(roster['roster'])):
        pArr = [roster['roster'][p]['person']['fullName'], roster['roster'][p]['jerseyNumber'],
                roster['roster'][p]['position']['abbreviation']]
        rosterArr.append(pArr)
    playerT = tabulate(rosterArr, headers=['Player Name', 'Jersey Number', 'Position'])
    await ctx.send(playerT)

@client.command()
async def weather(ctx, *, city: str):
    city_name = city
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    channel = ctx.message.channel
    if x["cod"] != "404":
        async with channel.typing():
            y = x["main"]
            current_temperature = y["temp"]
            current_temperature_celsiuis = str(round(current_temperature - 273.15))
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            temp_high = str(round(y['temp_max'] - 273.15))
            temp_low = str(round(y['temp_min'] - 273.15))
            z = x["weather"]
            weather_description = z[0]["description"]
            embed = discord.Embed(title=f"Weather in {city_name}",
                                  color=ctx.guild.me.top_role.color,
                                  timestamp=ctx.message.created_at, )
            embed.add_field(name="Descripition", value=f"**{weather_description}**", inline=False)
            embed.add_field(name="Current Temperature(C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
            embed.add_field(name="High Temperature for Today(C)", value=f"**{temp_high}°C**", inline=False)
            embed.add_field(name="Low Temperature for Today(C)", value=f"**{temp_low}°C**", inline=False)
            embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
            embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await channel.send(embed=embed)
    else:
        await channel.send("City not found.")

@client.command()
async def windsorWeatherReport(ctx):
    url = "https://community-open-weather-map.p.rapidapi.com/weather"
    querystring = {"q": "Windsor", "lat": "0", "lon": "0", "callback": "test", "id": "2172797", "lang": "null",
                   "units": "metric", "mode": "xml, html"}
    headers = {
        'x-rapidapi-key': "af9c139833mshfbd108e5b781b27p1ee771jsn2060a2fe19f1",
        'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    await ctx.send("Good Morning! Here is Windsor Weather for Today")
    await ctx.send("")
    await ctx.send("Weather Right Now: " + response.text.split(',')[4].split(':')[1].strip('"'))
    await ctx.send("Current Temperature: " + response.text.split(',')[7].split(':')[2] + '℃')
    await ctx.send("Today's Low: " + response.text.split(',')[9].split(':')[1])
    await ctx.send("Today's High: " + response.text.split(',')[10].split(':')[1])


@client.command()
async def bestCODPlayer(ctx):
    await ctx.send('LarryNut')


@client.command()
async def makeTeams(ctx, *players):
    playerList = []
    if len(players) == 0:
        await ctx.send("Cannot have zero players")
        return
    else:
        await ctx.send("Forming randomized teams...")
        for p in players:
            playerList.append(p)
        random.shuffle(playerList)
        fHalfLen = math.floor(len(playerList) / 2)
        sHalfLen = len(playerList) - fHalfLen
        await ctx.send("Team One\n----------------------")
        await asyncio.sleep(1)
        for i in range(fHalfLen):
            await ctx.send(playerList[i])
        await asyncio.sleep(1)
        await ctx.send("\nTeam Two\n----------------------")
        await asyncio.sleep(1)
        for y in range(sHalfLen):
            await ctx.send(playerList[fHalfLen + y])


def mysplit(s):
    head = s.rstrip('0123456789')
    tail = s[len(head):]
    return head, tail


def takeSecond(elem):
    return int(elem[1])


def playerExists(player):
    for p in range(len(playerList)):
        if playerList[p][0].lower() == player.lower():
            return 1
    return -1


def findPlayer(player):
    if playerExists(player) != 1:
        return -1
    for p in range(len(playerList)):
        if playerList[p][0].lower() == player.lower():
            return p


@client.command()
async def addPlayer(ctx, player):
    if playerExists(player) == 1:
        await ctx.send("Player already exists.")
        return
    newArr = [player, 0]
    playerList.append(newArr)
    await ctx.send("Player successfully added.")


@client.command()
async def addPlayerWRating(ctx, player, rating):
    if playerExists(player) == 1:
        await ctx.send("Player already exists.")
        return
    newArr = [player, rating]
    playerList.append(newArr)
    await ctx.send("Player successfully added.")


@client.command(brief="Returns table of all players")
async def showAllPlayers(ctx):
    await ctx.send(tabulate(playerList, headers=["Player", "Rating"], tablefmt='fancy_grid'))


@client.command()
async def showAllPlayersLoc():
    return tabulate(playerList, headers=["Player", "Rating"], tablefmt='fancy_grid')


@client.command(brief="Shows requested player")
async def showPlayer(ctx, player):
    if findPlayer(player) != -1:
        await ctx.send("Player found...")
        playerLoc = findPlayer(player)
        playerToShow = playerList[playerLoc]
        newList = []
        newList.append(playerToShow)
        await ctx.send(tabulate(newList, headers=["Player", "Rating"], tablefmt='fancy_grid'))
    else:
        await ctx.send("Player " + player + " does not exist.")
        return


@client.command()
async def showPlayerLoc(player):
    if findPlayer(player) != -1:
        playerLoc = findPlayer(player)
        playerToShow = playerList[playerLoc]
        newList = []
        newList.append(playerToShow)
        return tabulate(newList, headers=["Player", "Rating"], tablefmt='fancy_grid')
    else:
        return "Player " + player + " does not exist."


@client.command(brief="Changes specified users rating")
async def editRating(ctx, player, rating):
    if findPlayer(player) != -1:
        playerLoc = findPlayer(player)
        playerList[playerLoc][1] = rating
        await ctx.send("Rating successfully changed.")
        playerLoc = findPlayer(player)
        playerToShow = playerList[playerLoc]
        newList = []
        newList.append(playerToShow)
        await ctx.send(tabulate(newList, headers=["Player", "Rating"], tablefmt='fancy_grid'))


@client.command(brief="Removes player from list")
async def removePlayer(ctx, player):
    if findPlayer(player) != -1:
        playerLoc = findPlayer(player)
        del playerList[playerLoc]
        await ctx.send("Player successfully deleted.")
        await ctx.send("Updated list")
        await ctx.send(showAllPlayersLoc())


@client.command(brief="Returns your username")
async def myName(ctx):
    await ctx.send(str(ctx.author))


@client.command(brief="Adds you to player list")
async def addMe(ctx):
    playerA = str(ctx.author)
    player = playerA.split('#')[0]
    if playerExists(player) == 1:
        await ctx.send("Player already exists.")
        return
    newArr = [player, 0]
    playerList.append(newArr)
    await ctx.send("Player successfully added.")


@client.command(brief="Adds you to the player list. Format:.addMeRated {RATING}")
async def addMeRated(ctx, rating):
    playerA = str(ctx.author)
    player = playerA.split('#')[0]
    if playerExists(player) == 1:
        await ctx.send("Player already exists.")
        return
    newArr = [player, rating]
    playerList.append(newArr)
    await ctx.send("Player successfully added.")




@client.command(brief="Makes fair teams based on player ratings")
async def makeWeightedTeams(ctx, *players):
    if len(players) == 0:
        await ctx.send("Cannot have zero players")
        return
    else:
        pList = []
        for p in players:
            pList.append(p)
        for i in range(len(pList)):
            if playerExists(pList[i]) != 1:
                await ctx.send("Could not locate " + pList[i])
                return
        await ctx.send("Forming fair teams...")
        localList = []
        for y in range(len(pList)):
            if findPlayer(pList[y]) != -1:
                localList.append(playerList[findPlayer(pList[y])])
        teamOne = []
        teamTwo = []
        for num in range(len(localList)):
            if num == 0:
                teamOne.append(localList[num])
                continue
            if num == 1:
                teamTwo.append(localList[num])
                continue
            if num % 2 == 0:
                teamTwo.append(localList[num])
            else:
                teamOne.append(localList[num])
        await ctx.send("Team One\n-------------------")
        await asyncio.sleep(1)
        await ctx.send(tabulate(teamOne, headers=["Players", "Ratings"], tablefmt='fancy_grid'))
        await asyncio.sleep(2)
        await ctx.send("\nTeam Two\n--------------------")
        await asyncio.sleep(1)
        await ctx.send(tabulate(teamTwo, headers=["Players", "Ratings"], tablefmt='fancy_grid'))


@client.command(brief='Gives you suggestions on what to do', description='Gives you suggestions on what to do')
async def whatToDo(ctx):
    listOfStuff = ["Play Warzone", "Play private match Cold War", "Play pubs Cold War", "Play NHL", "Play FIFA",
                   "Take a nap", "Order food", "Play 2K"]
    random.shuffle(listOfStuff)
    await ctx.send(listOfStuff[0])


class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=discord.Color.blurple(), description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)


client.help_command = MyHelpCommand()

client.run(os.environ['token'])
