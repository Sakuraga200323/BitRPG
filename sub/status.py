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
    embed.add_field(name=f"Player", value=f"{p_data.user.mention})")
    embed.add_field(name=f"Level(Now/Limit)", value=f"*{p_data.lv()} / {p_data.max_lv()}*", inline=False)
    embed.add_field(name=f"HitPoint(Now/Max)", value=f"*{p_data.now_hp} / {p_data.max_hp}*")
    embed.add_field(name=f"MagicPoint(Now/Max)", value=f"*{p_data.now_mp} / {p_data.max_mp}*", inline=False)
    embed.add_field(name=f"Strength", value=f"*{p_data.STR()}*\n`(+{p_data.str_p()})`")
    embed.add_field(name=f"Defense", value=f"*{p_data.DEFE()}*\n`(+{p_data.defe_p()})`")
    embed.add_field(name=f"Agility", value=f"*{p_data.AGI()}*\n`(+{p_data.agi_p()})`")
    embed.add_field(name=f"StatusPoint", value=f"*{p_data.STP()}*")
    def bar(x,y):
        return round(x/y*24)*"|"
    if not p_data.STP() <= 0:
        s = f"STR`：{bar(p_data.str_p(), p_data.STP())}`"
        d = f"DEF`：{bar(p_data.defe_p(), p_data.STP())}`"
        a = f"AGI`：{bar(p_data.agi_p(), p_data.STP())}`"
        r = f"REM`：{bar(p_data.now_stp(), p_data.STP())}`"
                    
        embed.add_field(name=f"StatusPointBalance (Sum:{p_data.now_stp()})", value=f"{s}\n{d}\n{a}\n{r}", inline=False)
    embed.add_field(name = f"Experience", value=f"*{p_data.EXP()}*\n`({p_data.now_exp()} / {p_data.lv() - p_data.now_exp()})[{'|'*int((p_data.now_exp()/(p_data.lv()-1 if p_data.lv() > 1 else p_data.lv()))*10) if p_data.now_exp() >= 0 else ' ': <10}]`")
    embed.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=embed)




async def divid(client, user, ch, result):
    p_data = box.players[user.id]
    target = result.group(1)
    point = int(result.group(2))
    if not target in ("str","def","agi"):
        await ch.send(f"{target}は強化項目の一覧にありません。`str`,`def`,`agi` の中から選んでください。")
        return
    if p_data.now_stp() < point:
        await ch.send(f"{p_data.user.mention}の所持ポイントを{point - p_data.now_stp()}超過しています。{p_data.now_stp()}以下にしてください。")
        return
    result = p_data.share_stp(target, point)
    print("Point:" ,user.id)
    await ch.send(f"{p_data.user.mention}の{target}を{point}強化。強化量が+{result}になりました。")




ITEMS = ("HP回復薬","MP回復薬","ドーピング薬")
ITEMS2 = ("冒険者カード",)

async def kaihou_proc(client, ch, user):
    p_data = pg.fetchdict(f"SELECT * FROM player_tb where id = {user.id};")[0]
    item_num = pg.fetchdict(f"SELECT items->'魔石' as item_num FROM player_tb where id = {user.id};")[0]["item_num"]
    print(item_num)
    if item_num < 250:
        husoku = 250 - item_num 
        await ch.send(f"{p_data['name']}　は魔石を規定量所有していません。不足量{husoku}")
        return
    item_num -= 250
    while p_data["now_exp"] > p_data["lv"] and p_data["lv"] <= p_data["max_lv"]:
        p_data["now_exp"] -= p_data["lv"]
        p_data["lv"] += 1
        if p_data["lv"] % 10 == 0:
            p_data["stp"] += 50 
    pg.execute(f"update player_tb set lv = {p_data['lv']}, stp = {p_data['stp']}, now_exp = {p_data['now_exp']}, items = items::jsonb||json_build_object('魔石', {item_num})::jsonb, max_lv = {p_data['max_lv'] + 1000} where id = {user.id};")
    await ch.send(f"限界突破！！{p_data['name']}のレベル上限が{p_data['max_lv'] +1000}に上昇しました。")
