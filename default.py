import asyncio
from tabulate import tabulate
import discord
from discord.ext import commands, tasks
import random
import math
import requests
import os
from datetime import date, timedelta

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
    teamArr = []
    nhlteamsj = nhlResponse.json()
    nhlteams = nhlteamsj['teams']
    for t in nhlteams:
        newArr = [str(t['id']), t['name']]
        teamArr.append(newArr)
    await ctx.send("```"+tabulate(teamArr, headers=["Team ID", "Team Name"]) + "```")


@client.command()
async def getTeamDetails(ctx, teamId):
    channel = ctx.message.channel
    team = requests.get("https://statsapi.web.nhl.com/api/v1/teams/" + str(teamId)).json()
    teamName = team['teams'][0]['name']
    teamVenue = team['teams'][0]['venue']['name']
    teamDivision = team['teams'][0]['division']['name']
    teamId = team['teams'][0]['id']
    embed = discord.Embed(title=f"**{teamName}**",
                          color=ctx.guild.me.top_role.color,
                          timestamp=ctx.message.created_at, )
    embed.add_field(name="**Team Id**", value=f"{str(teamId)}", inline=False)
    embed.add_field(name="**Venue**", value=f"{teamVenue}", inline=False)
    embed.add_field(name="**Division**", value=f"{teamDivision}", inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await channel.send(embed=embed)


@client.command()
async def getPlayerDetails(ctx, teamId: int, playerNum: int):
    channel = ctx.message.channel
    roster = requests.get("https://statsapi.web.nhl.com/api/v1/teams/" + str(teamId) + "/roster").json()['roster']
    for i in roster:
        if (int(i['jerseyNumber']) == int(playerNum)):
            link = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(i['person']['id'])).json()
            playerName = i['person']['fullName']
            playerNumber = i['jerseyNumber']
            playerPos = i['position']['name']
            playerRole = i['position']['type']
            playerCity = link['people'][0]['birthCity']
            playerCountry = "none"
            playerNationality = link['people'][0]['nationality']
            if playerNationality == "USA" or playerNationality == "CAN":
                playerCountry = link['people'][0]['birthStateProvince']
            playerHeight = link['people'][0]['height']
            playerWeight = link['people'][0]['weight']
            handness = link['people'][0]['shootsCatches']
            if link['people'][0]['alternateCaptain'] == True:
                playerIsAlt = True
            else:
                playerIsAlt = False
            if link['people'][0]['captain'] == True:
                playerIsCap = True
            else:
                playerIsCap = False
            embed = discord.Embed(title=f"**{playerName}**",
                                  color=ctx.guild.me.top_role.color,
                                  timestamp=ctx.message.created_at, )
            embed.add_field(name="**Jersey Number**", value=f"{playerNumber}", inline=False)
            embed.add_field(name="**Position**", value=f"{playerPos}", inline=False)
            embed.add_field(name="**Type**", value=f"{playerRole}", inline=False)
            embed.add_field(name="**Hand**", value=f"{handness}", inline=False)
            embed.add_field(name="**Birth City**", value=f"{playerCity}", inline=False)
            if not playerCountry == "none":
                embed.add_field(name="**Country**", value=f"{playerCountry}", inline=False)
            embed.add_field(name="**Nationality**", value=f"{playerNationality}", inline=False)
            embed.add_field(name="**Height**", value=f"{playerHeight}", inline=False)
            embed.add_field(name="**Weight**", value=f"{playerWeight}", inline=False)
            if playerIsCap == True:
                embed.add_field(name="**Captain**", value=f"True", inline=False)
            if playerIsAlt == True:
                embed.add_field(name="**Alternate Captain**", value=f"True", inline=False)
            if link['people'][0]['rookie'] == True:
                embed.add_field(name="**Rookie**", value=f"True", inline=False)
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await channel.send(embed=embed)


@client.command()
async def getNHLRoster(ctx,*, teamId:int):
    roster = requests.get("https://statsapi.web.nhl.com/api/v1/teams/" + str(teamId) + "/roster").json()
    rosterArr = []
    for p in range(len(roster['roster'])):
        pArr = [roster['roster'][p]['person']['fullName'], roster['roster'][p]['jerseyNumber'],
                roster['roster'][p]['position']['abbreviation']]
        rosterArr.append(pArr)
    playerT = tabulate(rosterArr, headers=['Player Name', 'Jersey Number', 'Position'])
    await ctx.send("```"+playerT+"```")

