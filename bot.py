import discord
import asyncio
from timeit import default_timer as timer

import guild

client = discord.Client()
guilds = {}


@client.event
async def on_ready():
    """
    Called whenever it connects to Discord and has populated the internal cache
    """

    print('We have logged in as {0.user}'.format(client))
    print("Number of guilds in: " + str(len(client.guilds)))
    for g in client.guilds:
        if g.id not in guilds:
            server = guild.Guild(g)
            guilds[g.id] = server

    await asyncio.gather(*(guilds[i].setup() for i in guilds))
    print("Initial loading complete")


@client.event
async def on_message(message):

    await client.wait_until_ready()

    # don't want to trigger ourself by accident
    if message.author == client.user:
        return

    if message.content.startswith('who among us'):
        server = guilds[message.channel.guild.id]

        print("Starting a new round of Among Us in '" + message.channel.guild.name + "'")
        print("Channel from: " + str(message.channel))
        print("Members in channel: " + str(len(message.channel.members)))

        start = timer()
        await server.new_game()
        print("Game prepared in: " + str(int((timer() - start) * 1000)) + " milliseconds")

        print("There are " + str(len(server.players)) + " playing")
        await message.channel.send(
            "There are {0} crewmates and {1} imposters Among Us!".format(str(len(server.crewmates)),
                                                                         str(len(server.imposters))))


@client.event
async def on_guild_join(server):
    print("Joined a new guild: " + str(guild))
    g = guild.Guild(server)
    guilds[server.id] = g
    await g.setup()
    print("Guild loaded and setup")

token_file = open("bot_token.txt")
res = token_file.read()

# Blocking function call, nothing will run after this
client.run(res)
