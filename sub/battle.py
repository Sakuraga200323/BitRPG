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

def cbt_proc(user,ch):
    p_data = pg.fetchdict(f"select * from player_tb where id = {user.id};")[0]
    m_data = pg.fetchdict(f"select * from mob_tb where id = {ch.id};")[0]
    if user.id in sub.box.cbt_user:
        print(sub.box.cbt_user[user.id])
        user_cbt_prace = client.get_channel(sub.box.cbt_user[user.id])
        if user_cbt_prace.id != ch.id:
            loop.create_task(ch.send(f"【警告】{p_data['name']}は現在『{user_cbt_prace.name}』で戦闘中です。"))
            return
    if p_data["now_hp"] <= 0:
        loop.create_task(ch.send(f"【警告】{p_data['name']}は既に死亡しています。"))
        return
    if not user.id in sub.box.cbt_user:
        sub.box.cbt_user[user.id] = ch.id
    if not ch.id in sub.box.cbt_ch:
        sub.box.cbt_ch[ch.id] = []
    if not user.id in sub.box.cbt_ch[ch.id]:
        sub.box.cbt_ch[ch.id].append(user.id)
    if m_data["lv"] % 1000 == 0:
        get_exp = m_data["lv"]*100
    elif m_data["lv"] % 100 == 0:
        get_exp = m_data["lv"]*5
    elif m_data["lv"] % 10 == 0:
        get_exp = m_data["lv"] % 1.5
    else:
        get_exp = m_data["lv"]
    get_exp = round(get_exp)
    first_moblv = m_data["lv"]
    dmg1 = sub.calc.dmg(p_data["str"], m_data["def"])
    dmg2 = sub.calc.dmg(m_data["str"], p_data["def"])
    log1_1 = ""
    log2_1 = ""
    luck = random.randint(0, 100)
    if p_data["agi"] >= m_data["agi"]:
        log1_1 += f'+ {p_data["name"]}の攻撃！'
        X = 1
        if luck >= 95:
            log1_1 += "極ダメージ！"; X = 3
        elif luck >= 90:
            log1_1 += "超ダメージ！"; X = 2
        elif luck >= 85:
            log1_1 += "強ダメージ！"; X = 1.5
        dmg1 = round(X * dmg1)
        m_data["now_hp"] -= dmg1
        log1_1 += str(dmg1)
        log1_1 += f'\n{m_data["name"]}のHP[{m_data["now_hp"]}/{m_data["max_hp"]}]'
        if m_data["now_hp"] <= 0:
            log2_1 = f'{m_data["name"]}を倒した！！'
            m_data["lv"] += 1
        else:
            log2_1 += f'+ {m_data["name"]}の攻撃！'
            X = 1
            if luck >= 95:
                log2_1 += "極ダメージ！"; X = 3
            elif luck >= 90:
                log2_1 += "超ダメージ！"; X = 2
            elif luck >= 85:
                log2_1 += "強ダメージ！"; X = 1.5
            dmg2 = round(X * dmg2)
            p_data["now_hp"] -= dmg2
            log2_1 += str(dmg2)
            log2_1 += f'\n{p_data["name"]}のHP[{p_data["now_hp"]}/{p_data["max_hp"]}]'
            if p_data["now_hp"] <= 0:
                log2_1 = f'{p_data["name"]}はやられてしまった！！'

    if first_moblv < m_data["lv"]:
        desc = ""
        for i in box.cbt_ch[ch.id]:
            i_data = pg.fetchdict(f"select * from player_tb where id = {i}")[0]
            be_lv = i_data["lv"]
            i_data["all_exp"] += get_exp
            i_data["now_exp"] += get_exp
            while i_data["now_exp"] < i_data["lv"]:
                i_data["now_exp"] += i_data["lv"]
                i_data["lv"] += 1
                if p_data["lv"] % 10 == 0:
                    p_data["stp"] += 50
            desc += f'\n{i_data["name"]}が`{get_exp}Exp`獲得'
            if i_data["lv"] > be_lv:
                i_data["str"] = 10*(i_data["lv"] + 1) + i_data["str_stp"]
                i_data["def"] = 10*(i_data["lv"] + 1) + i_data["def_stp"]
                i_data["agi"] = 10*(i_data["lv"] + 1) + i_data["agi_stp"]
                i_data["max_hp"] = 10*(i_data["lv"] + 1)
                i_data["now_hp"] = i_data["max_hp"]
                i_data["now_mp"] = i_data["lv"]
                desc += f"\n{i_data['name']}はLvUP `{be_lv}->{i_data['lv']}`"
            try:
                del box.cbt_user[i.id]
            except Exception as e:
                pass
            pg.execute(
                f'''update player_tb set
                    lv = {i_data["lv"]},
                    max_hp = {i_data["max_hp"]},
                    now_hp = {i_data["max_hp"]},
                    max_mp = {i_data["lv"]},
                    now_mp = {i_data["now_mp"]},
                    str = {i_data["str"]},
                    def = {i_data["def"]},
                    agi = {i_data["agi"]},
                    stp = {i_data["stp"]},
                    all_exp = {i_data["all_exp"]},
                    now_exp = {i_data["now_exp"]},
                    money = {i_data["money"] + (round(m_data["lv"]/len(box.cbt_ch[ch.id])))} where id = {i.id};'''
            )
        if luck >= 99:
            a = p_data["items"].split("]")[0] + ",'魔石',]"
            pg.execute(
                f'''update player_tb set items = "{a}";'''
            )
            em = discord.Embed(
                description = f"{player.mention}が魔石を発見！")
            em.set_thumbnail(url = "https://media.discordapp.net/attachments/719855399733428244/720967442439864370/maseki.png")
            em_list.append(em)
        log1_2 = f"```diff\n{log1_1}```"
        log2_2 = f"```diff\n{log2_1}```"
        battle_log = f"{log1_2} {log2_2}"
        embed = discord.Embed(title = "Result",description = desc,)
        loop.create_task(ch.send(content = battle_log,embed = embed))
        print("Battle:" ,user.id, ch.id)
