import discord
import os
import pathlib
from env import COMMAND_PREFIX
from discord.ext import commands
from unidecode import unidecode

intents = discord.Intents().all()

class DiscordBot(commands.Bot):
    def __init__(self, db):
        self._db = db
        print("test")
        super().__init__(
            command_prefix=commands.when_mentioned_or(str("-r ")),
            intents=intents,
            help_command=None,
        )

    @property
    def db(self):
        return self._db
    
    async def load_cogs(self):
        fileName = ""
        for file in os.listdir(f"{pathlib.Path(__file__).parent.resolve()}/cogs"):
            if file.endswith(".py"):
                fileName = file[:-3]
                await self.load_extension(f"bot.cogs.{fileName}")

    async def setup_hook(self):
        await self.load_cogs()
    
    
    async def allRolesToDB(self, ctx):
        totRoles = 0
        nbSaved = 0
        roles = await ctx.guild.fetch_roles()
        for role in roles:
            totRoles += 1
            if self.db.roleToDb(role):
                nbSaved += 1
        return totRoles == nbSaved
    
    async def sendByBulk(self, channel, message):
        body = message.splitlines()
        limits = 1750
        toSend = ""
        for line in body:
            toSend += line + "\n"
            if(len(toSend) >= limits):
                messageSended = await channel.send(toSend)
                toSend = ""
                if messageSended:
                    await messageSended.edit(suppress=True)
        if len(toSend) > 0:
            messageSended = await channel.send(toSend)
            if messageSended:
                await messageSended.edit(suppress=True)
        return message
                