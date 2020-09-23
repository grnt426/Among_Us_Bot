import random
import logging
import asyncio

import discord


class Guild:

    def __init__(self, guild):
        self.guild = guild
        self.players = []
        self.imposters = []
        self.crewmates = []
        self.imposter_role = None
        self.crewmate_role = None
        self.among_us_role = None
        self.setup_done = False

    async def setup(self):
        if self.setup_done:
            return

        logging.info("\t\t==== Setting up {0} ====".format(self.guild.name))

        for r in self.guild.roles:
            if r.name == "Imposter":
                logging.info("Found Imposter role: {0} id: {1}".format(r, r.id) + str(r.id))
                self.imposter_role = r
            elif r.name == "Crewmate":
                logging.info("Found Crewmate role: {0} id: {1}".format(r, r.id) + str(r.id))
                self.crewmate_role = r
            elif r.name == "among us":
                logging.info("Found Among Us role: {0} id: {1}".format(r, r.id) + str(r.id))
                self.among_us_role = r

        if self.among_us_role is None:
            logging.error("No Among Us role to use, ignoring request")
            return

        # Create the roles if they don't exist
        if self.imposter_role is None:
            logging.info("Creating imposter role")
            self.imposter_role = await self.guild.create_role(name="Imposter", color=discord.colour.Color.dark_red())
        if self.crewmate_role is None:
            logging.info("Creating crewmate role")
            self.crewmate_role = await self.guild.create_role(name="Crewmate", color=discord.colour.Color.dark_blue())

        self.find_players()
        self.setup_done = True

    async def new_game(self):
        try:
            self.find_players()
            num_imposters = int(len(self.players) * 0.2)
            if num_imposters < 1:
                num_imposters = 1

            # reset the roles of the previous imposters
            if len(self.imposters) > 0:
                logging.info("Resetting roles of imposters from previous round")
                await asyncio.gather(*(m.add_roles(self.crewmate_role) for m in self.imposters))
                await asyncio.gather(*(m.remove_roles(self.imposter_role) for m in self.imposters))
            else:
                await asyncio.gather(*(m.add_roles(self.crewmate_role) for m in self.players))

            random.shuffle(self.players)
            self.imposters.clear()
            self.crewmates.clear()
            logging.info("Assigning imposter role to new imposters")
            await asyncio.gather(*(m.add_roles(self.imposter_role) for m in self.players[:num_imposters]))

            logging.info("Updating internal cache of imposters and crewmates")
            for m in self.players[:num_imposters]:
                self.imposters.append(m)
            for m in self.players[num_imposters:]:
                self.crewmates.append(m)
        except discord.HTTPException:
            logging.error("Failed to start a new game")

    def find_players(self):
        self.players.clear()
        self.crewmates.clear()
        self.imposters.clear()

        logging.info("Searching all {0} guild members for their roles".format(len(self.guild.members)))
        for m in self.guild.members:
            if self.among_us_role in m.roles:
                self.players.append(m)
            if self.crewmate_role in m.roles:
                self.crewmates.append(m)
            if self.imposter_role in m.roles:
                self.imposters.append(m)
        logging.info("{0} among us players processed".format(len(self.players)))