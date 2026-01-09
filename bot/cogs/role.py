from discord.ext import commands
from unidecode import unidecode

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def hasRole(self, member, name):
        return any(x for x in member.roles if x.name.lower() == name.lower())

    async def getRoleByName(self, ctx, name):
        arg = unidecode(name).lower()
        for role in ctx.guild.roles:
            roleName = unidecode(role.name.lower())
            if arg == roleName:
                return role
        return False
    
    async def getUnusedRoles(self, ctx):
        message = ""
        roles = await ctx.guild.fetch_roles()
        for role in roles:
            members = role.members
            if len(members) == 0:
                members = self.bot.db.getMemberRole(role)
                message += "- " + str(role.name)
                if members.rowcount > 0:
                    message += " | previously used by: "
                    i = 0
                    for res in members:
                        if i > 0:
                            message += ", "
                        message += res.name
                        i = i +1
                message += "\n"
        return message
    
    def roleToDb(self, role):
        return self.bot.db.roleToDb(role)
    
    async def allRolesToDB(self, ctx):
        totRoles = 0
        nbSaved = 0
        roles = await ctx.guild.fetch_roles()
        for role in roles:
            totRoles += 1
            if self.roleToDb(role):
                nbSaved += 1
        return totRoles == nbSaved
    
    async def restorRolesToUser(self, ctx, user):
        roles = self.bot.db.getRolesByUserDiscordID(user.id)

        for role in roles:
            if not ctx.guild.get_role(int(role.discord_id)):
                continue
            try:
                if not self.hasRole(user, role.name):
                    await user.add_roles(ctx.guild.get_role(int(role.discord_id)))
            except:
                return False
        return True
    
async def setup(bot) -> None:
    await bot.add_cog(Role(bot))