@client.command()
async def getPlayerStats(ctx, teamId: int, playerNum: int, year:str):
    postYear = int(year) + 1
    yearStr = year + str(postYear)
    yearFStr = year + "/" + str(postYear)
    channel = ctx.message.channel
    postYear = int(year) + 1
    roster = requests.get("https://statsapi.web.nhl.com/api/v1/teams/" + str(teamId) + "/roster").json()['roster']
    for i in roster:
        if (int(i['jerseyNumber']) == int(playerNum)):
            link = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(
                i['person']['id']) + "/stats?stats=statsSingleSeason&season=" + str(yearStr)).json()
            playerDetails = "https://statsapi.web.nhl.com/api/v1/people/" + str(
                i['person']['id'])
            playerName = i['person']['fullName']
            if not i['position'] == 'G':
                playerNumber = i['jerseyNumber']
                playerPos = i['position']['name']
                seasonType = link['stats'][0]['type']['gameType']['description']
                gamesPlayed = link['stats'][0]['splits'][0]['stat']['games']
                goals = link['stats'][0]['splits'][0]['stat']['goals']
                assists = link['stats'][0]['splits'][0]['stat']['assists']
                points = link['stats'][0]['splits'][0]['stat']['points']
                pim = link['stats'][0]['splits'][0]['stat']['pim']
                ppp = link['stats'][0]['splits'][0]['stat']['powerPlayPoints']
                gwg = link['stats'][0]['splits'][0]['stat']['gameWinningGoals']
                plusMinus = link['stats'][0]['splits'][0]['stat']['plusMinus']
                hits = link['stats'][0]['splits'][0]['stat']['hits']
                embed = discord.Embed(title=f"{playerName} + yearFStr",
                                      color=ctx.guild.me.top_role.color,
                                      timestamp=ctx.message.created_at, )
                embed.add_field(name="**Player Number**", value=f"{str(playerNumber)}", inline=False)
                embed.add_field(name="**Position**", value=f"{playerPos}", inline=False)
                embed.add_field(name="**Season Type**", value=f"{seasonType}", inline=False)
                embed.add_field(name="**Games Played**", value=f"{str(gamesPlayed)}", inline=False)
                embed.add_field(name="**Goals**", value=f"{str(goals)}", inline=False)
                embed.add_field(name="**Assists**", value=f"{str(assists)}", inline=False)
                embed.add_field(name="**Points**", value=f"{str(points)}", inline=False)
                embed.add_field(name="**PIM**", value=f"{str(pim)}", inline=False)
                embed.add_field(name="**Powerplay Points**", value=f"{str(ppp)}", inline=False)
                embed.add_field(name="**GWG**", value=f"{str(gwg)}", inline=False)
                embed.add_field(name="**+/-**", value=f"{str(plusMinus)}", inline=False)
                embed.add_field(name="**Hits**", value=f"{str(hits)}", inline=False)
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(title=f"{playerName} + yearFStr",
                                      color=ctx.guild.me.top_role.color,
                                      timestamp=ctx.message.created_at, )
                wins = link['stats'][0]['splits'][0]['stat']['wins']
                losses = link['stats'][0]['splits'][0]['stat']['losses']
                shutouts = link['stats'][0]['splits'][0]['stat']['shutouts']
                svpercent = link['stats'][0]['splits'][0]['stat']['savePercentage']
                gaa = link['stats'][0]['splits'][0]['stat']['goalAgainstAverage']
                gp = link['stats'][0]['splits'][0]['stat']['games']
                embed.add_field(name="**Wins**", value=f"{str(wins)}", inline=False)
                embed.add_field(name="**Losses**", value=f"{str(losses)}", inline=False)
                embed.add_field(name="**Shutouts**", value=f"{str(shutouts)}", inline=False)
                embed.add_field(name="**Save %**", value=f"{str(svpercent)}", inline=False)
                embed.add_field(name="GAA", value=f"{str(gaa)}", inline=False)
                embed.add_field(name="Games Played", value=f"{str(gp)}", inline=False)
                embed.set_footer(text=f"Requested by {ctx.author.name}")
                await channel.send(embed=embed)

