import asyncio
import logging
from timeit import default_timer as timer
import discord

import guild

logging.basicConfig(filename='bot.log', format='%(asctime)s [%(levelname)s] %(message)s',
                    filemode='w', level=logging.INFO)

client = discord.Client()
guilds = {}


@client.event
async def on_ready():
    """
    Called whenever it connects to Discord and has populated the internal cache
    """

    logging.info('We have logged in as {0.user}'.format(client))
    logging.info("Number of guilds in: {0} ".format(len(client.guilds)))
    for g in client.guilds:
        if g.id not in guilds:
            server = guild.Guild(g)
            logging.info(server)
            guilds[g.id] = server

    await asyncio.gather(*(guilds[i].setup() for i in guilds))
    logging.info("Initial loading complete")

    for s in guilds:
        logging.info("{0} players in {1}".format(len(guilds[s].players), s))


@client.event
async def on_message(message):

    await client.wait_until_ready()

    # don't want to trigger ourself by accident
    if message.author == client.user:
        return

    if message.content.startswith('who among us'):
        server = guilds[message.channel.guild.id]

        logging.info("Starting a new round of Among Us in '{0}'".format(message.channel.guild.name))
        logging.info("Channel from: '{0}'".format(message.channel))
        logging.info("Members in channel: {0}".format(len(message.channel.members)))

        start = timer()
        await server.new_game()
        logging.info("Game prepared in {0} milliseconds".format(int((timer() - start) * 1000)))

        logging.info("There are {0} players".format(len(server.players)))
        await message.channel.send(
            "There are {0} crewmates and {1} imposters Among Us!".format(len(server.crewmates),
                                                                         len(server.imposters)))


@client.event
async def on_guild_join(server):
    logging.info("Joined a new guild '{0}'".format(guild))
    g = guild.Guild(server)
    guilds[server.id] = g
    await g.setup()
    logging.info("Guild loaded and setup")

token_file = open("bot_token.txt")
res = token_file.read()
logging.info("Token file read, is empty? {0}".format(res.strip() is None))

# Blocking function call, nothing will run after this
client.run(res)
