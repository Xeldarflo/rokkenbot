import os

TOKEN = os.environ.get('DISCORD_TOKEN')
DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_IP_PORT = os.environ.get('DB_IP_PORT')
ROLE_IGNORED = os.environ.get('ROLE_IGNORED')  #role's id
CHANNEL_MESSAGE = os.environ.get('CHANNEL_MESSAGE')  #channel's id
CHANNEL_VNTL = os.environ.get('CHANNEL_VNTL')
DB_NAME = os.environ.get('DB_NAME')
COMMAND_PREFIX = os.environ.get('COMMAND_PREFIX')