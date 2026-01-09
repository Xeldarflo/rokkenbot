from discord.ext import commands, tasks
from env import CHANNEL_VNTL
import requests
import html
import re
import datetime
import pytz

time = datetime.time(hour=10, minute=0, tzinfo=pytz.timezone("Europe/Brussels"))

class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keyword = "Translation & Release Status Update/Discussion"
        self.url = "https://www.reddit.com/user/Humble_Informant6429.json"
        self.getvntlnewsloop.start()
    
    def cog_unload(self):
        self.getvntlnewsloop.cancel()
        return super().cog_unload()
    
    def getVNTLNews(self):
        r = requests.get(self.url)
        if r is None or r.status_code != 200:
            return None
        res = r.json()
        return res
    
    def getVNTLNewsAll(self):
        news = self.getVNTLNews()
        if news is None:
            return None
        for children in news["data"]["children"]:
            child = children["data"]
            if "title" in child and self.keyword in html.unescape(str(child["title"])):
                body = html.unescape(str(child["selftext"]))
                return body

    def getVNTLNewsSummary(self, body):
        if body is None:
            return None
        bodyLines = body.splitlines()
        summary = ""
        catNumContent = 0
        curCatTitle = ""
        for line in bodyLines:
            if re.search(r"\*{2}[^-].*\*{2}", line):
                curCatTitle = line
                catNumContent = 0
            if re.search(r"\*{2}\-{1}.*\*{2}", line):
                if catNumContent == 0:
                    summary+=curCatTitle
                    summary+="\n"
                summary+=line
                summary+="\n"
                catNumContent+=1
        return summary
    
    def getVNTLNewsAllAndSummary(self):
        body = self.getVNTLNewsAll()
        if body is None:
            return None
        summary = self.getVNTLNewsSummary(body)
        body = body + f"\n\n\n**LAST UPDATES**\n{summary}"
        return body
    
    @commands.command()
    async def getvntlnews(self, ctx):
        body = self.getVNTLNewsAllAndSummary()
        if not body:
            return None
        #channel = await self.bot.fetch_channel(CHANNEL_VNTL)
        #await self.bot.sendByBulk(channel, body)
        await self.bot.sendByBulk(ctx.channel, body)
        return body

    @tasks.loop(time=time)
    async def getvntlnewsloop(self):
        if datetime.datetime.today().weekday() != 1:
            return None
        body = self.getVNTLNewsAllAndSummary()
        if not body:
            return None
        channel = await self.bot.fetch_channel(CHANNEL_VNTL)
        await self.bot.sendByBulk(channel, body)
        return body
    
    @getvntlnewsloop.before_loop
    async def before_getvntlnewsloop(self):
        print('waiting...')
        await self.bot.wait_until_ready()

async def setup(bot) -> None:
    await bot.add_cog(Reddit(bot))