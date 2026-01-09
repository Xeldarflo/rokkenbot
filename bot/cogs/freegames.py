from discord.ext import tasks, commands
from env import CHANNEL_MESSAGE
import discord
import feedparser
import re

class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.primeGamesFeed = "https://feed.phenx.de/lootscraper_amazon_game.xml"
        self.getfreeprimegames.start()
    
    def cog_unload(self):
        self.getfreeprimegames.cancel()
        return super().cog_unload()
    
    @tasks.loop(hours=1)
    async def getfreeprimegames(self):
        feed = feedparser.parse(self.primeGamesFeed)
        feed.entries.reverse()
        for entry in feed.entries:

            if(self.bot.db.isOldPrimeGame(entry.id)):
                return False

            dateValid = re.search(r'<li><b>Offer valid to:</b> .{16}</li>', entry.content[0].value)
            if(dateValid):
                dateValid = dateValid[0]
                dateValid = dateValid[27:43]
            
            imgSrc = re.search(r'img src=\".{0,100}\"', entry.content[0].value)
            imgSrc = imgSrc[0]
            imgSrc = imgSrc[imgSrc.find("\"")+1:len(imgSrc)-1] 

            price = re.search(r'[0-9]{1,3}([,.][0-9]{1,2})? EUR', entry.content[0].value)
            if price:
                price = price[0].replace(" EUR", "€")
                price = "~~"+price+"~~ "
            else:
                price = ""

            priceDate = price
            if(dateValid):
                priceDate = price + "**Gratuit** jusqu'au: " + dateValid
            else:
                priceDate = price + "**Gratuit**"


            title = entry.title.replace("Amazon Prime (Game) - ", "")

            embed = discord.Embed(title=title,
                        url=entry.link,
                        description=priceDate)
            embed.set_image(url=imgSrc)

            embed.set_thumbnail(url="https://img.icons8.com/fluent/600/prime-gaming.png")

            embed.add_field(name="",
                    value="[**Ouvrir dans le navigateur ↗**]("+str(entry.link)+")",
                    inline=False)

            channel = await self.bot.fetch_channel(CHANNEL_MESSAGE)

            res = await channel.send(embed=embed)

            #channel = await self.bot.fetch_channel(1423030065901469747)

            #res = await channel.send(embed=embed)

            if(res):
                self.bot.db.addPrimeGame(entry.id)
                
        return True
    
    @getfreeprimegames.before_loop
    async def before_getfreeprimegames(self):
        print('waiting...')
        await self.bot.wait_until_ready()

async def setup(bot) -> None:
    await bot.add_cog(FreeGames(bot))