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
            em = discord.Embed(description=f"<@{user.id}> は現在『{channel.mention}』で戦闘中")
            await ch.send(embed=em)
            return False
        em = discord.Embed(description=f"<@{user.id}> が認識できないチャンネルで戦闘中 データの上書き開始")
        await ch.send(embed=em)
        player.battle_end()
        if player.battle_start(ch.id):
            em = discord.Embed(description=f"上書き完了 戦闘に参加")
            await ch.send(embed=em)
        else:
            em = discord.Embed(description=f"上書き失敗 戦闘に参加できていません")
            await ch.send(embed=em)
            return False
    if player.now_hp <= 0:
        em = discord.Embed(description=f"<@{user.id}> は既に死亡しています")
        await ch.send(embed=em)
        return False
    mob.player_join(user.id)
    return True





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
    anti_magic_em = None
    if mob.now_hp <= 0 :
        if mob.ID() in box.anti_magic:
            box.anti_magic.remove(mob.ID())
        if mob.mob.id in box.nerf:
            del box.nerf[mob.mob.id]
        if mob.mob.id in box.stun:
            del box.stun[mob.mob.id]
        result_desc = ""
        now = datetime.now(JST).strftime("%H:%M")
        exp, money = mob.reward()[0]+1, int(mob.reward()[1]/len(mob.battle_players))
        if  now in ['23:18']:
            exp *= 16
            await ch.send("????『幸運を。死したものより祝福を。』")
        print("戦闘参加していたPlayer: ",mob.battle_players)
        for p_id in mob.battle_players:
            p = box.players[p_id]
            up_exp, up_lv = p.get_exp(exp)
            p.kill_count(1)
            p.money(money)
            result_desc += f"\n<@{p_id}>"
            result_desc += f"\n> Exp+{exp} Cell+{money}"
            if up_lv > 0:
                result_desc += f"\n> LvUP {p.lv()-up_lv} -> {p.lv()}"
            drop_item_text = ""
            # ドロップアイテムfor #
            for id in reward_items:
                num,item_was_droped = reward_items[id]
                if item_was_droped:
                    status.get_item(user,id,num)
                    drop_item_text += f"{item_emoji_a[id]}×{num} "
            result_desc += f"\n> DropItem： {'-' if not drop_item_text else drop_item_text}"
            p.battle_end()
        if random() <= 0.01 and mob.lv() > player.lv():
            player.now_stp(mob.lv())
            stp_em = discord.Embed(description=f"<@{user.id}> STP+{mob.lv()}")
        result_em = discord.Embed(title="Result",description=result_desc,color=discord.Color.green())
        mob.lv(1)
        spawn_em = mob.battle_end()
        if mob.type in ("Elite","UltraRare",""):
            box.anti_magic.append(mob.ID())
            anti_magic_em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動！")
    for em in (result_em, stp_em, item_em, spawn_em, anti_magic_em):
        if em : await ch.send(embed=em)



def create_battle_text(a,b,str_up_num=1,atk_word="攻撃",buff=0):
    if a.now_hp <= 0:
        if a.ID() in box.players:
            text = f"{a.name}はやられてしまった"
        else:
            text = f"{a.name}を倒した"
    else:
        text = f"+ {a.name} {atk_word}->"
        if a.ID() in box.atk_switch and b.ID() in box.players:
            b = box.players[box.atk_switch[a.ID()]]
            del box.atk_switch[a.ID()]
            text += f"{b.name}が攻撃を防いだ！ "
        if a.ID in box.players:
            if b.now_defe > a.STR():
                no_dmg_text = f"防がれた！"
            else:
                no_dmg_text = f"避けるなぁぁぁぁぁ！"
        else:
            if b.now_defe > a.STR():
                no_dmg_text = f"防ぎきった！"
            else:
                no_dmg_text = f"全力回避！"
        if a.ID() in box.stun or a.ID() in box.nerf:
            if a.ID() in box.stun:
                dmg,now_defe,now_hp = 0,b.now_defe,b.now_hp
                text += f"動けない！"
                box.stun[a.ID()] -= 1
                if box.stun[a.ID()] <= 0:
                    text += " Stunから回復した！"
                    del box.stun[a.ID()]
            elif a.ID() in box.nerf:
                if random() <= 0.05:
                    dmg,now_defe,now_hp = b.damaged(a.STR()*str_up_num)
                    if dmg <= 0: text += no_dmg_text 
                    else: text += f"{dmg}の弱クリティカルヒット"
                else:
                    dmg,now_defe,now_hp = b.damaged(a.STR()/2*str_up_num)
                    if dmg <= 0: text += no_dmg_text
                    else: text += f"{dmg}の弱ダメージ"
                box.nerf[a.ID()] -= 1
                if box.nerf[a.ID()] <= 0:
                    text += " Nerfから回復した！"
                    del box.nerf[a.ID()]
            if a.ID() in box.stun and a.ID() in box.nerf:
                dmg,now_defe,now_hp = 0,b.now_defe,b.now_hp
                text += f"動けない！"
                box.stun[a.ID()] -= 1
                if box.stun[a.ID()] <= 0:
                    text += " Nerfから回復した！"
                    del box.stun[a.ID()]
        elif not a.ID() in box.stun:
            if random() <= 0.05:
                dmg,now_defe,now_hp = b.damaged(a.STR()*2*str_up_num)
                if dmg <= 0: text += no_dmg_text
                else: text += f"{dmg}のクリティカルヒット"
            else:
                dmg,now_defe,now_hp = b.damaged(a.STR()*str_up_num)
                if dmg <= 0: text += no_dmg_text
                else: text += f"{dmg}のダメージ"
        if buff in [1,2] and not a.ID() in box.stun:
            buff_dict = {1:"Stun",2:"Nerf"}
            text += f" {buff_dict[buff]}付与"
            if buff == 1:
                box.stun[b.ID()] = 3
            if buff == 2:
                box.nerf[b.ID()] = 5
        text += f"\n< {b.name} >\n{old_def_gauge(now_defe,b.DEFE())}\n{old_hp_gauge(b.now_hp,b.max_hp)}"
    return text

