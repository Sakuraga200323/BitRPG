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


pg = Postgres(dsn)

async def send_bord(client, user, ch):
      p_data = pg.fetchdict(f"select * from player_tb where id = {user.id};")
      print(p_data)
      embed = discord.Embed(title = "Player Status Board")
      embed.add_field(name = f"Player", value = f"{p_data['name']}({user.mention})", inline = False)
      embed.add_field(name = f"Sex", value = f"{p_data['sex']}", inline = False)
      embed.add_field(name = f"Lv (Level)", value = f"*{p_data['lv']} / {p_data['max_lv']}*")
      embed.add_field(name = f"HP (HitPoint)", value = f"*{p_data['now_hp']} / {p_data['max_hp']}*")
      embed.add_field(name = f"MP (MagicPoint)", value = f"*{p_data['now_mp']} / {p_data['max_mp']}*")
      embed.add_field(name = f"STR (Strength)", value = f"*{p_data['str'] + p_data['str_p']}*\n`(+{p_data['str_p']})`")
      embed.add_field(name = f"DEF (Defense)", value = f"*{p_data['def'] + p_data['def_p']}*\n`(+{p_data['def_p']})`")
      embed.add_field(name = f"AGI (Agility)", value = f"*{p_data['agi'] + p_data['agir_p']}*\n`(+{p_data['agi_p']})`")
      embed.add_field(name = f"EXP (ExperiencePoint)", value = f"*{p_data['all_exp']}*\n`[次のレベルまで後{p_data['lv'] - p_data['now_exp']}]`")
      embed.add_field(name = f"STP (StatusPoint)", value = f"*{p_data['stp']}*\n")
      embed.set_thumbnail(url=m_author.avatar_url)
      await m_ch.send(embed = embed)
