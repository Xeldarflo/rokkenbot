from discord.ext import commands
from unidecode import unidecode
from env import CHANNEL_MESSAGE

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.getOtherCogs()

    def isAdmin(self, member):
        return member.guild_permissions.administrator
    
    def getOtherCogs(self):
        self.cogUser = self.bot.get_cog('User')
        self.cogRole = self.bot.get_cog('Role')
        self.cogGeneral = self.bot.get_cog('General')
     
    @commands.command()
    async def diethedeath(self, ctx, arg):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        user = await self.cogUser.getUser(ctx, arg, True)
        if not user:
            await ctx.channel.send('User not found. You must tag him or writes his complete pseudo')
            return False
        user = await ctx.guild.fetch_member(user.id)
        hell = await self.cogRole.getRoleByName(ctx, "DIE THE DEATH ! SENTENCE TO DEATH ! GREAT EQUALIZER IS THE DEATH !!!!!!!!")
        if not hell:
            await ctx.channel.send('Role not found')
            return False
        if(self.cogRole.hasRole(user, "DIE THE DEATH ! SENTENCE TO DEATH ! GREAT EQUALIZER IS THE DEATH !!!!!!!!")):
            await ctx.channel.send('The user has already been die the death')
            return False
        await user.add_roles(hell)
        await ctx.channel.send(str(self.cogGeneral.getEmojiByName("dlanor", True)))
        await ctx.channel.send('```diff\n- Die the death sentence to death great equalizer is the death!\n```')

    @commands.command()
    async def pardondiethedeath(self, ctx, arg):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        user = await self.cogUser.getUser(ctx, arg, True)
        if not user:
            await ctx.channel.send('User not found. You must tag him or writes his complete pseudo')
            return False
        user = await ctx.guild.fetch_member(user.id)
        hell = await self.cogRole.getRoleByName(ctx, "DIE THE DEATH ! SENTENCE TO DEATH ! GREAT EQUALIZER IS THE DEATH !!!!!!!!")
        if not hell:
            await ctx.channel.send('Role not found')
            return False
        if not self.cogRole.hasRole(user, "DIE THE DEATH ! SENTENCE TO DEATH ! GREAT EQUALIZER IS THE DEATH !!!!!!!!"):
            await ctx.channel.send('The user has not been die the death')
            return False
        await user.remove_roles(hell)
        await ctx.channel.send(str(self.cogGeneral.getEmojiByName("beato2", True)))
    
    @commands.command()
    async def saveuser(self, ctx, arg):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        user = await self.cogUser.getUser(ctx, arg, True)
        if not user:
            await ctx.channel.send('User not found. You must tag him or writes his complete pseudo')
            return False
        user = await ctx.guild.fetch_member(user.id)
        if self.cogUser.userToDB(user):
            await ctx.channel.send('User saved')

    @commands.command()
    async def saverole(self, ctx, arg):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        role = await self.cogRole.getRoleByName(ctx, arg)
        if not role:
            await ctx.channel.send('Role not found. You must write his complete pseudo')
            return False
        if await self.cogRole.roleToDb(role):
            await ctx.channel.send('Role saved')

    @commands.command()
    async def saveallusers(self, ctx):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        if await self.cogUser.allUsersToDB(ctx):
            await ctx.channel.send('All users have been saved')
        else:
            await ctx.channel.send('Some users were not saved')

    @commands.command()
    async def saveallroles(self, ctx):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        if await self.cogRole.allRolesToDB(ctx):
            await ctx.channel.send('All roles have been saved')
        else:
            await ctx.channel.send('Some roles were not saved')

    @commands.command()
    async def listunusedroles(self, ctx):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        message = await self.cogRole.getUnusedRoles(ctx)
        if message != '':
            await ctx.channel.send(message)
        else:
            await ctx.channel.send('All roles are used')

    @commands.command()
    async def saveroleuser(self, ctx, arg):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        user = await self.cogUser.getUser(ctx, arg, True)
        if not user:
            await ctx.channel.send('User not found. You must tag him or writes his complete pseudo')
            return False
        user = await ctx.guild.fetch_member(user.id)
        if(self.bot.db.roleUserToDB(user)):
            await ctx.channel.send('All roles for the user have been saved')
        else:
            await ctx.channel.send('Some roles for the user have not been saved')

    @commands.command()
    async def saveallroleusers(self, ctx):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        if await self.cogUser.allRoleUserToDB(ctx):
            await ctx.channel.send('All roles for all users have been saved')
        else:
            await ctx.channel.send('Some roles for some users were not saved')

    @commands.command()
    async def restorerolesto(self, ctx, arg):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        user = await self.cogUser.getUser(ctx, arg, True)
        if not user:
            await ctx.channel.send('User not found. You must tag him or writes his complete pseudo')
            return False
        user = await ctx.guild.fetch_member(user.id)
        try:
            if await self.cogRole.restorRolesToUser(ctx, user):
                await ctx.channel.send('Roles of the user have been restored')
        except:
            await ctx.channel.send('Roles of the user have **not** been restored')

    @commands.command()
    async def restoreallrolesusers(self, ctx):
        self.getOtherCogs()
        if not self.isAdmin(ctx.author):
            await ctx.channel.send('This command is reserved to the administrators')
            return False
        async for user in ctx.guild.fetch_members():
            try:
                if await self.cogRole.restorRolesToUser(ctx, user):
                    await ctx.channel.send('Roles of the user '+user.display_name+' have been restored')
            except:
                await ctx.channel.send('Roles of the user '+user.display_name+' have **not** been restored')
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.getOtherCogs()
        guild = member.guild
        channel = await self.bot.fetch_channel(CHANNEL_MESSAGE)
        if await self.cogRole.restorRolesToUser(member, member):
            await channel.send('Roles of '+member.display_name+' have been restored')
        else:
            await channel.send('Roles of '+member.display_name+' have **not** been restored')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        channel = await self.bot.fetch_channel(CHANNEL_MESSAGE)
        if(self.bot.db.roleUserToDB(member)):
            await channel.send('All roles for '+member.display_name+' have been saved')
        else:
            await channel.send('Some roles for '+member.display_name+' have not been saved')

async def setup(bot) -> None:
    await bot.add_cog(Moderation(bot))