# soccer api
headers = {
    "apikey": "852ce3b0-a51d-11eb-a4e1-e9fa778bd020"}

@client.command()
async def getCountries(ctx, cont):
    params = (
        ("continent", cont),
    )
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/countries', headers=headers, params=params).json()['data']
    codesArr = []
    countriesArr = []
    for i in response:
        codesArr.append(i)
    for r in range(len(codesArr)):
        country = [response[codesArr[r]]['country_id'], response[codesArr[r]]['name']]
        countriesArr.append(country)
    await ctx.send(tabulate(countriesArr, headers=["Country ID", "Name"]))

@client.command()
async def getLeagues(ctx):
    params = (
        ("subscribed", True),
    )
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/leagues', headers=headers, params=params).json()['data']
    leaugeOne = [response[0]['league_id'],response[0]['name']]
    leaugeTwo = [response[1]['league_id'], response[1]['name']]
    leagues = [leaugeOne,leaugeTwo]
    await ctx.send(tabulate(leagues, headers=["League ID", "Name"]))

@client.command()
async def getTeams(ctx,countryId):
    params = (
        ("country_id", countryId),
    )
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/teams', headers=headers, params=params).json()['data']
    teamArr = []
    charLen = 0
    for i in range(len(response)):
        team = [response[i]['team_id'], response[i]['name']]
        charLen += len(str(response[i]['team_id'])) + len(response[i]['name'])
        if charLen >= 1000:
            await ctx.send(tabulate(teamArr, headers=["Team ID", "Name"]))
            charLen = 0
            del(teamArr)
            teamArr = []
        teamArr.append(team)
    await ctx.send(tabulate(teamArr, headers=["Team ID", "Name"]))

@client.command()
async def getTeamInfo(ctx, id):
    channel = ctx.message.channel
    params = (
    )
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/teams/' + id, headers=headers, params=params).json()['data']
    embed = discord.Embed(title=f"{response['name']}",
                          color=ctx.guild.me.top_role.color,
                          timestamp=ctx.message.created_at, )
    embed.add_field(name="Short Code", value=f"**{response['short_code']}**", inline=False)
    embed.add_field(name="Team ID", value=f"**{str(response['team_id'])}**", inline=False)
    embed.set_thumbnail(url=response['logo'])
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await channel.send(embed=embed)

@client.command()
async def getSeasons(ctx,leagueId):
    params = (
        ("league_id", leagueId),
    )
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/seasons', headers=headers, params=params).json()['data']
    seasonsArr = []
    for i in range(len(response)):
        season = [response[i]['season_id'], response[i]['name'], response[i]['start_date'], response[i]['end_date']]
        seasonsArr.append(season)
    await ctx.send(tabulate(seasonsArr, headers=["Season ID", "Name", "Start Date", "End Date"]))

@client.command()
async def getMatches(ctx, seasonId, dateFrom = "0000-00-00", dateTo = "2100-01-01"):
    params = (
        ("season_id", seasonId),
        ("date_from", dateFrom),
        ("date_to", dateTo)
    )
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/matches', headers=headers, params=params).json()['data']
    matchesArr = []
    for i in range(len(response)):
        match = [response[i]['match_id'], response[i]['status'], response[i]['match_start'], response[i]['home_team']['name'],response[i]['away_team']['name'],response[i]['stats']['ft_score']]
        matchesArr.append(match)
    await ctx.send(tabulate(matchesArr, headers=["Match Id", "Status", "Match Start", "Home Team", "Away Team", "Final Score (Home-Away)"]))

target_channel_id = 829376713266823230

@tasks.loop(hours=24)
async def getMatchesLoop(seasonId = 510):
    today = date.today()
    tomorrow = date.today() + timedelta(days=2)
    params = (
        ("season_id", seasonId),
        ("date_from", today),
        ("date_to", tomorrow)
    )
    message_channel = client.get_channel(target_channel_id)
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/matches', headers=headers, params=params).json()['data']
    matchesArr = []
    for i in range(len(response)):
        match = [response[i]['match_id'], response[i]['status'],response[i]['home_team']['name'],response[i]['away_team']['name'],response[i]['stats']['ft_score']]
        matchesArr.append(match)
    await message_channel.send("Today's Serie A Results")
    await message_channel.send(tabulate(matchesArr, headers=["Match Id", "Status", "Home Team", "Away Team", "Final Score (Home-Away)"]))

