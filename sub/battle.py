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



client = pg = None
def first_set(c,p):
    global client, pg
    client = c
    pg = p




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
        5:(randint(1,2),mob.name in ("モノリス",'ゴールド-モノリス')),
        6:(randint(3,6),random()<=0.03),
        11:(randint(3,6),(random()<=0.05 and mob.lv()%10==0) or mob.type in ("UltraRare",)),
        13:(randint(3,6),(random()<=0.05 and mob.lv()%10==0) or mob.type in ("UltraRare",)),
        15:(randint(2,5),(random()<=0.05 and mob.lv()%100==0) or mob.type in ("UltraRare",)),
        17:(randint(2,5),(random()<=0.05 and mob.lv()%100==0) or mob.type in ("UltraRare",)),
        19:(randint(1,3),(random()<=0.05 and mob.lv()%100==0) or mob.type in ("UltraRare","UltraEro")),
        21:(randint(1,3),(random()<=0.05 and mob.lv()%100==0) or mob.type in ("UltraRare","UltraEro")),
    }
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
        guild = client.get_guild(719165196861702205)
        if  now in ['23:18']:
            exp *= 16
            await ch.send("????『幸運を。死したものより祝福を。』")
        print(f"『{mob.name}』(Lv.{mob.lv()})を{[ str(client.get_user(i)) for i in mob.battle_players]}が討伐")
        for p_id in mob.battle_players:
            p = box.players[p_id]
            EXP = exp
            member = guild.get_member(p_id)
            if member:
                user_is_special = guild.get_role(763404511318245416) in member.roles
                if user_is_special:
                    EXP += int(mob.lv()*0.25)
                user_is_nitro = guild.get_role(763359264672579605) in member.roles
                if user_is_nitro:
                    EXP += int(mob.lv()*0.25)
                user_is_gold = guild.get_role(763409546424352769) in member.roles
                if user_is_gold:
                    EXP += int(mob.lv()*0.25)
            up_exp, up_lv = p.get_exp(EXP)
            p.kill_count(1)
            p.money(money)
            if p.ID() == player.ID():
                result_desc += f"\n*<@{p_id}>*"
            else:
                result_desc += f"\n<@{p_id}>"
            result_desc += f"\n> Exp+{EXP} Cell+{money}"
            if up_lv > 0:
                result_desc += f"\n> LvUP {p.lv()-up_lv} → {p.lv()}"
            p.battle_end()
        result_em = discord.Embed(title="Result",description=result_desc,color=discord.Color.green())
        # ドロップアイテムfor #
        drop_item_text = ''
        member = guild.get_member(player.ID())
        user_is_frontier = False
        if member:
            user_is_frontier = guild.get_role(799961431536697366) in member.roles
        for id in reward_items:
            num,item_was_droped = reward_items[id]
            if item_was_droped:
                status.get_item(player.user,id,num)
                drop_item_text += f"{box.items_emoji[id]}×{num} "
            else:
                if user_is_frontier:
                    if random() <= 0.001:
                        status.get_item(player.user,id,num)
                        drop_item_text += f"(開拓者Bonus!!{box.items_emoji[id]}×{num}) "
        result_em.add_field(name=f"Drop Item",value=f"<@{user.id}>\n>>> {drop_item_text}")
        if random() <= 0.001:
            player.now_stp(500)
            result_em.add_field(name=f"Lucky Bonus",value=f"<@{user.id}>\n>>> STP+500")
        if mob.lv() % 100 == 0:
            player.money(1000)
            result_em.add_field(name=f"Last Attack Bonus",value=f"<@{user.id}>\n>>> Cell+1000")
        mob.lv(1)
        spawn_em = mob.battle_end()
        if mob.type in ("Elite","UltraRare",""):
            box.anti_magic.append(mob.ID())
            anti_magic_em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動！")
    return result_em, spawn_em, anti_magic_em



