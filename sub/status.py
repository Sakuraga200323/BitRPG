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

async def open_status(client, user, ch):
    if not user.id in box.players:
        return
    p_data = box.players[user.id]
    mc = p_data.magic_class_
    embed = discord.Embed(
        title="Player Status Board",
        color=0xe1ff00 if mc == 1 else 0x8f6200 if mc == 2 else 0x2e3cff
    )
    embed.add_field(name=f"Player", value=f"{p_data.user.mention})")
    embed.add_field(name=f"Level (Now/Limit)", value=f"*{p_data.lv()} / {p_data.max_lv()}*", inline=False)
    embed.add_field(name=f"HitPoint (Now/Max)", value=f"*{p_data.now_hp} / {p_data.max_hp}*")
    embed.add_field(name=f"MagicPoint (Now/Max)", value=f"*{p_data.now_mp} / {p_data.max_mp}*", inline=False)
    embed.add_field(name=f"Strength", value=f"*{p_data.STR()}* (+{p_data.str_p()})")
    embed.add_field(name=f"Defense", value=f"*{p_data.DEFE()}* (+{p_data.defe_p()})")
    embed.add_field(name=f"Agility", value=f"*{p_data.AGI()}* (+{p_data.agi_p()})")
    embed.add_field(name=f"StatusPoint", value=f"*{p_data.now_stp()}*")
    guage_edge_reft = "<:_end:784330415624290306>"
    guage_edge_right = "<:end_:784330344748417024>"
    def gauge(x,y):
        return round(x/y*15)*"━"
    if not p_data.STP() <= 0:
        all_stp = p_data.STP() - p_data.now_stp()
        s = f"{gauge(p_data.str_p(), all_stp)}"
        d = f"{gauge(p_data.defe_p(), all_stp)}"
        a = f"{gauge(p_data.agi_p(), all_stp)}"
        embed.add_field(name=f"BuildUpBalance (STR⧰DEF⧰AGI)", value=f"{p_data.STP()}\n{guage_edge_reft}`{s}⧱{d}⧱{a}`{guage_edge_right}", inline=False)
    have_exp = p_data.now_exp()
    must_exp = p_data.lv() + 1
    exp_gauge_num = int((have_exp / must_exp)*10)
    exp_gauge_1 = '<:1_:784323561052569642>'*exp_gauge_num
    exp_gauge_0 = (10 - exp_gauge_num) * '<:0_:784323507110150144>'
    print(exp_gauge_num)
    embed.add_field(name = f"Experience", value=(
          f"*{p_data.max_exp()}*"
        + f"\n{guage_edge_reft}{exp_gauge_1 + exp_gauge_0}{guage_edge_right}"
        + f"\n`({p_data.now_exp()} / {p_data.lv()+1})`"))
    embed.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=embed)
    log_ch = client.get_channel(766997493195210774)
    await log_ch.send(embed=embed)




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

async def up_max_lv(client, ch, user):
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


                  





ITEMS = (
    "HP回復薬",
    "MP回復薬",
    "ドーピング薬",
    "魔石")

ITEMS2 = ("冒険者カード",)

ITEMS_IMG_URL = {
    "HP回復薬":"https://media.discordapp.net/attachments/719855399733428244/757449313516519544/hp_cure_potion.png",
    "MP回復薬":"https://media.discordapp.net/attachments/719855399733428244/757449147321417779/mp_cure_potion.png",
    "ドーピング薬":"https://media.discordapp.net/attachments/719855399733428244/757464460792168618/doping_potion.png",
    "魔石":"https://media.discordapp.net/attachments/719855399733428244/757449362652790885/maseki.png"}

async def open_inventory(client, ch, user):
    items_dtd = pg.fetchdict(f"select items from player_tb where id = {user.id};")[0]["item"]
    text = ""
    for item, num in items_dtd.items():
        text += f"{item}：`{num}`\n"
    embed = discord.Embed(
        title="Player Inventory Bord",
        description=f"**{text}**"
    )
    await ch.send(embed=embed)

async def use_item(client, ch, user, item):
    if not item in ITEMS+ITEMS2:
        await ch.send(f"{item}と言うアイテムは存在しません。")
        return
    p_data = pg.fetchdict(f"SELECT * FROM player_tb where id = {user.id};")[0]
    item_num = pg.fetchdict(f"SELECT items->'{item}' as item_num FROM player_tb where id = {user.id};")[0]["item_num"]
    print(item_num)
    if item_num <= 0:
        await ch.send(f"{p_data['name']}　は{item}を所有していません。")
        return
    if not item in ITEMS2:
        item_num -= 1
        pg.execute(f"update player_tb set items = items::jsonb||json_build_object('{item}', {item_num})::jsonb where id = {user.id};")
                      
    item_logem = None

    if item == "HP回復薬":
        print("HP回復薬:",p_data["now_hp"], "/", p_data["max_hp"])
        if p_data["max_hp"] > p_data["now_hp"]:
            before_hp = p_data["now_hp"]
            p_data["now_hp"] += int(p_data["max_hp"]*0.25)
            if p_data["now_hp"] > p_data["max_hp"]:
                p_data["now_hp"] = p_data["max_hp"]
            cured_hp = p_data["now_hp"] - before_hp
            pg.execute(f"update player_tb set now_hp = {p_data['now_hp']} where id = {user.id};")
            item_logem = discord.Embed(description=f"HP回復薬を使用し、{p_data['name']} のHPが{cured_hp}回復した！")
        else:
            item_logem = discord.Embed(description=f"HP回復薬を使用したが、{p_data['name']} のHPは満タンだった")
            
    if item == "MP回復薬":
        pass
                                       
    
    if item == "ドーピング薬":
        dmg = round(p_data["max_hp"]*0.2)
        pg.execute(f"update player_tb set now_hp = now_hp - {dmg} where id = {user.id};")
        item_logem = discord.Embed(description=f"ドーピング薬を使用し、{p_data['name']} 攻撃力が10%上昇!")

    if item == "冒険者カード":
        embed = discord.Embed(title="Adventure Info")
        embed.add_field(name="Name",value=f"**{p_data['name']}**")
        embed.add_field(name="Sex",value=f"**{p_data['sex']}**")
        embed.add_field(name="KillCount",value=f"**{p_data['kill_ct']}**")
        embed.add_field(name="Money",value=f"**{p_data['money']}cell**")
        if client.get_channel(p_data['cbt_ch_id']):
            cbt_ch = client.get_channel(p_data['cbt_ch_id'])
            embed.add_field(name="Battle",value=f"{cbt_ch.mention}")
        embed.set_thumbnail(url=user.avatar_url)
        embed.timestamp = datetime.now(JST)
        await ch.send(embed=embed)

    if item_logem:
        item_logem.set_thumbnail(url=ITEMS_IMG_URL[item])
        await ch.send(embed=item_logem)




                  
                  
                  
                  
                  
