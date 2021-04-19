import asyncio
import time
from tabulate import tabulate
import discord
from discord.ext import commands
import random
import math
import os
import requests
import time

client = commands.Bot(command_prefix='.', case_insensitive=True)

playerList = []


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="type .help for commands ¯\\_(ツ)_/¯"))
    print('LarryBot is ready')


@client.event
async def on_member_join(member):
    print(f'Welcome {member}, I am better than you at COD.')


@client.event
async def on_member_remove(member):
    print(f'See ya boss {member}')


@client.command()
async def ping(ctx):
    await ctx.send('Pong')


@client.command()
async def weather(ctx):
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


@commands.has_any_role("Lebron's Aunt")
@client.command()
async def addPlayer(ctx, player):
    if playerExists(player) == 1:
        await ctx.send("Player already exists.")
        return
    newArr = [player, 0]
    playerList.append(newArr)
    await ctx.send("Player successfully added.")


@commands.has_any_role("Lebron's Aunt")
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


@commands.has_any_role("Lebron's Aunt")
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


@commands.has_any_role("Lebron's Aunt")
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


@client.command()
async def makeWeightedTeamsOld(ctx, *players):
    defList = []
    if len(players) == 0:
        await ctx.send("Cannot have zero players")
        return
    else:
        await ctx.send("Forming fair teams...")
        for p in players:
            defList.append(mysplit(p))
        defList.sort(key=takeSecond, reverse=True)
        for i in range(len(defList)):
            if defList[i][1] > 10 or defList[i][1] < 0:
                await ctx.send("There is a rating higher than 10 or lower than 0\nThe ratings maximum is 10 and "
                               "minimum is 0")
                return
        teamOne = []
        teamTwo = []
        for num in range(len(defList)):
            if num == 0:
                teamOne.append(defList[num])
                continue
            if num == 1:
                teamTwo.append(defList[num])
                continue
            if num % 2 == 0:
                teamTwo.append(defList[num])
            else:
                teamOne.append(defList[num])
        await ctx.send("Team One\n-------------------")
        await asyncio.sleep(1)
        for p in teamOne:
            await ctx.send(p)
        await asyncio.sleep(2)
        await ctx.send("\nTeam Two\n--------------------")
        await asyncio.sleep(1)
        for p in teamTwo:
            await ctx.send(p)


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