def create_battle_text(a,b,str_up_num=1,atk_word="攻撃",buff=0):
    if a.now_hp <= 0:
        if a.ID() in box.players:
            battle_text = f"{a.name} はやられてしまった"
        else:
            battle_text = f"{a.name} を倒した"
    else:
        plus_or_minus = ""
        if a.ID() in box.players:
            a_mark,b_mark = "+","-"
        else:
            a_mark,b_mark = "-","+"
        battle_text = f"{a_mark}■ {a.name} の{atk_word}"
        irregular_text = ''
        a_strength = int(a.STR()*str_up_num)
        a_id = a.ID()
        a_was_stun,a_was_nerf,a_was_fleeze = False,False,False
        if a_id in box.nerf:
            box.nerf[a_id] -= 1
            a_was_nerf = True
            a_strength = int(a_strength/2)
            irregular_text = f'\n┣━ {a.name} は力が入らない！ (Nerf×{box.nerf[a_id]}, Strength50%)'
            if box.nerf[a_id] <= 0:
                del box.nerf[a_id]
        if a_id in box.stun:
            box.stun[a_id] -= 1
            a_strength = 0
            a_was_stun = True
            irregular_text = f'\n┣━ {a.name} は痺れて動けない！ (Stun×{box.stun[a_id]}, Strength0%)'
            if box.stun[a_id] <= 0:
                del box.stun[a_id]
        if a_id in box.fleez:
            a_strength = 0
            irregular_text = f'\n┣━ {a.name} は凍って動けない！ (Strength0%)'
            a_was_fleeze = True
        if a_strength != 0:
            if b.ID() in box.fleez:
                box.fleez.remove(b.ID())
            if random() <= 0.05:
                a_strength *= 5
                irregular_text += '\n┣━ クリティカルヒット！ (Strength500%)'
            elif random() <= min(((b.AGI()/a.AGI() - 1) if a.AGI()>0 else 0), 0.75) and not b.ID() in box.fleez:
                if b.ID() in box.stun:
                    if random() <= 0.5:
                        a_strength = 0
                        irregular_text += f'\n┣━ {b.name} はギリギリ避けた！ (Strength0%)'
                else:
                    a_strength = 0
                    irregular_text += f'\n┣━ {b.name} は華麗に避けた！ (Strength0%)'
            elif a_id in box.atk_switch:
                b_id = box.atk_switch[a_id]
                if b_id in box.players:
                    b = box.players[b_id]
                    del box.atk_switch[a_id]
                    irregular_text += f"\n┣━ {b.name} が攻撃を防いだ！ (Target{b.name})"
        battle_text += irregular_text
        b_dmg,b_now_def,b_now_hp = b.damaged(a_strength)
        battle_text += f'\n┗━ {b_dmg}ダメージ (Damage-{a_strength-b_dmg})'
        if a_was_stun and not a_id in box.stun:
            battle_text = battle_text.replace('┗','┣')
            battle_text += '\n┗━ Stun から回復'
        if a_was_nerf and not a_id in box.nerf:
            battle_text = battle_text.replace('┗','┣')
            battle_text += '\n┗━ Nerf から回復'
        if buff in [1,2] and not a.ID() in box.stun:
            buff_dict = {1:"Stun",2:"Nerf"}
            battle_text = battle_text.replace('┗','┣')
            battle_text += f"\n┗━ {buff_dict[buff]} 付与"
            if buff == 1:
                box.stun[b.ID()] = 3
            if buff == 2:
                box.nerf[b.ID()] = 5
        battle_text += f"\n\n{b_mark}■ {b.name} の状態\n{old_def_gauge(b_now_def,b.DEFE())}\n{old_hp_gauge(b_now_hp,b.max_hp)}"
    return battle_text

gauge_design = '|'

# HPゲージ作成関数 #
def old_hp_gauge(a,b):
    num = int((a/b)*20)
    gauge_1 = (num)*gauge_design
    gauge_1 = f"{gauge_1:<20}"
    return (('-┏HP ╋' if num<5 else "+┏HP ┣")) + ("--- You Are Dead ---" if a<=0 else gauge_1) + '┫' + f"\n ┗━━━({a}/{b})"
# DEFゲージ作成関数 #
def old_def_gauge(a,b):
    num = int((a/b)*20)
    gauge_1 = (num)*gauge_design
    gauge_1 = f"{gauge_1:<20}"
    return (('-┏DEF╋' if num<5 else "+┏DEF┣")) + ("---- Break Down ----" if a<=0 else gauge_1) + '┫' + f"\n ┗━━━({a}/{b})"


# ダメージがない場合のメッセージ #
def zero_dmg_text():
    text = ("華麗に躱した","完全に防いだ","当たらなかった","効かなかったようだ","無駄無駄無駄無駄無駄ァ！")
    return choice(text)


# 戦闘 #
async def cbt_proc(user, ch):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    start_result = await battle_start(player,mob)
    if not start_result:
        return
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        text1 = create_battle_text(player,mob)
        text2 = create_battle_text(mob,player)

    # 戦闘処理（Player後手） #
    else:
        text1 = create_battle_text(mob,player)
        text2 = create_battle_text(player,mob)

    battle_log = f"```diff\n{text1}``````diff\n{text2}```"
    result_em,spawn_em,anti_magic_em = await battle_result(player, mob)
    await ch.send(content=battle_log,embed=result_em)
    if spawn_em:await ch.send(embed=spawn_em)
    if anti_magic_em:await ch.send(embed=anti_magic_em)


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
    if mob.type in ("Elite","UltraRare","Catastrophe"):
        if not mob.ID() in box.anti_magic:
           box.anti_magic.append(mob.ID())
        anti_magic_em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動！")
        await ch.send(embed=anti_magic_em)
                    








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
        if player.magic_class() == "Orca":
            if not target in ['3','GinHex','GH']:
                em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動中 魔法が使えない！")
                await ch.send(embed=em)
                return
        else:
            em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動中 魔法が使えない！")
            await ch.send(embed=em)
            return
    if player.magic_class() == "Wolf":
        await magic_wolf.use_magic(user,ch,target)
    if player.magic_class() == "Armadillo":
        await magic_armadillo.use_magic(user,ch,target)
    if player.magic_class() == "Orca":
        await magic_orca.use_magic(user,ch,target)
