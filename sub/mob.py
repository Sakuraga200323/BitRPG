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
    elif lv % 100 == 0:
        rank = "Catastrophe"
        num = 2
        agi_num = -666
        import sub.SS_Mob
        name = random.choice(list(sub.SS_Mob.set.keys()))
        url = sub.SS_Mob.set[name]
    elif lv % 10 == 0:
        rank = "Elite"
        num = 1.5
        import sub.S_Mob
        name = random.choice(list(sub.S_Mob.set.keys()))
        url = sub.S_Mob.set[name]
    else:
        rank = "Normal"
        num = 1
        import sub.N_Mob
        name = random.choice(list(sub.N_Mob.set.keys()))
        url = sub.N_Mob.set[name]
    pg.execute(f"update mob_tb set name = '{name}',lv = {lv},max_hp = {100*(lv+1)*num},now_hp = {100*(lv+1)*num},str = {10*(lv+1)*num},def = {100*(lv+1)*num},agi = {100*(lv+1)*num*agi_num},img_url = '{url}';")
    embed = discord.Embed(
        title=f"<{rank}> {m_data['name']} appears !!",
        description=f"Lv:{m_data['lv']} HP:{m_data['max_hp']}",
        color=color
    )
    embed.set_image(url=m_data["img_url"])
    loop.create_tasks(client.get_channel(data['id']).send(embed = embed))
