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



def divid(user, ch, result):
    loop = asyncio.get_event_loop()
    print("Point:" ,user.id)
    p_data = pg.fetchdict(f"select * from player_tb where id = {user.id};")[0]
    target = result.group(1)
    point = int(result.group(2))
    if target in ("str","STR"):
        target = "str"
    elif target in ("def","DEF"):
        target = "def"
    elif target in ("agi","AGI"):
        target = "agi"
    else:
        loop.create_task(ch.send(f"【警告】{target}はステータスの一覧にありません。`str`,`def`,`agi` の中から選んでください。"))
    if p_data["stp"] == 0:
        loop.create_task(ch.send(f"【報告】{p_data['name']}はポイントを所持していません。ポイントはLvUP毎に10獲得可能です。"))
        return
    elif p_data[8] < point:
        loop.create_task(ch.send(f"【警告】{p_data['name']}の所持ポイントを{point - p_data['stp']}超過しています。{p_data['stp']}以下にしてください。"))
        return
    p_data['stp'] -= point
    p_data[target] += point
    p_data[target + "_stp"] += point
    pg.execute(f"update player_tb set {target} =  {p_data[f'{target}']}, {target + '_stp'} = {p_data[target + "_stp"]} where id = {user.id};")

    loop.create_task(ch.send(f"【報告】{p_data['name']}の{target}を強化。強化量が+{p_data[target_num]}になりました。"))
