import math
import ast
import asyncio
from datetime import datetime, timedelta, timezone
import discord
from discord.ext import tasks
import glob
import os
import psutil
import psycopg2
import psycopg2.extras
import random
import re
import traceback
import sub.box, sub.calc

JST = timezone(timedelta(hours=+9), 'JST')

dsn = os.environ.get('DATABASE_URL')

class Postgres:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def execute(self, sql):
        self.cur.execute(sql)

    def fetch(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    def fetchdict(self, sql):
        self.cur.execute (sql)
        results = self.cur.fetchall()
        dict_result = []
        for row in results:
            dict_result.append(dict(row))
        return dict_result

standard_set = "name,sex,id,lv,max_hp,now_hp,max_mp,now_mp,str,def,agi,stp,str_stp, def_stp, agi_stp,all_exp,now_exp,money"
standard_mobset = "name,id,lv,max_hp,now_hp,str,def,agi,img_url"

token = os.environ.get('TOKEN')
client = discord.Client()

admin_list = [
    715192735128092713,
    710207828303937626,
    548058577848238080,
]

def appear(m_data):
    import sub.box,sub.calc
    pg = Postgres(dsn)
    loop = asyncio.get_event_loop()
    agi_num = 1
    lv = m_data["lv"]       
    if lv % 1000 == 0:
        rank = "WorldEnd"
        num = 5
        agi_num = -666
        name = "?????"
        url = "None"
        color = discord.Color.from_rgb(0,0,0)
    elif lv % 100 == 0:
        rank = "Catastrophe"
        num = 2
        agi_num = -666
        import sub.SS_Mob
        name = random.choice(list(sub.SS_Mob.set.keys()))
        url = sub.SS_Mob.set[name]
        color = discord.Color.red()
    elif lv % 10 == 0:
        rank = "Elite"
        num = 1.5
        import sub.S_Mob
        name = random.choice(list(sub.S_Mob.set.keys()))
        url = sub.S_Mob.set[name]
        color = discord.Color.from_rgb(255,255,0)
    else:
        rank = "Normal"
        num = 1
        import sub.N_Mob
        name = random.choice(list(sub.N_Mob.set.keys()))
        url = sub.N_Mob.set[name]
        color = discord.Color.green()
    if random.randint(0,1000) == 777:
        rank = "UltraRare"
        num = 1
        name = "古月"
        url = "https://media.discordapp.net/attachments/719489738939301938/750412647203209266/download20200903025142.png?width=585&height=585"
        color = discord.Color.from_rgb(227,170,0)
        print("古月出現")
    pg.execute(f"update mob_tb set name = '{name}',lv = {lv},max_hp = {11*(lv+1)*num},now_hp = {11*(lv+1)*num},str = {10*(lv+1)*num},def = {10*(lv+1)*num},agi = {10*(lv+1)*num*agi_num},img_url = '{url}', rank = '{rank}' where id = {m_data['id']};")
    m_data = pg.fetchdict(f"select * from mob_tb where id = {m_data['id']};")[0]
    embed = discord.Embed(
        title=f"<{rank}> {m_data['name']} appears !!",
        description=f"Lv:{m_data['lv']} HP:{m_data['max_hp']}",
        color=color
    )
    if url != "None":
        embed.set_image(url=url)
    return embed
