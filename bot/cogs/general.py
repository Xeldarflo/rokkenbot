from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def getEmojiByName(self, name, strict=False):
        for emoji in self.bot.emojis:
            if not strict and name.lower() in emoji.name.lower() and len(name) > len(emoji.name)/2:
                return emoji
            elif strict and name.lower() == emoji.name.lower():
                return emoji
        return False
    
    @commands.command()
    async def dlanor(self, ctx):
        await ctx.channel.send('die the death sentence to death great equalizer is the death!')

async def setup(bot) -> None:
    await bot.add_cog(General(bot))