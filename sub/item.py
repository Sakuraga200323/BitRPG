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

ITEMS = ["HP回復薬","MP回復薬","ドーピング薬",""]

pg = Postgres(dsn)

loop = asyncio.get_event_loop()

def open(client, ch, user):
    items_dtd = pg.fetchdict("select items from player_tb;")[0][0][1]
    text = ""
    for item, num in zip(items_dtd.keys(), items_dtd.items()):
        text += f"{item}(`{num}`)\n"
    embed = discord.Embed(
        title="Player Inventory Bord",
        description=f"**{text}**"
    )
    loop.create_task(ch.send(embed=embed))

def use(client, ch, user, item):
    if not item in ITEMS:
        loop.create_task(ch.send(f"{item}と言うアイテムは存在しません。"))
        return
    p_data = pg.fetchdict(f"SELECT * FROM player_tb;")[0]
    item_num = pg.fetchdict(f"SELECT items->'{item}' FROM player_tb;")[0]
    if items_num <= 0:
        loop.create_task(ch.send(f"{p_data['name']}　は{item}を所有していません。"))
        return
    item_num -= 1
    pg.execute("update player_tb set items = items::jsonb||json_build_object('{item}', {item_num})::jsonb;")

    if item == "HP回復薬":
        if p_data["max_hp"] > p_data["now_hp"]:
            before_hp = p_data["now_hp"]
            p_data["now_hp"] += int(p_data["max_hp"]*0.25)
            if p_data["now_hp"] > p_data["max_hp"]:
                p_data["now_hp"] = p_data["max_hp"]
            cured_hp = p_data["now_hp"] - before_hp
            pg.execute(f"update player_tb set now_hp = {p_data['now_hp']};")
            loop.create_task(ch.send(f"HP回復薬を使用し、{p_data['name']}　のHPが{cured_hp}回復した！"))
        else:
            loop.create_task(ch.send(f"HP回復薬を使用したが、{p_data['name']}　のHPは満タンだった。"))
            
    if item == "MP回復薬":
        pass

    if item == "ドーピング薬":
        pass
