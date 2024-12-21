#TODO go to hell command
""" TODO backup role command
TODO restor role command """


import discord
from discord.ext import commands, tasks
import re
import os
from unidecode import unidecode
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, UniqueConstraint
from sqlalchemy.sql import select
import feedparser

token = os.environ.get('DISCORD_TOKEN')
dbUsername = os.environ.get('DB_USERNAME')
dbPassword = os.environ.get('DB_PASSWORD')
dbIpPort = os.environ.get('DB_IP_PORT')
roleIgnored = os.environ.get('ROLE_IGNORED')  #role's id
channelMessage = os.environ.get('CHANNEL_MESSAGE')  #channel's id
dbName = os.environ.get('DB_NAME')
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='-r ', intents=intents)

metadata_obj = MetaData()
users = Table('users', metadata_obj,
     Column('id', Integer, primary_key=True),
     Column('name', String),
     Column('discord_id', String, unique=True),
)


roles = Table('roles', metadata_obj,
     Column('id', Integer, primary_key=True),
     Column('name', String),
     Column('discord_id', String, unique=True),
     Column('rating', Integer),
)

roleusers = Table('roleusers', metadata_obj,
     Column('id', Integer, primary_key=True),
     Column('role_id', ForeignKey("roles.id")),
     Column('user_id', ForeignKey("users.id")),
     UniqueConstraint('role_id', 'user_id', name='uniq_1')
)

primegames = Table('primegames', metadata_obj,
     Column('id', Integer, primary_key=True),
     Column('rss_id', String, unique=True),
)



engine = create_engine('postgresql://'+dbUsername+':'+dbPassword+'@'+dbIpPort+'/'+dbName)

metadata_obj.create_all(engine)

async def getUserByID(arg):
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
            user = await bot.fetch_user(user)
        except: 
            user = False

        if user:
            return user
        return False

def getUserByName(ctx, arg, strict=False):
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

async def getUser(ctx, arg, strict=False):
    if not arg:
        return False
    
    user = await getUserByID(arg)

    if user:
        return user

    user = getUserByName(ctx, arg, strict)
    return user

def isAdmin(member):
    return member.guild_permissions.administrator

async def getRoleByName(ctx, name):
    arg = unidecode(name).lower()
    for role in ctx.guild.roles:
        roleName = unidecode(role.name.lower())
        if arg == roleName:
            return role
    return False

def hasRole(member, name):
    return any(x for x in member.roles if x.name.lower() == name.lower())

def getMemberRole(role):
    s = select(roleusers, users).join(roles, roleusers.c.role_id == roles.c.id).join(users, roleusers.c.user_id == users.c.id).where(roles.c.discord_id == str(role.id))
    with engine.connect() as conn:
        result = conn.execute(s)
    return result

def getEmojiByName(name, strict=False):
    for emoji in bot.emojis:
        if not strict and name.lower() in emoji.name.lower() and len(name) > len(emoji.name)/2:
            return emoji
        elif strict and name.lower() == emoji.name.lower():
            return emoji
    return False

def userToDB(user):
    name = unidecode(user.name.lower())
    s = select(users).where(users.c.discord_id == str(user.id))
    with engine.connect() as conn:
        result = conn.execute(s)
    

    if(result.rowcount == 0):
        ins = users.insert().values(name=name, discord_id=str(user.id))
        with engine.connect() as conn:
                result = conn.execute(ins)
                conn.commit()
    else:
        return True

async def allUsersToDB(ctx):
    totUser = 0
    nbSaved = 0
    async for user in ctx.guild.fetch_members():
        totUser += 1
        if userToDB(user):
            nbSaved += 1
    return totUser == nbSaved

def roleToDb(role):
    name = unidecode(role.name.lower())
    s = select(roles).where(roles.c.discord_id == str(role.id))
    with engine.connect() as conn:
        result = conn.execute(s)
    if(result.rowcount == 0):
        ins = roles.insert().values(name=name, discord_id=role.id)
        with engine.connect() as conn:
                result = conn.execute(ins)
                conn.commit()
    else:
        return True


async def allRolesToDB(ctx):
    totRoles = 0
    nbSaved = 0
    roles = await ctx.guild.fetch_roles()
    for role in roles:
        totRoles += 1
        if roleToDb(role):
            nbSaved += 1
    return totRoles == nbSaved

async def getUnusedRoles(ctx):
    message = ""
    roles = await ctx.guild.fetch_roles()
    for role in roles:
        members = role.members
        if len(members) == 0:
            members = getMemberRole(role)
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

