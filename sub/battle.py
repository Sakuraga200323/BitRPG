import ast
import asyncio
import cv2
from datetime import datetime, timedelta, timezone
import math
import os
from random import random, randint, choice
import re
import sys

import discord
from discord.ext import tasks, commands
import psutil
import psycopg2, psycopg2.extras
import traceback

from sub import box, status, avatar, calc

JST = timezone(timedelta(hours=+9), 'JST')

item_emoji = {
    1:"<:card:786514637289947176>",
    2:"<:hp_potion:786236538584694815>",
    3:"<:mp_potion:786236615575339029>",
    4:"<:soul_fire:786513145010454538>",
    5:"<:toishi:786513144691556364>",
    6:"<:maseki:785641515561123921>",
    7:"<:masuisyou:786516036673470504>",
    8:"<:magic_coin:786513121236746260>",
}

item_emoji_a = {
    1:"<:card:786514637289947176>",
    2:"<a:hp_potion_a:786982694479200336>",
    3:"<a:mp_potion_a:786982694839124021>",
    4:"<:soul_fire:786513145010454538>",
    5:"<a:toishi_a:786974865777229864>",
    6:"<:maseki:785641515561123921>",
    7:"<a:masuisyou_a:786982694948306974>",
    8:"<a:magic_coin_a:786966211594289153>"
}


pg = None
client = None




async def battle_start_check(player, mob):
    ch = mob.mob
    user = player.user
    if not user.id in box.players:
        print("box.playersに存在しないPlayer.idを取得")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from player_tb;")]:
            box.players[user.id] = player
            print(f"Playerデータ挿入(battle.py->cbt_proc)： {player.user}")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from mob_tb;")]:
            box.mobs[user.id] = mob
            print(f"Mobデータ挿入(battle.py->cbt_proc)： {mob.name}")
    if not player.battle_start(ch.id):
        channel = client.get_channel(player.battle_ch)
        if channel:
            await ch.send(f"<@{user.id}> は現在『{now_ch.mention}』で戦闘中です。")
            return 0
        await ch.send(f"<@{user.id}> が認識できないチャンネルで戦闘中。データの上書きを行ないます。")
        player.battle_end()
        if player.battle_start(ch.id):
            await ch.send(f"上書き完了")
        else:
            await ch.send(f"上書き失敗、戦闘に参加できていません。")
            return 0
    if player.now_hp <= 0:
        await ch.send(f"<@{user.id}> は既に死亡しています。")
        return 0
    mob.player_join(user.id)
    return 1





async def battle_result(player, mob):
    reward_items = { # {id:(num,item was droped)}
        2:(randint(3,6),random()<=0.05),
        3:(randint(3,6),random()<=0.05),
        4:(1,True),
        5:(choice((1,2)),mob.name in ("Golem",)),
        6:(randint(3,6),random()<=0.03)}
    ch = mob.mob
    user = player.user
    result_em = stp_em = item_em = spawn_em = None
    if mob.now_hp <= 0 :
        result_desc = ""
        now = datetime.now(JST).strftime("%H:%M")
        if  now in ['23:18']:
            get_exp *= 16
            await ch.send("????『幸運を。死したものより祝福を。』")
        exp, money = mob.reward()[0], int(mob.reward()[1]/len(mob.battle_players))
        print("戦闘参加していたPlayer: ",mob.battle_players)
        for p_id in mob.battle_players:
            p = box.players[p_id]
            up_exp, up_lv = p.get_exp(exp)
            p.kill_count(1)
            p.money(money)
            result_desc += f"<@{p_id}> Exp+{exp} Cell+{money} "
            if up_lv > 0:
                result_desc += f"\nLvUP {p.lv()-up_lv} -> {p.lv()}"
            drop_item_text = ""
            # ドロップアイテムfor #
            for id in reward_items:
                num,item_was_droped = reward_items[id]
                if item_was_droped:
                    status.get_item(client,user,id,num)
                    drop_item_text += f"{item_emoji_a[id]}×{num} "
            result_desc += f"\nDropItem： {'-' if not drop_item_text else drop_item_text}"
        if random() <= 0.01:
            player.now_stp(mob.lv())
            stp_em = discord.Embed(description=f"<@{user.id}> STP+{mob.lv()}")
        result_em = discord.Embed(title="Result",description=result_desc,color=discord.Color.green())
        mob.lv(1)
        spawn_em = mob.battle_end()
    for em in (result_em, stp_em, item_em, spawn_em):
        if em : await ch.send(embed=em)





