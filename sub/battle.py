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

from sub import box, status, avatar, calc,  magic_wolf, magic_orca, magic_armadillo

JST = timezone(timedelta(hours=+9), 'JST')

item_emoji = {
    1:"<:card:786514637289947176>",
    2:"<a:hp_potion_a:786982694479200336>",
    3:"<a:mp_potion_a:786982694839124021>",
    4:"<:soul_fire:786513145010454538>",
    5:"<a:toishi_a:786974865777229864>",
    6:"<:maseki:785641515561123921>",
    7:"<a:masuisyou_a:786982694948306974>",
    8:"<a:magic_coin_a:786966211594289153>",
    9:"<:hp_full_potion:788668620074385429>",
    10:"<:mp_full_potion:788668620314116106>",
}

item_emoji_a = {
    1:"<:card:786514637289947176>",
    2:"<a:hp_potion_a:786982694479200336>",
    3:"<a:mp_potion_a:786982694839124021>",
    4:"<:soul_fire:786513145010454538>",
    5:"<a:toishi_a:786974865777229864>",
    6:"<:maseki:785641515561123921>",
    7:"<a:masuisyou_a:786982694948306974>",
    8:"<a:magic_coin_a:786966211594289153>",
    9:"<:hp_full_potion:788668620074385429>",
    10:"<:mp_full_potion:788668620314116106>",
}


pg = None
client = None




async def battle_start(player, mob):
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
            await ch.send(f"<@{user.id}> は現在『{channel.mention}』で戦闘中です。")
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





async def battle_result(player, mob):
    reward_items = { # {id:(num,item was droped)}
        2:(randint(3,6),random()<=0.05),
        3:(randint(3,6),random()<=0.05),
        4:(1,True),
        5:(randint(1,2),mob.name in ("Golem",)),
        6:(randint(3,6),random()<=0.03)}
    ch = mob.mob
    user = player.user
    result_em = stp_em = item_em = spawn_em = None
    if mob.now_hp <= 0 :
        if mob.mob.id in box.nerf:
            del box.nerf[mob.mob.id]
        if mob.mob.id in box.stun:
            del box.stun[mob.mob.id]
        result_desc = ""
        now = datetime.now(JST).strftime("%H:%M")
        exp, money = mob.reward()[0], int(mob.reward()[1]/len(mob.battle_players))
        if  now in ['23:18']:
            exp *= 16
            await ch.send("????『幸運を。死したものより祝福を。』")
        print("戦闘参加していたPlayer: ",mob.battle_players)
        for p_id in mob.battle_players:
            p = box.players[p_id]
            up_exp, up_lv = p.get_exp(exp)
            p.kill_count(1)
            p.money(money)
            result_desc += f"\n<@{p_id}> Exp+{exp} Cell+{money} "
            if up_lv > 0:
                result_desc += f"\nLvUP {p.lv()-up_lv} -> {p.lv()}"
            drop_item_text = ""
            # ドロップアイテムfor #
            for id in reward_items:
                num,item_was_droped = reward_items[id]
                if item_was_droped:
                    status.get_item(user,id,num)
                    drop_item_text += f"{item_emoji_a[id]}×{num} "
            result_desc += f"\nDropItem： {'-' if not drop_item_text else drop_item_text}"
            p.battle_end()
        if random() <= 0.01:
            player.now_stp(mob.lv())
            stp_em = discord.Embed(description=f"<@{user.id}> STP+{mob.lv()}")
        result_em = discord.Embed(title="Result",description=result_desc,color=discord.Color.green())
        mob.lv(1)
        spawn_em = mob.battle_end()
    for em in (result_em, stp_em, item_em, spawn_em):
        if em : await ch.send(embed=em)



# HPゲージ作成関数 #
def hp_gauge(avatar):
    num = int((avatar.now_hp/avatar.max_hp)*20)
    guage_1 = ((num)*"/")+((20-num)*" ")
    return ('-[' if num<5 else "+[") + ("-"*20 if avatar.now_hp<=0 else guage_1) + ']'

# ダメージがない場合のメッセージ #
def zero_dmg_text():
    text = ("華麗に躱した","完全に防いだ","当たらなかった","効かなかったようだ","無駄無駄無駄無駄無駄ァ！")
    return choice(text)


