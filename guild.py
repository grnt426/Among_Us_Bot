import random

import discord
import asyncio


class Guild:
    players = []
    imposters = []
    crewmates = []
    guild = None
    imposter_role = None
    crewmate_role = None
    among_us_role = None
    setup_done = False

    def __init__(self, guild):
        self.guild = guild

    async def setup(self):
        if self.setup_done:
            return

        print("\t\t==== Setting up: " + self.guild.name + " ====")

        for r in self.guild.roles:
            if r.name == "Imposter":
                print("Found Imposter role: " + str(r) + " id: " + str(r.id))
                self.imposter_role = r
            elif r.name == "Crewmate":
                print("Found Crewmate role: " + str(r) + " id: " + str(r.id))
                self.crewmate_role = r
            elif r.name == "among us":
                print("Found Among Us role: " + str(r) + " id: " + str(r.id))
                self.among_us_role = r

        if self.among_us_role is None:
            print("No Among Us role to use, ignoring request")
            return

        # Create the roles if they don't exist
        if self.imposter_role is None:
            print("Creating imposter role")
            self.imposter_role = await self.guild.create_role(name="Imposter", color=discord.colour.Color.dark_red())
        if self.crewmate_role is None:
            print("Creating crewmate role")
            self.crewmate_role = await self.guild.create_role(name="Crewmate", color=discord.colour.Color.dark_blue())

        self.find_players()
        self.setup_done = True

    async def new_game(self):
        self.find_players()
        num_imposters = int(len(self.players) * 0.2)
        if num_imposters < 1:
            num_imposters = 1

        # reset the roles of the previous imposters
        if len(self.imposters) > 0:
            await asyncio.gather(*(m.add_roles(self.crewmate_role) for m in self.imposters))
            await asyncio.gather(*(m.remove_roles(self.imposter_role) for m in self.imposters))
        else:
            await asyncio.gather(*(m.add_roles(self.crewmate_role) for m in self.players))

        random.shuffle(self.players)
        self.imposters.clear()
        self.crewmates.clear()
        await asyncio.gather(*(m.add_roles(self.imposter_role) for m in self.players[:num_imposters]))

        for m in self.players[:num_imposters]:
            self.imposters.append(m)
        for m in self.players[num_imposters:]:
            self.crewmates.append(m)

    def find_players(self):
        for m in self.guild.members:
            if self.among_us_role in m.roles and m not in self.players:
                self.players.append(m)

            if self.crewmate_role in m.roles and m not in self.crewmates:
                self.crewmates.append(m)
            if self.imposter_role in m.roles and m not in self.imposters:
                self.imposters.append(m)