# HPゲージ作成関数 #
def old_hp_gauge(a,b):
    num = int((a/b)*20)
    guage_1 = ((num)*"|")+((20-num)*" ")
    return ('-HP :[' if num<5 else "+HP :[") + ("-"*20 if a<=0 else guage_1) + ']' + f"\n     ({a}/{b})"
# DEFゲージ作成関数 #
def old_def_gauge(a,b):
    num = int((a/b)*20)
    guage_1 = ((num)*"|")+((20-num)*" ")
    return ('-DEF:[' if num<5 else "+DEF:[") + ("-"*20 if a<=0 else guage_1) + ']' + f"\n     ({a}/{b})"
# HPゲージ作成関数 #
def hp_gauge(avatar):
    num = int((avatar.now_hp/avatar.max_hp)*20)
    guage_1 = ((num)*"|")+((20-num)*" ")
    return ('-HP :[' if num<5 else "+HP :[") + ("-"*20 if avatar.now_hp<=0 else guage_1) + ']'
# DEFゲージ作成関数 #
def def_gauge(avatar):
    num = int((avatar.now_defe/avatar.max_defe)*20)
    guage_1 = ((num)*"|")+((20-num)*" ")
    return ('-DEF:[' if num<5 else "+DEF:[") + ("-"*20 if avatar.now_defe<=0 else guage_1) + ']'


# ダメージがない場合のメッセージ #
def zero_dmg_text():
    text = ("華麗に躱した","完全に防いだ","当たらなかった","効かなかったようだ","無駄無駄無駄無駄無駄ァ！")
    return choice(text)

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
        await ch.send(f"戦闘に参加していなかったのでHPを全回復しました。")
        return
    now_ch = client.get_channel(player.battle_ch)
    if player.battle_ch != ch.id:
        await ch.send(f"<@{player.user.id}> は現在『{now_ch.mention}』で戦闘中です。")
        return
    mob.battle_end()
    if player.ID() in box.power_charge:
        del box.power_charge[player.ID()]
    if mob.ID() in box.stun:
        del box.stun[mob.ID()]
    if mob.ID() in box.nerf:
        del box.nerf[mob.ID()]
    await ch.send(embed = mob.spawn())
    if mob.type in ("Elite","UltraRare",""):
        box.anti_magic.append(mob.ID())
        anti_magic_em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動！")
        await ch.send(embed=anti_magic_em)
                    



# 戦闘 #
async def cbt_proc(user, ch):
    player,mob = box.players[user.id],box.mobs[ch.id]
    start_check = await battle_start(player, mob)
    if start_check is False: return

    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        text1 = create_battle_text(player,mob)
        text2 = create_battle_text(mob,player)

    # 戦闘処理（Player後手） #
    else:
        text1 = create_battle_text(mob,player)
        text2 = create_battle_text(player,mob)

    battle_log = f"```diff\n{text1}``````diff\n{text2}```"
    await ch.send(content=battle_log)
    await battle_result(player, mob)






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
    if ch.id in box.anti_magic:
        if player.magic_class() != "Orca":
            em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動中 魔法が使えない！")
            await ch.send(embed=em)
            return
        if not target in ['3','GinHex','GH']:
            em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動中 魔法が使えない！")
            await ch.send(embed=em)
            return
    if player.magic_class() == "Wolf":
        await magic_wolf.use_magic(user,ch,target)
    if player.magic_class() == "Armadillo":
        await magic_armadillo.use_magic(user,ch,target)
    if player.magic_class() == "Orca":
        await magic_orca.use_magic(user,ch,target)
