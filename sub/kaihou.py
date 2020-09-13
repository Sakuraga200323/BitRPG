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

standard_set = "name,sex,id,lv,max_hp,now_hp,max_mp,now_mp,str,def,agi,stp,str_stp, def_stp, agi_stp,all_exp,now_exp,money"
standard_mobset = "name,id,lv,max_hp,now_hp,str,def,agi,img_url"

token = os.environ.get('TOKEN')
client = discord.Client()

admin_list = [
    715192735128092713,
    710207828303937626,
    548058577848238080,
]




getmagic_list = [
    "001|Heal",
    "002|FireBall",
    "003|StrRein",
    "004|DefRein",
    "005|AgiRein",
    "006|LifeConversion"


]

loop = asyncio.get_event_loop()
pg = Postgres(dsn)

ITEMS = ("HP回復薬","MP回復薬","ドーピング薬")
ITEMS2 = ("冒険者カード",)

async def kaihou_proc(client, ch, user):
    p_data = pg.fetchdict(f"SELECT * FROM player_tb where id = {user.id};")[0]
    item_num = pg.fetchdict(f"SELECT items->'魔石' as item_num FROM player_tb;")[0]["item_num"]
    print(item_num)
    if item_num <= 500:
        husoku = 500 - item_num 
        await ch.send(f"{p_data['name']}　は魔石を規定量所有していません。不足量{husoku}")
        return
    item_num -= 500
    while p_data["now_exp"] > p_data["lv"] and p_data["lv"] <= p_data["max_lv"]:
        p_data["now_exp"] -= p_data["lv"]
        p_data["lv"] += 1
        if i_data["lv"] % 10 == 0:
            i_data["stp"] += 50 
    pg.execute(f"update player_tb set lv = {p_data['lv']}, stp = {p_data['stp']}, now_exp = {p_data['now_exp']}, items = items::jsonb||json_build_object('{item}', {item_num})::jsonb, max_lv += 1000 where id = {user.id};")
    await ch.send(f"限界突破！！{p_data['name']}のレベル上限が{p_data['max_lv']}に上昇しました。")
