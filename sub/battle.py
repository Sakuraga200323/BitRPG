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
from sub import box, calc, avatar


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

async def cbt_proc(client, user, ch):
    print(box.players)
    print(box.mobs)
    if not user.id in box.players:
        box.players[user.id] = avatar.Player(client, user.id)
        print(f"Playerデータ挿入： {box.players[user.id].user}")
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if not player.battle_start(ch.id):
        channel = client.get_channel(player.battle_ch)
        if channel:
            await ch.send(f"<@{user.id}> は現在『<@{channel.id}>』で戦闘中です。")
            return
        else:
            await ch.send(f"<@{user.id}> のデータに存在しないチャンネルIDが記載されていました。データの上書きを行ないます。")
            player.battle_end()
            if player.battle_start(ch.id):
                await ch.send(f"上書き完了")
            else:
                await ch.send(f"上書き失敗、戦闘に参加できていません。")
                return

    if player.now_hp <= 0:
        await ch.send(f"<@{user.id}> は既に死亡しています。")
        return
    mob.player_join(user.id)



    # モンスターとの戦闘で使うダメージ、運の計算およびログの設定 #
    dmg1 = calc.dmg(player.STR(), mob.defe())
    dmg2 = calc.dmg(mob.str(), player.DEFE())
    if mob.name == "古月":
        dmg2 *= 0.75
        dmg2 = int(dmg2*2)
    log1_1 = ""
    log2_1 = ""
    luck = random.randint(0, 100)
    luck2 = random.randint(0, 100)



    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
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
        log1_1 += str(dmg1)
        log1_1 += f"の{t}"
        log1_1 += f'\n{mob.name} のHP[{mob.cut_hp(dmg1)}/{mob.max_hp}]'
        if mob.now_hp <= 0:
            log2_1 = f'{mob.name} を倒した！！'
        else:
            log2_1 += f'- {mob.name} の攻撃！'
            if mob.name == "古月":
                log2_1 += "デュアルミスリルパイプ!"
            X = 1
            t2 = "ダメージ"
            if luck2 >= 95:
                t2 = "極ダメージ！"; X = 3
            elif luck2 >= 90:
                t2 = "超ダメージ！"; X = 2
            elif luck2 >= 85:
                t2 = "強ダメージ！"; X = 1.5
            dmg2 = round(X * dmg2)
            log2_1 += str(dmg2)
            if mob.name == "古月":
                log2_1 += f"×2の{t2}"
            else:
                log2_1 += f"の{t2}"
            log2_1 += f'\n{user.name} のHP[{player.cut_hp(dmg2)}/{player.max_hp}]'
            if p_data["now_hp"] <= 0:
                log2_1 += f'{user.name} はやられてしまった！！'


    # 戦闘処理（Player後手） #
    else:
        log1_1 += f'- {mob.name} の攻撃！'
        if mob.name == "古月":
            log2_1 += "デュアルミスリルパイプ!"
        t = "ダメージ" ; X = 1
        if luck >= 95:
            t = "極ダメージ！"; X = 3
        elif luck >= 90:
            t = "超ダメージ！"; X = 2
        elif luck >= 85:
            t = "強ダメージ！"; X = 1.5
        dmg2 = round(X * dmg2)
        if mob.name == "古月":
            log1_1 += str(dmg2/2)
            log1_1 += f"×2の{t}"
        else:
            log1_1 += str(dmg2)
            log1_1 += f"の{t}"
        log1_1 += f'\n{user.name} のHP[{player.cut_hp(dmg2)}/{player.max_hp}]'
        if player.now_hp <= 0:
            log2_1 = f'\n{user.name} はやられてしまった！！'
        else:
            log2_1 += f'+ {user.name} の攻撃！'
            t2 = "ダメージ" ; X = 1
            if luck2 >= 95:
                t2 = "極ダメージ！"; X = 3
            elif luck2 >= 90:
                t2 = "超ダメージ！"; X = 2
            elif luck2 >= 85:
                t2 = "強ダメージ！"; X = 1.5
            dmg1 = round(X * dmg1)
            log2_1 += str(dmg1)
            log2_1 += f"の{t2}"
            log2_1 += f'\n{mob.name} のHP[{mob.cut_hp(dmg1)}/{mob.max_hp}]'
            if m_data["now_hp"] <= 0:
                log2_1 += f'\n{mob.name} を倒した！！'

    log1_2 = f"```diff\n{log1_1}```"
    log2_2 = f"```diff\n{log2_1}```"
    battle_log = f"{log1_2}{log2_2}"


    # バフのターンとかの確認 #
    #buff_text = ""
    #if user.id in buff.doping:  # ドーピング薬
    #    buff.doping[user.id][0] -= 1
    #    if buff.doping[user.id][0] <= 0:
    #        p_data["now_hp"] -= buff.doping[user.id][1]
    #        buff_text += f"- {p_data['name']} はドーピング薬の反動を受けた！{buff.doping[user.id][1]}のダメージ!\n"
    #        buff_text += f"{p_data['name']} のHP[{p_data['now_hp']}/{p_data['max_hp']}]"
    #        buff_log = f"```diff\n{buff_text}```"
    #        battle_log += buff_log
    #        del buff.doping[user.id]

    embed = em = item_em = None
    if mob.now_hp <= 0:
        desc = ""
        now = datetime.now(JST).strftime("%H:%M")
        if  now in ['23:18']:
            get_exp *= 16
            await ch.send("????『幸運を。死したものより祝福を。』")

        exp, money = mob.exp()
        for p_id in mob.battle_players_id:
            p = box.players[p_id]
            p.get_exp(exp)
        mob.battle_end()

        if random.random() >= 0.99:
            player.now_stp(mob.lv())
            em = discord.Embed(description=f"<@{user.id}> は{mob.lv()}のSTPを獲得した！")

        embed = discord.Embed(title="Result",description = desc,color = discord.Color.green())
    
    
    await ch.send(content=battle_log,embed = embed)
    if em:
        await ch.send(embed=em)
    if item_em:
        await ch.send(embed=item_em)
    embed = mob.spawn()
    await ch.send(embed=embed)