# 戦闘 #
async def cbt_proc(user, ch):
    player,mob = box.players[user.id],box.mobs[ch.id]
    await battle_start(player, mob)
    # モンスターとの戦闘で使うダメージ、運の計算およびログの定義 #
    dmg1,dmg2 = calc.dmg(player.STR(), mob.defe()),calc.dmg(mob.str(), player.DEFE())
    dmg2 = int(dmg2*1.45) if mob.name=="古月" else dmg2
    log1_1 = log2_1 = ""


    a,b = random(),random()
    t,x = ("極",5) if a>=0.95 else ("超",2) if a>=0.9 else ("強",1.5) if a>=0.85 else ("",1)
    t2,x2 = ("極",5) if b>=0.95 else ("超",2) if b>=0.9 else ("強",1.5) if b>=0.85 else ("",1)
    t += "ダメージ！"
    t2 += "ダメージ！"
    
    def create_battle_text(a,b,atk_word="攻撃",buff=0):
        if a.now_hp <= 0:
            if "#" in a.name: result_text = f"{a.name}はやられてしまった"
            else: text = f"{a.name}を倒した"
        else:
            text = f"{a.name}の{atk_word}->"
            if not a.ID() in box.stun:
                if random() <= 0.05:
                    dmg, now_hp = b.damaged(a.STR()*2)
                    text += f"{dmg}のクリティカルヒット"
                else:
                    dmg, now_hp = b.damaged(a.STR()*2)
                    text += f"{dmg}のダメージ"
            if a.ID() in box.nerf:
                if random() <= 0.05:
                    dmg, now_hp = b.damaged(a.STR())
                    text += f"{dmg}のクリティカルヒット"
                else:
                    dmg, now_hp = b.damaged(a.STR()/2)
                    text += f"{dmg}のダメージ"
                box.stun[a.ID()] -= 1
                if box.stun[a.ID()] <= 0: del box.nstun[a.ID]
            if a.ID() in box.stun:
                dmg, now_hp = 0, b.now_hp
                text += f"動けない！"
                box.nerf[a.ID()] -= 1
                if box.nerf[a.ID()] <= 0: del box.nerf[a.ID]
            if buff in [1,2] and not a.id in box.stun:
                buff_dict = {1:"Stun",2:"Nerf"}
                text += f" {buff_dict}"
                if buff == 1:
                    box.stun[b.ID()] = 3
                if buff == 2:
                    box.nerf[b.ID()] = 5
            text += f"\n{b.name} ({b.now_hp}/{b.max_hp})\n{hp_gauge(b)}"
        return text
        
                    
    
    # バフチェック
    if ch.id in box.nerf and box.nerf[ch.id] > 0:
        dmg2 *= 0.5
        dmg2 = int(dmg2)
        box.nerf[ch.id] -= 1
    if ch.id in box.stun and box.stun[ch.id] > 0:
        dmg2 = 0
        box.stun[ch.id] -= 1

    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        log1_1 += f'{player.user}の攻撃->'
        dmg1 = round(x * dmg1)
        log1_1 += f"{dmg1}の{t}" if dmg1!=0 else f"{mob.name}は動けない！" if ch.id in box.stun else zero_dmg_text()
        log1_1 += f'\n{mob.name}({mob.cut_hp(dmg1)}/{mob.max_hp})\n{hp_gauge(mob)}'
        log2_1 += f'{mob.name}を倒した！！' if mob.now_hp<=0 else f'{mob.name}の攻撃->'
        if not mob.now_hp <= 0:
            dmg2 = round(x2 * dmg2)
            log2_1 += f"{dmg2}の{t2}" if dmg2>0 else zero_dmg_text()
            log2_1 += f'\n{user}({player.cut_hp(dmg2)}/{player.max_hp})\n{hp_gauge(player)}'

    # 戦闘処理（Player後手） #
    else:
        log1_1 += f'{mob.name}の攻撃->'
        dmg2 = round(x2 * dmg2)
        log1_1 += f"{str(dmg2)}の{t2}" if dmg2!=0 else f"{mob.name}は動けない！" if ch.id in box.stun else zero_dmg_text()
        log1_1 += f'\n{user}({player.cut_hp(dmg2)}/{player.max_hp})\n{hp_gauge(player)}'
        log2_1 += f'{user}はやられてしまった！！' if player.now_hp<=0 else f'{user}の攻撃->'
        if not player.now_hp <= 0 :
            dmg1 = round(x * dmg1)
            log2_1 += f"{str(dmg1)}の{t}" if dmg1>0 else zero_dmg_text()
            log2_1 += f'\n{mob.name}({mob.cut_hp(dmg1)}/{mob.max_hp})\n{hp_gauge(mob)}'

    battle_log = f"```diff\n{log1_1}``````diff\n{log2_1}```"
    await ch.send(content=battle_log)
    await battle_result(player, mob)





# 戦闘から離脱 #
async def reset(user, ch):
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
                    




# Magic #


async def open_magic(user,ch):
    player,mob = box.players[user.id],box.mobs[ch.id]
    if player.magic_class() == "Wolf":
        await magic_wolf.open_magic(user,ch)
    if player.magic_class() == "Armadillo":
        await magic_armadillo.open_magic(user,ch)
    if player.magic_class() == "Orca":
        await magic_orca.open_magic(user,ch)

async def use_magic(user,ch,target):
    player,mob = box.players[user.id],box.mobs[ch.id]
    if player.magic_class() == "Wolf":
        await magic_wolf.use_magic(user,ch,target)
    if player.magic_class() == "Armadillo":
        await magic_armadillo.use_magic(user,ch,target)
    if player.magic_class() == "Orca":
        await magic_orca.use_magic(user,ch,target)