def roleUserToDB(user):
    totRoles = 0
    nbSaved = 0
    rolesUser = user.roles 
    userToDB(user)
    s = select(users).where(users.c.discord_id == str(user.id))
    with engine.connect() as conn:
        result = conn.execute(s)
    idUser = result.first().id
    for role in rolesUser:
        roleToDb(role)
        if totRoles > 0 and role.id != roleIgnored:
            s = select(roles).where(roles.c.discord_id == str(role.id))
            with engine.connect() as conn:
                result = conn.execute(s)
            idRole = result.first().id

            s = select(roleusers).where(roleusers.c.role_id == str(idRole), roleusers.c.user_id == str(idUser))
            with engine.connect() as conn:
                result = conn.execute(s)
            if result.rowcount == 0:
                ins = roleusers.insert().values(role_id=idRole, user_id=idUser)
                with engine.connect() as conn:
                    result = conn.execute(ins)
                    conn.commit()
                    if(result):
                        nbSaved += 1
            else:
                nbSaved += 1 
        else: 
            nbSaved += 1 
        totRoles += 1
    return totRoles == nbSaved


async def allRoleUserToDB(ctx):
    totUser = 0
    nbSaved = 0
    async for user in ctx.guild.fetch_members():
        totUser += 1
        if roleUserToDB(user):
            nbSaved += 1
    return totUser == nbSaved
        
async def restorRolesToUser(ctx, user):
    s = select(users).where(users.c.discord_id == str(user.id))
    with engine.connect() as conn:
        result = conn.execute(s)
    if result.rowcount == 0:
        return False
    idUser = result.first().id

    j = roleusers.join(roles, roleusers.c.role_id == roles.c.id)
    s = select(roleusers, roles).select_from(j).where(roleusers.c.user_id == idUser)
    with engine.connect() as conn:
        result = conn.execute(s)

    for row in result:
        if not hasRole(user, row.name):
            await user.add_roles(ctx.guild.get_role(int(row.discord_id)))
    return True


@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')

@bot.command()
async def dlanor(ctx):
        await ctx.channel.send('die the death sentence to death great equalizer is the death!')

@bot.command()
async def avatar(ctx, arg):
    if not arg:
        await ctx.channel.send("arg user missing")
        return False
    user = await getUser(ctx, arg)
    if not user:
        await ctx.channel.send('User not found')
        return False
    await ctx.channel.send(user.avatar_url_as(static_format='png'))
    return True
        

@bot.command()
async def diethedeath(ctx, arg):
    if not isAdmin(ctx.author):
        await ctx.channel.send('This command is reserved to the administrators')
        return False
    user = await getUser(ctx, arg, True)
    if not user:
        await ctx.channel.send('User not found. You must tag him or writes his complete pseudo')
        return False
    user = await ctx.guild.fetch_member(user.id)
    hell = await getRoleByName(ctx, "DIE THE DEATH ! SENTENCE TO DEATH ! GREAT EQUALIZER IS THE DEATH !!!!!!!!")
    if not hell:
        await ctx.channel.send('Role not found')
        return False
    if(hasRole(user, "DIE THE DEATH ! SENTENCE TO DEATH ! GREAT EQUALIZER IS THE DEATH !!!!!!!!")):
        await ctx.channel.send('The user has already been die the death')
        return False
    await user.add_roles(hell)
    await ctx.channel.send(str(getEmojiByName("dlanor", True)))
    await ctx.channel.send('```diff\n- Die the death sentence to death great equalizer is the death!\n```')

@bot.command()
async def pardondiethedeath(ctx, arg):
    if not isAdmin(ctx.author):
        await ctx.channel.send('This command is reserved to the administrators')
        return False
    user = await getUser(ctx, arg, True)
    if not user:
        await ctx.channel.send('User not found. You must tag him or writes his complete pseudo')
        return False
    user = await ctx.guild.fetch_member(user.id)
    hell = await getRoleByName(ctx, "DIE THE DEATH ! SENTENCE TO DEATH ! GREAT EQUALIZER IS THE DEATH !!!!!!!!")
    if not hell:
        await ctx.channel.send('Role not found')
        return False
    if not hasRole(user, "DIE THE DEATH ! SENTENCE TO DEATH ! GREAT EQUALIZER IS THE DEATH !!!!!!!!"):
        await ctx.channel.send('The user has not been die the death')
        return False
    await user.remove_roles(hell)
    await ctx.channel.send(str(getEmojiByName("beato2", True)))


@bot.command()
async def saveuser(ctx, arg):
    if not isAdmin(ctx.author):
        await ctx.channel.send('This command is reserved to the administrators')
        return False
    user = await getUser(ctx, arg, True)
    if not user:
        await ctx.channel.send('User not found. You must tag him or writes his complete pseudo')
        return False
    user = await ctx.guild.fetch_member(user.id)
    if userToDB(user):
        await ctx.channel.send('User saved')

@bot.command()
async def saverole(ctx, arg):
    if not isAdmin(ctx.author):
        await ctx.channel.send('This command is reserved to the administrators')
        return False
    role = await getRoleByName(ctx, arg)
    if not role:
        await ctx.channel.send('Role not found. You must write his complete pseudo')
        return False
    if await roleToDb(role):
        await ctx.channel.send('Role saved')


