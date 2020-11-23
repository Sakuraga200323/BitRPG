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
from sub import box, calc

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

def my_round(val, digit=0):
    p = 10 ** digit
    return (val * p * 2 + 1) // 2 / p

pg = Postgres(dsn)

async def send_bord(client, user, ch):
    print("status:",user.name, user.id)
    if not user.id in box.players:
        return
    p_data = box.players[user.id]
    embed = discord.Embed(title = "Player Status Board")
    embed.add_field(name=f"Player", value=f"{p_data.user.mention})", inline = False)
    embed.add_field(name=f"Level", value=f"*{p_data.lv()} / {p_data.max_lv()}*")
    embed.add_field(name=f"HitPoint", value=f"*{p_data.now_hp} / {p_data.max_hp}*")
    embed.add_field(name=f"MagicPoint", value=f"*{p_data.now_mp} / {p_data.max_mp}*")
    embed.add_field(name=f"Strength", value=f"*{p_data.STR()}*\n`(+{p_data.str_p()})`")
    embed.add_field(name=f"Defense", value=f"*{p_data.DEFE()}*\n`(+{p_data.defe_p()})`")
    embed.add_field(name=f"Agility", value=f"*{p_data.AGI()}*\n`(+{p_data.agi_p()})`")
    embed.add_field(name=f"StatusPoint", value=f"*{p_data.now_stp()}*")
    def bar(x,y):
        return round(x/y*24)*"|"
    if not p_data.now_stp() <= 0:
        s = f"STR`：{bar(p_data.str_p(), p_data.STP())}`"
        d = f"DEF`：{bar(p_data.defe_p(), p_data.STP())}`"
        a = f"AGI`：{bar(p_data.agi_p(), p_data.STP())}`"
        r = f"REM`：{bar(p_data.now_stp(), p_data.STP())}`"
                    
        embed.add_field(name=f"StatusPointBalance (Sum:{p_data.now_stp})", value=f"{s}\n{d}\n{a}\n{r}", inline=False)
    embed.add_field(name = f"ExperiencePoint(Sum/Now/MoreToNextLv)", value=f"*{p_data.EXP()} / {p_data.now_exp} / {p_data.lv - p_data.now_exp})*\n`[{'|'*int((p_data.now_exp()/p_data.lv())*100) if p_data.now_exp() >= 0 else ' ': <10}]`")
    embed.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=embed)
