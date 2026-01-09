from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, UniqueConstraint, update
from sqlalchemy.sql import select
from env import DB_USERNAME,DB_PASSWORD,DB_IP_PORT,DB_NAME,ROLE_IGNORED
from unidecode import unidecode

class Database():
    def __init__(self):
        self.initDb()

    @property
    def engine(self):
        return self._engine
    
    @property
    def users(self):
        return self._users
    
    @property
    def roles(self):
        return self._roles
    
    @property
    def roleusers(self):
        return self._roleusers
    
    @property
    def primegames(self):
        return self._primegames

    def initDb(self):
        metadata_obj = MetaData()
        self._users = Table('users', metadata_obj,
                Column('id', Integer, primary_key=True),
                Column('name', String),
                Column('discord_id', String, unique=True),
        )

        self._roles = Table('roles', metadata_obj,
                Column('id', Integer, primary_key=True),
                Column('name', String),
                Column('discord_id', String, unique=True),
                Column('rating', Integer),
        )
        
        self._roleusers = Table('roleusers', metadata_obj,
                    Column('id', Integer, primary_key=True),
                    Column('role_id', ForeignKey("roles.id")),
                    Column('user_id', ForeignKey("users.id")),
                    UniqueConstraint('role_id', 'user_id', name='uniq_1')
        )

        self._primegames = Table('primegames', metadata_obj,
                    Column('id', Integer, primary_key=True),
                    Column('rss_id', String, unique=True),
        )

        self._engine = create_engine('postgresql://'+str(DB_USERNAME)+':'+str(DB_PASSWORD)+'@'+str(DB_IP_PORT)+'/'+str(DB_NAME))

        metadata_obj.create_all(self.engine)

    def getRolesByUserDiscordID(self, discordID):
        s = select(self.users).where(self.users.c.discord_id == str(discordID))
        with self.engine.connect() as conn:
            result = conn.execute(s)
        if result.rowcount == 0:
            return False
        if(first := result.first()) is None:
            return False
        idUser = first.id

        j = self.roleusers.join(self.roles, self.roleusers.c.role_id == self.roles.c.id)
        s = select(self.roleusers, self.roles).select_from(j).where(self.roleusers.c.user_id == idUser)
        with self.engine.connect() as conn:
            result = conn.execute(s)

        return result
    
    def getMemberRole(self, role):
        s = select(self.roleusers, self.users).join(self.roles, self.roleusers.c.role_id == self.roles.c.id).join(self.users, self.roleusers.c.user_id == self.users.c.id).where(self.roles.c.discord_id == str(role.id))
        with self.engine.connect() as conn:
            result = conn.execute(s)
        return result
    
    def getRoles(self):
        s = select(self.roles)
        with self.engine.connect() as conn:
            result = conn.execute(s)
        return result
    
    def userToDB(self, user):
        name = unidecode(user.name.lower())
        s = select(self.users).where(self.users.c.discord_id == str(user.id))
        with self.engine.connect() as conn:
            result = conn.execute(s)

        if(result.rowcount == 0):
            ins = self.users.insert().values(name=name, discord_id=str(user.id))
            with self.engine.connect() as conn:
                    result = conn.execute(ins)
                    conn.commit()
        else:
            return True
    
    def roleToDb(self, role):
        name = unidecode(role.name.lower())
        s = select(self.roles).where(self.roles.c.discord_id == str(role.id))
        with self.engine.connect() as conn:
            result = conn.execute(s)
        if(result.rowcount == 0):
            ins = self.roles.insert().values(name=name, discord_id=role.id)
            with self.engine.connect() as conn:
                    result = conn.execute(ins)
                    conn.commit()
        else:
            return True
        
    def roleUserToDB(self, user):
        totRoles = 0
        nbSaved = 0
        rolesUser = user.roles 
        self.userToDB(user)
        s = select(self.users).where(self.users.c.discord_id == str(user.id))
        with self.engine.connect() as conn:
            result = conn.execute(s)
        if(first := result.first()) is None:
            return nbSaved
        idUser = first.id
        for role in rolesUser:
            self.roleToDb(role)
            if totRoles > 0 and role.id != ROLE_IGNORED:
                s = select(self.roles).where(self.roles.c.discord_id == str(role.id))
                with self.engine.connect() as conn:
                    result = conn.execute(s)
                if(first := result.first()) is None:
                    return nbSaved
                idRole = first.id
                s = select(self.roleusers).where(self.roleusers.c.role_id == str(idRole), self.roleusers.c.user_id == str(idUser))
                with self.engine.connect() as conn:
                    result = conn.execute(s)
                if result.rowcount == 0:
                    ins = self.roleusers.insert().values(role_id=idRole, user_id=idUser)
                    with self.engine.connect() as conn:
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
    
    def isOldPrimeGame(self, entryID):
        s = select(self.primegames).where(self.primegames.c.rss_id == str(entryID))
        with self.engine.connect() as conn:
            result = conn.execute(s)
        if(result.rowcount > 0):
            return True
        return False
    
    def addPrimeGame(self, entryID):
        ins = self.primegames.insert().values(rss_id=str(entryID))
        with self.engine.connect() as conn:
            result = conn.execute(ins)
            conn.commit()
    