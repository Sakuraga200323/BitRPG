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
import sub.box
import sub.calc

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
    p_data = pg.fetchdict(f"select * from player_tb where id = {user.id};")[0]
    all_stp = p_data['str_stp'] + p_data['def_stp']+ p_data['agi_stp'] + p_data['stp']; print(all_stp)
    embed = discord.Embed(title = "Player Status Board")
    embed.add_field(name = f"Player", value = f"{p_data['name']}({user.mention})", inline = False)
    embed.add_field(name = f"Sex", value = f"{p_data['sex']}", inline = False)
    embed.add_field(name = f"Lv (Level)", value = f"*{p_data['lv']} / {p_data['max_lv']}*")
    embed.add_field(name = f"HP (HitPoint)", value = f"*{p_data['now_hp']} / {p_data['max_hp']}*")
    embed.add_field(name = f"MP (MagicPoint)", value = f"*{p_data['now_mp']} / {p_data['max_mp']}*")
    embed.add_field(name = f"STR (Strength)", value = f"*{p_data['str'] + p_data['str_stp']}*\n`(+{p_data['str_stp']})`")
    embed.add_field(name = f"DEF (Defense)", value = f"*{p_data['def'] + p_data['def_stp']}*\n`(+{p_data['def_stp']})`")
    embed.add_field(name = f"AGI (Agility)", value = f"*{p_data['agi'] + p_data['agi_stp']}*\n`(+{p_data['agi_stp']})`")
    embed.add_field(name = f"STP (StatusPoint)", value = f"*{p_data['stp']}*\n")
    def bar(x,y):
        return round(x/y*100)*"■"
    s = f"*STR*：`{bar(p_data['str_stp'], all_stp)}`"
    d = f"*DEF*：`{bar(p_data['def_stp'], all_stp)}`"
    a = f"*AGI*：`{bar(p_data['agi_stp'], all_stp)}`"
    n = f"*REM*：`{bar(p_data['stp'], all_stp)}`"
    embed.add_field(name = f"STPBalance (Max■×100, STPOnly)", value = f"{s}\n{d}\n{a}\n{n}")
    embed.add_field(name = f"EXP (ExperiencePoint)", value = f"*{p_data['all_exp']}*\n`[次のレベルまで後{p_data['lv'] - p_data['now_exp']}]`")
    embed.set_thumbnail(url=user.avatar_url)
    await ch.send(embed = embed)
