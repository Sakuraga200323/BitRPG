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
    embed.add_field(name = f"Player", value = f"{p_data.user.mention})", inline = False)
    embed.add_field(name = f"Lv (Level)", value = f"*{p_data.lv} / {p_data.max_lv}*")
    embed.add_field(name = f"HP (HitPoint)", value = f"*{p_data.now_hp} / {p_data.max_hp}*")
    embed.add_field(name = f"MP (MagicPoint)", value = f"*{p_data.now_mp} / {p_data.max_mp}*")
    embed.add_field(name = f"STR (Strength)", value = f"*{p_data.STR}*\n`(+{p_data.str_p})`")
    embed.add_field(name = f"DEF (Defense)", value = f"*{p_data.DEFE}*\n`(+{p_data.defe_p})`")
    embed.add_field(name = f"AGI (Agility)", value = f"*{p_data.AGI}*\n`(+{p_data.agi_p})`")
    embed.add_field(name = f"STP (StatusPoint)", value = f"*{p_data.now_stp}*")
    def bar(x,y):
        return round(x/y*32)*"|"
    if not p_data.all_stp <= 0:
        s = f"`STR：{bar(p_data.str_p, p_data.all_stp)}`"
        d = f"`DEF：{bar(p_data.defe_p, p_data.all_stp)}`"
        a = f"`AGI：{bar(p_data.agi_p, p_data.all_stp)}`"
        r = f"`REM：{bar(p_data.all_stp, p_data.all_stp)}`"
                    
        embed.add_field(name = f"STP Balance (STP Only, Sum:{p_data.all_stp})", value = f"{s}\n{d}\n{a}\n{r}", inline = False)
    embed.add_field(name = f"EXP (ExperiencePoint)", value = f"*{p_data.all_exp}*\n`[{'|'*int((self.now_exp/self.lv)*100) if self.now_exp >= 0 else ' ': <10}]`")
    embed.set_thumbnail(url=user.avatar_url)
    await ch.send(embed = embed)
