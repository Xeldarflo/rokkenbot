from env import TOKEN
from database.database import Database
from bot.discordBot import DiscordBot

db = Database()
bot = DiscordBot(db)
bot.run(str(TOKEN))