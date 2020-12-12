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

from sub import box, status, avatar

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


reward_items = { # {id:(num,item was droped)}
    2:(randint(3,6),random()<=0.05),
    3:(randint(3,6),random()<=0.05),
    4:(1,True),
    5:(choice((1,2)),mob.name in ("Golem",)),
    6:(randint(3,6),random()<=0.03)
}


pg = None

# 戦闘 #
async def cbt_proc(client, user, ch):
    if not user.id in box.players:
        print("box.playersに存在しないPlayer.idを取得")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from player_tb;")]:
            box.players[user.id] = avatar.Player(client, user.id)
            print(f"Playerデータ挿入(battle.py->cbt_proc)： {box.players[user.id].user}")
    player,mob = box.players[user.id],box.mobs[ch.id]
    if not player.battle_start(ch.id):
        channel = client.get_channel(player.battle_ch)
        if channel:
            await ch.send(f"<@{user.id}> は現在『<@{channel.id}>』で戦闘中です。")
            return
        await ch.send(f"<@{user.id}> が認識できないチャンネルで戦闘中。データの上書きを行ないます。")
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

    # モンスターとの戦闘で使うダメージ、運の計算およびログの定義 #
    dmg1,dmg2 = calc.dmg(player.STR(), mob.defe()),calc.dmg(mob.str(), player.DEFE())
    dmg2 = int(dmg2*1.45) if mob.name=="古月" else dmg2
    log1_1 = log2_1 = ""

    # HPゲージ作成関数 #
    def hp_gauge(now, max):
        return  "-"*20 if now<=0 else (int((now/max)*20)*"/")+((20-int((now/max)*20))*" ")

    a,b = random(),random()
    t,x = ("極",5) if a>=0.95 else ("超",2) if a>=0.9 else ("強",1.5) if a>=0.85 else ("",1)
    t2,x2 = ("極",5) if b>=0.95 else ("超",2) if b>=0.9 else ("強",1.5) if b>=0.85 else ("",1)
    t += "ダメージ！"
    t2 += "ダメージ！"

    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        log1_1 += f'+ {player.user}の攻撃->'
        dmg1 = round(x * dmg1)
        log1_1 += f"{str(dmg1)}の{t}" if dmg1!=0 else "しかし当たらなかった…"
        log1_1 += f'\n{mob.name} のHP[{mob.cut_hp(dmg1)}/{mob.max_hp}]\n[{hp_gauge(mob.now_hp, mob.max_hp)}]'
        log2_1 += f'{mob.name}を倒した！！' if mob.now_hp<=0 else f'- {mob.name}の攻撃->'
        if not mob.now_hp <= 0:
            dmg2 = round(x2 * dmg2)
            log2_1 += f"{str(dmg2)}の{t2}" if dmg2!=0 else "しかし当たらなかった…"
            log2_1 += f'\n{user} のHP[{player.cut_hp(dmg2)}/{player.max_hp}]\n[{hp_gauge(player.now_hp, player.max_hp)}]'

    # 戦闘処理（Player後手） #
    else:
        log1_1 += f'- {mob.name}の攻撃->'
        dmg2 = round(x * dmg2)
        log1_1 += f"{str(dmg2)}の{t}" if dmg1!=0 else "しかし当たらなかった…"
        log1_1 += f'\n{user}のHP[{player.cut_hp(dmg2)}/{player.max_hp}]\n[{hp_gauge(player.now_hp, player.max_hp)}]'
        log2_1 += f'{user}はやられてしまった！！' if player.now_hp<=0 else f'- {user}の攻撃->'
        if not player.now_hp <= 0 :
            dmg1 = round(x2 * dmg1)
            log2_1 += f"{str(dmg1)}の{t2}" if dmg1!=0 else "しかし当たらなかった…"
            log2_1 += f'\n{mob.name}のHP[{mob.cut_hp(dmg1)}/{mob.max_hp}]\n[{hp_gauge(mob.now_hp, mob.max_hp)}]'

    battle_log = f"```diff\n{log1_1}``````diff\n{log2_1}```"

    embed = em = item_em = spawn_embed = None
    if mob.now_hp <= 0 :
        desc = ""
        now = datetime.now(JST).strftime("%H:%M")
        if  now in ['23:18']:
            get_exp *= 16
            await ch.send("????『幸運を。死したものより祝福を。』")
        exp,money = mob.reward()[0],int(mob.reward()[1]/len(mob.battle_players))
        print("戦闘参加していたPlayer: ",mob.battle_players)
        for p_id in mob.battle_players:
            p = box.players[p_id]
            up_exp, up_lv = p.get_exp(exp)
            p.kill_count(1)
            p.money(money)
            desc += f"<@{p_id}> Exp+{exp} Money+{money}cell "
            if up_lv > 0: desc += f"\nLvUP {p.lv()-up_lv} -> {p.lv()}"
            drop_items_text = ""
            def get_item_sub(item_id, item_num):
                status.get_item(client, user, item_id, item_num)
                desc += f"{item_emoji_a[item_id]}×{item_num} "
            # ドロップアイテムfor #
            for id in id_num_dict:
                num,item_was_droped = reward_items[id]
                if item_was_droped:
                    get_item_sub(id, num)
            desc += f"\nDropItem： {'-' if not drop_items_text else drop_items_text}"
        if random() <= 0.01:
            player.now_stp(mob.lv())
            em = discord.Embed(description=f"<@{user.id}> STP+{mob.lv()}")
        embed = discord.Embed(title="Result",description=desc,color=discord.Color.green())
        mob.lv(1)
        spawn_embed = mob.battle_end()
    
    await ch.send(content=battle_log,embed = embed)
    if em: await ch.send(embed=em)
    if item_em: await ch.send(embed=item_em)
    if spawn_embed: await ch.send(embed=spawn_embed)

        
# 戦闘から離脱 #
async def reset(client, user, ch):
    if not user or not ch:
        await ch.send("プレイヤーもしくはチャンネルが見つかりません。")
        rerturn
    if not user.id in box.players:
        box.players[user.id] = avatar.Player(client, user.id)
        print(f"Playerデータ挿入： {box.players[user.id].user}")
        return
    player,mob = box.players[user.id],box.mobs[ch.id]
    if not player.battle_ch:
        player.now_hp = player.max_hp
        await ch.send(f"HPを全回復しました。")
        return
    now_ch = client.get_channel(player.battle_ch)
    if player.battle_ch != ch.id:
        await ch.send(f"<@{player.user.id}> は『<@{now_ch.id}>』で戦闘中です。")
        return
    mob.battle_end()
    await ch.send(embed = mob.spawn())
                    
