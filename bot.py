import discord
import random
import asyncio

client = discord.Client()


@client.event
async def on_ready():
    """
    When it first starts up and is ready to receive messages.
    """
    print('We have logged in as {0.user}'.format(client))
    print("Number of guilds in: " + str(len(client.guilds)))


@client.event
async def on_message(message):
    crewmate_role = imposter_role = among_us_role = None
    if message.author == client.user:
        return

    if message.content.startswith('who among us'):
        print("Starting a new round of Among Us in '" + message.channel.guild.name + "'")
        print("Channel from: " + str(message.channel))

        print("Members in channel: " + str(len(message.channel.members)))

        print("Roles in server: " + str(len(message.channel.guild.roles)))
        for r in message.channel.guild.roles:
            print(str(r))
            if r.name == "Imposter":
                print("Found Imposter role")
                imposter_role = r
            elif r.name == "Crewmate":
                print("Found Crewmate role")
                crewmate_role = r
            elif r.name == "among us":
                print("Found Among Us role")
                among_us_role = r

        if among_us_role is None:
            print("No Among Us role to use, ignoring request")
            return

        # Create the roles if they don't exist
        if imposter_role is None:
            print("Creating imposter role")
            color = discord.colour.Color.dark_red()
            imposter_role = await message.channel.guild.create_role(name="Imposter", color=color)
        if crewmate_role is None:
            print("Creating crewmate role")
            color = discord.colour.Color.dark_blue()
            crewmate_role = await message.channel.guild.create_role(name="Crewmate", color=color)

        # List of members who are playing Among Us
        members = []
        for m in message.channel.members:
            if m.bot:
                continue
            elif among_us_role in m.roles:
                members.append(m)

        # Don't start a game if too few people have this role.
        # if len(members) < 3:
        #     print("Too few people to start")
        #     await message.channel.send('There are too few for imposters to be Among Us...right?')
        #     return
        print("There are " + str(len(members)) + " playing")

        # For now, 20% of those with the role will be imposters, and at least one person will be an imposter
        imposters = int(len(members) * 0.2)
        if imposters < 1:
            imposters = 1
        print("There will be " + str(imposters) + " imposters")

        # Assign roles to members randomly
        random.shuffle(members)
        new_imposters = 0

        # remove_roles = []
        # for m in members:
        #     remove_roles.append(m.remove_roles(imposter_role, crewmate_role))
        res = await asyncio.gather(*(m.remove_roles(imposter_role, crewmate_role) for m in members))
        print(res)

        await asyncio.gather(*(m.add_roles(imposter_role) for m in members[:imposters]))
        print("Done assigning imposters")
        await asyncio.gather(*(m.add_roles(crewmate_role) for m in members[imposters:]))
        print("Done assigning crewmates")

        # for m in members:
        #     if new_imposters < imposters:
        #         print(m.display_name + " is an imposter")
        #         await m.add_roles(imposter_role)
        #         new_imposters += 1
        #     else:
        #         await m.add_roles(crewmate_role)
        #         print(m.display_name + " is a crewmate")
        print("Done assigning roles")
        await message.channel.send(
            "There are {0} crewmates and {1} imposters Among Us!".format(str(len(members) - imposters), str(imposters)))


# Blocking function call, nothing will run after this
token_file = open("bot_token.txt")
res = token_file.read()
print(res)
client.run(res)
