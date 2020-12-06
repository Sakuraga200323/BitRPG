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



token = os.environ.get('TOKEN')

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

pg = None

async def cbt_proc(client, user, ch):
    if not user.id in box.players:
        print("box.playersに存在しないPlayer.idを取得")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from player_tb;")]:
            box.players[user.id] = avatar.Player(client, user.id)
            print(f"Playerデータ挿入(battle.py>cbt_proc)： {box.players[user.id].user}")
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

    # HPゲージの取得
    def hp_gauge(now, max):
        gauge_num = int((now/max)*20)
        return (gauge_num*"/") + ((20 - gauge_num)*" ")

    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        log1_1 += f'+ {player.user}の攻撃->'
        t = "ダメージ"
        X = 1
        if random.random() >= 0.95:
            t = "極ダメージ！"
            X = 3
        elif random.random() >= 0.9:
            t = "超ダメージ！"
            X = 2
        elif random.random() >= 0.85:
            t = "強ダメージ！"
            X = 1.5
        dmg1 = round(X * dmg1)
        if dmg1 != 0:
            log1_1 += str(dmg1)
            log1_1 += f"の{t}"
        else:
            if dmg1 == 0:
                log1_1 += "しかし当たらなかった"
        log1_1 += f'\n{mob.name} のHP[{mob.cut_hp(dmg1)}/{mob.max_hp}]'
        log1_1 += f"\n[{hp_gauge(mob.now_hp, mob.max_hp)}]"
        if mob.now_hp <= 0:
            log2_1 = f'{mob.name}を倒した！！'
        else:
            log2_1 += f'- {mob.name}の攻撃->'
            X = 1
            t2 = "ダメージ"
            if random.random() >= 0.95:
                t2 = "極ダメージ！"; X = 3
            elif random.random() >= 0.9:
                t2 = "超ダメージ！"; X = 2
            elif random.random() >= 85:
                t2 = "強ダメージ！"; X = 1.5
            dmg2 = round(X * dmg2)
            if dmg2 != 0:
                log2_1 += str(dmg2)
                log2_1 += f"の{t2}"
            elif dmg2 == 0:
                log2_1 += "しかし当たらなかった！"
            log2_1 += f'\n{user} のHP[{player.cut_hp(dmg2)}/{player.max_hp}]'
            log2_1 += f"\n[{hp_gauge(player.now_hp, player.max_hp)}]"
            if player.now_hp <= 0:
                log2_1 += f'{user}はやられてしまった！！'


    # 戦闘処理（Player後手） #
    else:
        log1_1 += f'- {mob.name}の攻撃->'
        t = "ダメージ" ; X = 1
        if random.random() >= 0.95:
            t = "極ダメージ！"; X = 3
        elif random.random() >= 0.9:
            t = "超ダメージ！"; X = 2
        elif random.random() >= 85:
            t = "強ダメージ！"; X = 1.5
        dmg2 = round(X * dmg2)
        if not dmg2 == 0:
            log1_1 += str(dmg2)
            log1_1 += f"の{t}"
        elif dmg2 == 0:
            log1_1 += "しかし当たらなかった！"
        log1_1 += f'\n{user}のHP[{player.cut_hp(dmg2)}/{player.max_hp}]'
        log1_1 += f"\n[{hp_gauge(player.now_hp, player.max_hp)}]"
        if player.now_hp <= 0:
            log2_1 = f'\n{user}はやられてしまった！！'
        else:
            log2_1 += f'+ {user}の攻撃->'
            t2 = "ダメージ" ; X = 1
            if random.random() >= 0.95:
                t2 = "極ダメージ！"; X = 3
            elif random.random >= 0.9:
                t2 = "超ダメージ！"; X = 2
            elif random.random >= 85:
                t2 = "強ダメージ！"; X = 1.5
            dmg1 = round(X * dmg1)
            if not dmg1 == 0:
                log2_1 += str(dmg1)
                log2_1 += f"の{t2}"
            elif dmg1 == 0:
                log2_1 += "しかし当たらなかった！"
            log2_1 += f'\n{mob.name}のHP[{mob.cut_hp(dmg1)}/{mob.max_hp}]'
            log2_1 += f"\n[{hp_gauge(mob.now_hp, mob.max_hp)}]"
            if mob.now_hp <= 0:
                log2_1 += f'\n{mob.name}を倒した！！'

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
    #         del buff.doping[user.id]


    embed = em = item_em = spawn_embed = None
    if mob.now_hp <= 0:
        desc = ""
        now = datetime.now(JST).strftime("%H:%M")
        if  now in ['23:18']:
            get_exp *= 16
            await ch.send("????『幸運を。死したものより祝福を。』")

        exp, money = mob.exp()
        print("戦闘参加しているPlayer: ",mob.battle_players)
        for p_id in mob.battle_players:
            p = box.players[p_id]
            up_exp, up_lv = p.get_exp(exp)
            desc += f"<@{p_id}> は{exp}の経験値を獲得。"
            if up_lv > 0:
                desc += f"LvUP {p.lv()-up_lv} -> {p.lv()}"

        if random.random() >= 0.99:
            player.now_stp(mob.lv())
            em = discord.Embed(description=f"<@{user.id}> は{mob.lv()}のSTPを獲得した！")

        embed = discord.Embed(title="Result",description = desc,color = discord.Color.green())
        mob.lv(1)
        spawn_embed = mob.battle_end()
    
    
    await ch.send(content=battle_log,embed = embed)
    if em:
        await ch.send(embed=em)
    if item_em:
        await ch.send(embed=item_em)
    if spawn_embed:
        await ch.send(embed=spawn_embed)



async def reset(client, user, ch):
    if not user or not ch:
        await ch.send("バグでプレイヤーもしくはチャンネルが見つかりません。")
        rerturn
    if not user.id in box.players:
        box.players[user.id] = avatar.Player(client, user.id)
        print(f"Playerデータ挿入： {box.players[user.id].user}")
        return
    player = box.players[user.id]
    mob = box.mobs[ch.id]

    if not player.battle_ch:
        player.now_hp = player.max_hp
        await ch.send(f"HPを全回復しました。")
        return

    now_ch = client.get_channel(player.battle_ch)
    if player.battle_ch != ch.id:
        await ch.send(f"<@{player.user.id}> は<@{now_ch.id}> で戦闘中です。")
        return
    mob.battle_end()
    await ch.send(embed = mob.spawn())
                    
