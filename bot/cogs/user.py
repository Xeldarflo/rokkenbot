import re
from unidecode import unidecode
from discord.ext import commands

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def getUserByID(self, arg):
        arg = arg.strip()
        matches = re.search(r'<@&?!?(\d+)>', arg)

        if(matches):
            user = matches[0]
            user = user.replace('@', "")
            user = user.replace('<', "")
            user = user.replace('>', "")
            user = user.replace('&', "")
            user = user.replace('!', "")
            try:
                user = await self.bot.fetch_user(user)
            except: 
                user = False
            if user:
                return user
            return False
        
    def getUserByName(self, ctx, arg, strict=False):
        arg = unidecode(arg.lower())
        for u in ctx.guild.members:
            name = unidecode(u.name.lower())
            if not strict and arg in name and (len(arg) >= 4 or len(arg) == len(name)):
                return u
            if not strict and u.nick: 
                nick = unidecode(u.nick.lower())
                if arg in nick and (len(arg) >= 4 or len(arg) == len(nick)):
                    return u
            elif strict and arg == name:
                return u
        return False

    async def getUser(self, ctx, arg, strict=False):
        if not arg:
            return False
        
        user = await self.getUserByID(arg)

        if user:
            return user

        user = self.getUserByName(ctx, arg, strict)
        return user
    
    def userToDB(self, user):
        return self.bot.db.userToDB(user)
    
    async def allUsersToDB(self, ctx):
        totUser = 0
        nbSaved = 0
        async for user in ctx.guild.fetch_members():
            totUser += 1
            if self.userToDB(user):
                nbSaved += 1
        return totUser == nbSaved
    
    async def allRoleUserToDB(self, ctx):
        totUser = 0
        nbSaved = 0
        async for user in ctx.guild.fetch_members():
            totUser += 1
            if self.bot.db.roleUserToDB(user):
                nbSaved += 1
        return totUser == nbSaved
    
    @commands.command()
    async def avatar(self, ctx, arg):
        if not arg:
            await ctx.channel.send("arg user missing")
            return False
        user = await self.getUser(ctx, arg)
        if not user:
            await ctx.channel.send('User not found')
            return False
        await ctx.channel.send(user.avatar.replace(static_format='png'))
        return True
        
async def setup(bot) -> None:
    await bot.add_cog(User(bot))