async def reset(user, ch):
    if not user or not ch:
        await ch.send("【報告】処理中になんらかのバグが発生し、プレイヤーもしくはチャンネルの情報が取得できませんでした。")
        rerturn
    p_data = pg.fetchdict(f"select * from player_tb where id = {user.id};")[0]
    m_data = pg.fetchdict(f"select * from mob_tb where id = {ch.id};")[0]

    if not p_data["cbt_ch_id"] or (p_data["cbt_ch_id"] and not p_data["cbt_ch_id"] in box.cbt_ch):
        pg.execute(f"update player_tb set now_hp = {p_data['max_hp']}, cbt_ch_id = Null where id = {user.id}")
        await ch.send(f"【報告】HPを回復しました。")
        return

    if not p_data["cbt_ch_id"] == ch.id:
        if p_data["cbt_ch_id"] in box.cbt_ch:
            await ch.send(f"【警告】{p_data['name']} は{ch.mention}で戦闘していません。")

    else:
        if not ch.id in box.cbt_ch:
            pg.execute(f"update player_tb set now_hp = {p_data['max_hp']}, cbt_ch_id = Null where id = {user.id};")
            pg.execute(f"update mob_tb set now_hp = {m_data['max_hp']} where id = {ch.id};")
            await ch.send("【報告】処理中のなんらかのバグによるデータの矛盾を発見しました。強制的に戦闘解除、およびHPの回復を行いました。")
            return

        for i in box.cbt_ch[ch.id]:
            i_data = pg.fetchdict(f"select * from player_tb where id = {i};")[0]
            pg.execute(f"update player_tb set now_hp = {i_data['max_hp']} where id = {i};")
            if not i in box.cbt_user:
                return
            del box.cbt_user[i]
        pg.execute(f"update mob_tb set now_hp = {m_data['max_hp']} where id = {ch.id};")
        await ch.send(f"{m_data['name']}(Lv:{m_data['lv']}) との戦闘が解除されました。")
        rank = "Normal"
        color = discord.Color.blue()
        if m_data["lv"] % 1000 == 0:
            rank = "WorldEnd"
            color = discord.Color.from_rgb(0,0,0)
        if  m_data["lv"] % 100 == 0:
            rank = "Catastrophe"
            color = discord.Color.red()
        if m_data["lv"] % 10 == 0:
            rank = "Elite"
            color = discord.Color.from_rgb(255,255,0)
        embed = discord.Embed(
            title=f"<{rank}> {m_data['name']} appears !!",
            description=f"Lv:{m_data['lv']} HP:{m_data['max_hp']}",
            color=color
        )
        if m_data["lv"] % 1000 != 0:
            embed.set_image(url=m_data["img_url"])
        await ch.send(embed = embed)
                    
