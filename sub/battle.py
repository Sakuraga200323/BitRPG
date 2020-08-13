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

def cbt_proc(user,ch):
    import sub.box, sub.calc
    print("Battle:" ,user.id, ch.id)
    p_data = pg.fetchdict(f"select * from player_tb where id = {user.id};")[0]
    m_data = pg.fetchdict(f"select * from mob_tb where id = {ch.id};")[0]
    if user.id in sub.box.cbt_user:
        user_cbt_prace = client.get_channel(sub.box.cbt_user[user.id])
        if user_cbt_prace and user_cbt_prace.id != ch.id:
            loop.create_task(ch.send(f"【警告】{p_data['name']}は現在『{user_cbt_prace.name}』で戦闘中です。"))
            return
    if p_data["now_hp"] <= 0:
        loop.create_task(ch.send(f"【報告】{p_data['name']}は既に死亡しています。"))
        return
    if not user.id in sub.box.cbt_user:
        sub.box.cbt_user[user.id] = ch.id
    if not ch.id in sub.box.cbt_ch:
        sub.box.cbt_ch[ch.id] = []
    if not user.id in sub.box.cbt_ch[ch.id]:
        sub.box.cbt_ch[ch.id].append(user.id)
    pg.execute(f"update player_tb set cbt_ch_id = {ch.id} where id = {user.id};")
    if m_data["lv"] % 1000 == 0:
        get_exp = m_data["lv"]*100
    elif m_data["lv"] % 100 == 0:
        get_exp = m_data["lv"]*5
    elif m_data["lv"] % 10 == 0:
        get_exp = m_data["lv"] * 1.5
    else:
        get_exp = m_data["lv"]
    get_exp = round(get_exp)
    first_moblv = m_data["lv"]
    dmg1 = sub.calc.dmg(p_data["str"], m_data["def"])
    dmg2 = sub.calc.dmg(m_data["str"], p_data["def"])
    log1_1 = ""
    log2_1 = ""
    luck = random.randint(0, 100)
    luck2 = random.randint(0, 100)
    if p_data["agi"] >= m_data["agi"]:
        log1_1 += f'+ {p_data["name"]} の攻撃！'
        t = "ダメージ"
        X = 1
        if luck >= 95:
            t = "極ダメージ！"
            X = 3
        elif luck >= 90:
            t = "超ダメージ！"
            X = 2
        elif luck >= 85:
            t = "強ダメージ！"
            X = 1.5
        dmg1 = round(X * dmg1)
        m_data["now_hp"] -= dmg1
        pg.execute(f"update mob_tb set now_hp = {m_data['now_hp']} where id = {m_data['id']};")
        log1_1 += str(dmg1)
        log1_1 += f"の{t}"
        log1_1 += f'\n{m_data["name"]} のHP[{m_data["now_hp"]}/{m_data["max_hp"]}]'
        if m_data["now_hp"] <= 0:
            log2_1 = f'{m_data["name"]} を倒した！！'
            m_data["lv"] += 1
        else:
            log2_1 += f'- {m_data["name"]} の攻撃！'
            X = 1
            t2 = "ダメージ"
            if luck2 >= 95:
                t2 = "極ダメージ！"; X = 3
            elif luck2 >= 90:
                t2 = "超ダメージ！"; X = 2
            elif luck2 >= 85:
                t2 = "強ダメージ！"; X = 1.5
            dmg2 = round(X * dmg2)
            p_data["now_hp"] -= dmg2
            pg.execute(f"update player_tb set now_hp = {p_data['now_hp']} where id = {p_data['id']};")
            log2_1 += str(dmg2)
            log2_1 += f"の{t2}"
            log2_1 += f'\n{p_data["name"]} のHP[{p_data["now_hp"]}/{p_data["max_hp"]}]'
            if p_data["now_hp"] <= 0:
                log2_1 += f'{p_data["name"]} はやられてしまった！！'


    else:
        log1_1 += f'- {m_data["name"]} の攻撃！'
        t = "ダメージ" ; X = 1
        if luck >= 95:
            t = "極ダメージ！"; X = 3
        elif luck >= 90:
            t = "超ダメージ！"; X = 2
        elif luck >= 85:
            t = "強ダメージ！"; X = 1.5
        dmg2 = round(X * dmg2)
        p_data["now_hp"] -= dmg2
        pg.execute(f"update player_tb set now_hp = {p_data['now_hp']} where id = {p_data['id']};")
        log1_1 += str(dmg2)
        log1_1 += f"の{t}"
        log1_1 += f'\n{p_data["name"]} のHP[{p_data["now_hp"]}/{p_data["max_hp"]}]'
        if p_data["now_hp"] <= 0:
            log2_1 = f'\n{p_data["name"]} はやられてしまった！！'
        else:
            log2_1 += f'+ {p_data["name"]} の攻撃！'
            t2 = "ダメージ" ; X = 1
            if luck2 >= 95:
                t2 = "極ダメージ！"; X = 3
            elif luck2 >= 90:
                t2 = "超ダメージ！"; X = 2
            elif luck2 >= 85:
                t2 = "強ダメージ！"; X = 1.5
            dmg1 = round(X * dmg1)
            m_data["now_hp"] -= dmg1
            pg.execute(f"update mob_tb set now_hp = {m_data['now_hp']} where id = {m_data['id']};")
            log2_1 += str(dmg1)
            log2_1 += f"の{t2}"
            log2_1 += f'\n{m_data["name"]} のHP[{m_data["now_hp"]}/{m_data["max_hp"]}]'
            if m_data["now_hp"] <= 0:
                log2_1 += f'\n{m_data["name"]} を倒した！！'
                m_data["lv"] += 1

    embed = None
    em = None
    if first_moblv < m_data["lv"]:
        desc = ""
        now = datetime.now(JST)strftime("%H:%M")
        if  now in ['23:18']
            get_exp *= 16

        for i in sub.box.cbt_ch[ch.id]:
            i_data = pg.fetchdict(f"select * from player_tb where id = {i}")[0]
            be_lv = i_data["lv"]
            i_data["all_exp"] += get_exp
            i_data["now_exp"] += get_exp
            while i_data["now_exp"] > i_data["lv"]:
                i_data["now_exp"] -= i_data["lv"]
                i_data["lv"] += 1
                if p_data["lv"] % 10 == 0:
                    p_data["stp"] += 50
            desc += f'\n{i_data["name"]} が`{get_exp}Exp`獲得'
            if i_data["lv"] > be_lv:
                i_data["str"] = 10*(i_data["lv"] + 1) + i_data["str_stp"]
                i_data["def"] = 10*(i_data["lv"] + 1) + i_data["def_stp"]
                i_data["agi"] = 10*(i_data["lv"] + 1) + i_data["agi_stp"]
                i_data["max_hp"] = 10*(i_data["lv"] + 1)
                i_data["now_hp"] = i_data["max_hp"]
                i_data["now_mp"] = i_data["lv"]
                desc += f"\n{i_data['name']} はLvUP `{be_lv}->{i_data['lv']}`"
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
                    money = {i_data["money"] + (round(m_data["lv"]/len(sub.box.cbt_ch[ch.id])))} where id = {i};'''
            )
            try:
                if i in sub.box.cbt_user:
                    del sub.box.cbt_user[i]
            except:
                loop.create.tasks(ch.send(f"【注意】{i_data['name']} の戦闘離脱処理が正常に作動しなかった可能性が発生。"))
            i_data = pg.fetchdict(f"select * from player_tb where id = {i}")[0]
        if luck >= 1000:
            a = p_data["items"]
            a.append('魔石')
            print(f'{a}')
            b = f'{a}'.strip(']').strip('[')
            pg.execute(
                f"""update player_tb set items = '{{b}}';"""
            )
            em = discord.Embed(
                description = f"{p_data['name']} が魔石を発見！")
            em.set_thumbnail(url = "https://media.discordapp.net/attachments/719855399733428244/720967442439864370/maseki.png")
            
        embed = discord.Embed(title = "Result",description = desc,color = discord.Color.green())
        pg.execute(f"update player_tb set cbt_ch_id = NULL where cbt_ch_id = {ch.id};")
        if ch.id in sub.box.cbt_ch:
            del sub.box.cbt_ch[ch.id]
           
        
    log1_2 = f"```diff\n{log1_1}```"
    log2_2 = f"```diff\n{log2_1}```"
    battle_log = f"{log1_2}{log2_2}"
    print(type(p_data["items"]), p_data["items"])
    loop.create_task(ch.send(content = battle_log,embed = embed))
    if em:
        loop.create_task(ch.send(embed = em))
    if first_moblv < m_data["lv"]:
        import sub.mob
        loop.create_task(ch.send(embed=sub.mob.appear(m_data)))



def reset(user, ch):
    p_data = pg.fetchdict(f"select * from player_tb where id = {user.id};")[0]
    m_data = pg.fetchdict(f"select * from mob_tb where id = {ch.id};")[0]
    if ch.id in sub.box.cbt_ch:
        if not user.id in sub.box.cbt_ch[ch.id]:
            return
        for i in sub.box.cbt_ch[ch.id]:
            i_data = pg.fetchdict(f"select * from player_tb where id = {i};")[0]
            pg.execute(f"update player_tb set now_hp = {i_data['max_hp']} where id = {i};")
            if not i in sub.box.cbt_user:
                return
            del sub.box.cbt_user[i]
        pg.execute(f"update mob_tb set now_hp = {m_data['max_hp']} where id = {ch.id};")
        loop.create_task(ch.send(f"{m_data['name']}(Lv:{m_data['lv']}) との戦闘が解除されました。"))
        rank = "Normal"
        color = discord.Color.blue()
        if m_data["lv"] % 1000 == 0:
            rank = "WorldEnd"
            color = discord.Color.black()
        if  m_data["lv"] % 100 == 0:
            rank = "Catastrophe"
            color = discord.Color.red()
        if m_data["lv"] % 10 == 0:
            rank = "Elite"
            color = discord.Color.gold()
        embed = discord.Embed(
            title=f"<{rank}> {m_data['name']} appears !!",
            description=f"Lv:{m_data['lv']} HP:{m_data['max_hp']}",
            color=color
        )
        embed.set_image(url=m_data["img_url"])
        loop.create_task(ch.send(embed = embed))
    else:
        if not user.id in sub.box.cbt_user:
            pg.execute(f"update player_tb set now_hp = {p_data['max_hp']} where id = {user.id}")
            loop.create_task(ch.send(f"HPを回復しました。"))
        loop.create_task(ch.send(f"『{ch.name}』で戦闘は実行されていません。"))
                    