# 戦闘 #
async def cbt_proc(client, user, ch):
    player,mob = box.players[user.id],box.mobs[ch.id]
    await battle_start_check(player, mob)
    # モンスターとの戦闘で使うダメージ、運の計算およびログの定義 #
    dmg1,dmg2 = calc.dmg(player.STR(), mob.defe()),calc.dmg(mob.str(), player.DEFE())
    dmg2 = int(dmg2*1.45) if mob.name=="古月" else dmg2
    log1_1 = log2_1 = ""

    # HPゲージ作成関数 #
    def hp_gauge(now, max):
        num = int((now/max)*20)
        guage_1 = ((num)*"/")+((20-num)*" ")
        return ('-[' if num<11 else '+[') + ("-"*20 if now<=0 else guage_1) + ']'

    a,b = random(),random()
    t,x = ("極",5) if a>=0.95 else ("超",2) if a>=0.9 else ("強",1.5) if a>=0.85 else ("",1)
    t2,x2 = ("極",5) if b>=0.95 else ("超",2) if b>=0.9 else ("強",1.5) if b>=0.85 else ("",1)
    t += "ダメージ！"
    t2 += "ダメージ！"
    
    # ダメージがない場合のメッセージ #
    def zero_dmg_text():
        text = ("華麗に躱した","完全に防いだ","当たらなかった","効かなかったようだ","無駄無駄無駄無駄無駄ァ！")
        return choice(text)

    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        log1_1 += f'{player.user}の攻撃->'
        dmg1 = round(x * dmg1)
        log1_1 += f"{str(dmg1)}の{t}" if dmg1!=0 else zero_dmg_text()
        log1_1 += f'\n{mob.name}({mob.cut_hp(dmg1)}/{mob.max_hp})\n{hp_gauge(mob.now_hp, mob.max_hp)}'
        log2_1 += f'{mob.name}を倒した！！' if mob.now_hp<=0 else f'{mob.name}の攻撃->'
        if not mob.now_hp <= 0:
            dmg2 = round(x2 * dmg2)
            log2_1 += f"{str(dmg2)}の{t2}" if dmg2!=0 else zero_dmg_text()
            log2_1 += f'\n{user}({player.cut_hp(dmg2)}/{player.max_hp})\n{hp_gauge(player.now_hp, player.max_hp)}'

    # 戦闘処理（Player後手） #
    else:
        log1_1 += f'{mob.name}の攻撃->'
        dmg2 = round(x * dmg2)
        log1_1 += f"{str(dmg2)}の{t}" if dmg2!=0 else zero_dmg_text()
        log1_1 += f'\n{user}({player.cut_hp(dmg2)}/{player.max_hp})\n{hp_gauge(player.now_hp, player.max_hp)}'
        log2_1 += f'{user}はやられてしまった！！' if player.now_hp<=0 else f'{user}の攻撃->'
        if not player.now_hp <= 0 :
            dmg1 = round(x2 * dmg1)
            log2_1 += f"{str(dmg1)}の{t2}" if dmg1!=0 else zero_dmg_text()
            log2_1 += f'\n{mob.name}({mob.cut_hp(dmg1)}/{mob.max_hp})\n{hp_gauge(mob.now_hp, mob.max_hp)}'

    battle_log = f"```diff\n{log1_1}``````diff\n{log2_1}```"
    await ch.send(content=battle_log)
    await battle_result(player, mob)





# 戦闘から離脱 #
async def reset(client, user, ch):
    player,mob = box.players[user.id],box.mobs[ch.id]
    if not user.id in box.players:
        print("box.playersに存在しないPlayer.idを取得")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from player_tb;")]:
            box.players[user.id] = player
            print(f"Playerデータ挿入(battle.py->cbt_proc)： {player.user}")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from mob_tb;")]:
            box.mobs[user.id] = mob
            print(f"Mobデータ挿入(battle.py->cbt_proc)： {mob.name}")
    if not player.battle_ch:
        player.now_hp = player.max_hp
        await ch.send(f"HPを全回復しました。")
        return
    now_ch = client.get_channel(player.battle_ch)
    if player.battle_ch != ch.id:
        await ch.send(f"<@{player.user.id}> は現在『{now_ch.mention}』で戦闘中です。")
        return
    mob.battle_end()
    await ch.send(embed = mob.spawn())
                    