@bot.command()
async def saveallusers(ctx):
    if not isAdmin(ctx.author):
        await ctx.channel.send('This command is reserved to the administrators')
        return False
    if await allUsersToDB(ctx):
        await ctx.channel.send('All users have been saved')
    else:
        await ctx.channel.send('Some users were not saved')

@bot.command()
async def saveallroles(ctx):
    if not isAdmin(ctx.author):
        await ctx.channel.send('This command is reserved to the administrators')
        return False
    if await allRolesToDB(ctx):
        await ctx.channel.send('All roles have been saved')
    else:
        await ctx.channel.send('Some roles were not saved')

@bot.command()
async def listunusedroles(ctx):
    if not isAdmin(ctx.author):
        await ctx.channel.send('This command is reserved to the administrators')
        return False
    message = await getUnusedRoles(ctx)
    if message != '':
        await ctx.channel.send(message)
    else:
        await ctx.channel.send('All roles are used')
        

@bot.command()
async def saveroleuser(ctx, arg):
    if not isAdmin(ctx.author):
        await ctx.channel.send('This command is reserved to the administrators')
        return False
    user = await getUser(ctx, arg, True)
    if not user:
        await ctx.channel.send('User not found. You must tag him or writes his complete pseudo')
        return False
    user = await ctx.guild.fetch_member(user.id)
    if(roleUserToDB(user)):
        await ctx.channel.send('All roles for the user have been saved')
    else:
        await ctx.channel.send('Some roles for the user have not been saved')


@bot.command()
async def saveallroleusers(ctx):
    if not isAdmin(ctx.author):
        await ctx.channel.send('This command is reserved to the administrators')
        return False
    if await allRoleUserToDB(ctx):
        await ctx.channel.send('All roles for all users have been saved')
    else:
        await ctx.channel.send('Some roles for some users were not saved')


@bot.command()
async def restorerolesto(ctx, arg):
    if not isAdmin(ctx.author):
        await ctx.channel.send('This command is reserved to the administrators')
        return False
    user = await getUser(ctx, arg, True)
    if not user:
        await ctx.channel.send('User not found. You must tag him or writes his complete pseudo')
        return False
    user = await ctx.guild.fetch_member(user.id)
    if await restorRolesToUser(ctx, user):
        await ctx.channel.send('Roles of the user have been restored')

@bot.event
async def on_member_join(member):
    guild = member.guild
    channel = guild.get_channel(channelMessage)
    if await restorRolesToUser(member, member):
        await channel.send('Roles of '+member.display_name+' have been restored')

@bot.event
async def on_member_remove(member):
    guild = member.guild
    channel = guild.get_channel(channelMessage)
    if(roleUserToDB(member)):
        await channel.send('All roles for '+member.display_name+' have been saved')
    else:
        await channel.send('Some roles for '+member.display_name+' have not been saved')

@bot.command()
async def getfreeprimegames(ctx):
    feed = feedparser.parse("https://feed.phenx.de/lootscraper_amazon_game.xml")
    for entry in feed.entries:

        s = select(primegames).where(primegames.c.rss_id == str(entry.id))
        with engine.connect() as conn:
            result = conn.execute(s)
        if(result.rowcount > 0):
            return False

        dateValid = re.search(r'<li><b>Offer valid to:</b>.{19}</li>', entry.content[0].value)
        dateValid = dateValid[0]
        dateValid = dateValid[27:45]
        
        imgSrc = re.search(r'img src=\".{0,100}\"', entry.content[0].value)
        imgSrc = imgSrc[0]
        imgSrc = imgSrc[imgSrc.find("\"")+1:len(imgSrc)-1] 

        price = re.search(r'[0-9]{1,3}([,.][0-9]{1,2})? EUR', entry.content[0].value)
        if price:
            price = price[0].replace(" EUR", "€")
            price = "~~"+price+"~~ "
        else:
            price = ""

        title = entry.title.replace("Amazon Prime (Game) - ", "")

        embed = discord.Embed(title=title,
                      url=entry.link,
                      description=price + "**Gratuit** jusqu'au: " + dateValid)
        embed.set_image(url=imgSrc)

        primeFile = discord.File("/app/assets/images/prime-gaming.png", filename="prime-gaming.png")
        embed.set_thumbnail(url="attachment://prime-gaming.png")

        embed.add_field(name="",
                value="[**Ouvrir dans le navigateur ↗**]("+entry.link+")",
                inline=False)

        res = await ctx.channel.send(file=primeFile, embed=embed)
        if(res):
            ins = primegames.insert().values(rss_id=str(entry.id))
            with engine.connect() as conn:
                result = conn.execute(ins)
                conn.commit()
            
    return True

bot.run(token)