@getMatchesLoop.before_loop
async def before():
    await client.wait_until_ready()
    print("Finished Waiting")


@client.command()
async def getLiveMatches(ctx, seasonId):
    params = (
        ("season_id", seasonId),
        ("live", True)
    )
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/matches', headers=headers, params=params).json()['data']
    matchesArr = []
    for i in range(len(response)):
        match = [response[i]['match_id'], response[i]['status'], response[i]['match_start'], response[i]['home_team']['name'],response[i]['away_team']['name'],response[i]['stats']['ft_score']]
        matchesArr.append(match)
    await ctx.send(tabulate(matchesArr, headers=["Match Id", "Status", "Match Start", "Home Team", "Away Team", "Final Score (Home-Away)"]))

@client.command()
async def getPlayers(ctx,countryId, minAge = 0, maxAge = 100):
    params = (
        ("country_id", countryId),
        ("min_age", minAge),
        ("max_age", maxAge)
    )
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/players', headers=headers, params=params).json()['data']
    playersArr = []
    charLen = 0
    for i in range(len(response)):
        player = [response[i]['player_id'], response[i]['firstname'], response[i]['lastname'], response[i]['age']]
        charLen += len(str(response[i]['player_id'])) + len(response[i]['firstname']) + len(response[i]['lastname']) + len(str(response[i]['age']))
        if charLen >= 500:
            await ctx.send(tabulate(playersArr, headers=["Player ID", "First Name", "Last Name", "Age"]))
            del(playersArr)
            charLen = 0
            playersArr = []
        playersArr.append(player)
    await ctx.send(tabulate(playersArr, headers=["Player ID", "First Name", "Last Name","Age"]))

@client.command()
async def getPlayerInfo(ctx, playerId):
    params = (
    )
    channel = ctx.message.channel
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/players/' + playerId, headers=headers, params=params).json()['data']
    embed = discord.Embed(title=f"{response['firstname'] + ' ' + response['lastname']}",
                          color=ctx.guild.me.top_role.color,
                          timestamp=ctx.message.created_at, )
    embed.add_field(name="Age", value=f"**{str(response['age'])}**", inline=False)
    embed.add_field(name="Birthday", value=f"**{response['birthday']}**", inline=False)
    embed.set_thumbnail(url=response['img'])
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await channel.send(embed=embed)

@client.command()
async def topScorers(ctx,seasonId):
    params = (
        ("season_id", seasonId),
    )
    response = requests.get('https://app.sportdataapi.com/api/v1/soccer/topscorers', headers=headers, params=params).json()['data']
    standings = []
    charLen = 0
    for i in range(len(response)):
        player = [response[i]['pos'],response[i]['player']['player_name'], response[i]['team']['team_name'], response[i]['goals']['overall']]
        charLen += len(str(response[i]['pos'])) + len(response[i]['player']['player_name']) + len(response[i]['team']['team_name']) + len(str(response[i]['goals']['overall']))
        if charLen >= 500:
            await ctx.send(tabulate(standings, headers=["Rank", "Player", "Team", "Goals"]))
            del(standings)
            charLen = 0
            standings = []
        standings.append(player)
    await ctx.send(tabulate(standings, headers=["Rank", "Player", "Team", "Goals"]))

# weather api
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

@tasks.loop(hours=24)
async def windsorWeatherReport():
    city_name = "Windsor"
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    channel = client.get_channel(target_channel_id)
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
            embed = discord.Embed(title=f"Weather in {city_name}")
            embed.add_field(name="Descripition", value=f"**{weather_description}**", inline=False)
            embed.add_field(name="Current Temperature(C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
            embed.add_field(name="High Temperature for Today(C)", value=f"**{temp_high}°C**", inline=False)
            embed.add_field(name="Low Temperature for Today(C)", value=f"**{temp_low}°C**", inline=False)
            embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
            embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
            await channel.send(embed=embed)
    else:
        await channel.send("City not found.")

@windsorWeatherReport.before_loop
async def before():
    await asyncio.sleep(50400)
    await client.wait_until_ready()
    print("Finished Waiting (weather)")

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

getMatchesLoop.start()
windsorWeatherReport.start()

client.run(os.environ['token'])
