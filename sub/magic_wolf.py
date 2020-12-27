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

from sub import box, status, avatar, calc, battle

JST = timezone(timedelta(hours=+9), 'JST')

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



# BeeRay #
async def magic_1(player,mob):
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    ch = mob.mob
    if player.now_mp < 50:
        em=discord.Embed(description="MPが足りないようだ…")
        await ch.send(embed=em)
        return
    up_num = 1.5 + ((player.magic_lv())/100000)
    if up_num > 3: up_num = 3
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        text1 = battle.create_battle_text(player,mob,atk_word="『BeeRay』",str_up_num=up_num)
        text2 = battle.create_battle_text(mob,player)
    # 戦闘処理（Player後手） #
    else:
        text1 = battle.create_battle_text(mob,player)
        text2 = battle.create_battle_text(player,mob,atk_word="『BeeRay』",str_up_num=up_num)
    battle_log = f"```diff\n{text1}``````diff\n{text2}```"
    await ch.send(content=battle_log)
    await battle.battle_result(player, mob)
    player.magic_lv(1)
    player.cut_mp(50)

# StrengthRein #
async def magic_2(player,mob):
    ch = mob.mob
    if player.magic_lv() < 500:
        em = discord.Embed(description=f"熟練度が足りないようだ…")
        await ch.send(embed=em)
        return
    if player.now_mp < 100:
        em=discord.Embed(description="MPが足りないようだ…")
        await ch.send(embed=em)
        return
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    now_hp = player.cut_hp(int(player.max_hp/2))
    text = f"『命を力に…！』 {player.user}に{int(player.max_hp/2)}の反動"
    if 0 >= now_hp:
        text += f"\n{player.user}は死んでしまった！"
        await ch.send(f"```c\n{text}```")
        return
    up_num = 3 + ((player.magic_lv()-500)/100000)
    if up_num > 5: up_num = 5
    # 戦闘処理（Player後手） #
    text1 = battle.create_battle_text(mob,player)
    text2 = battle.create_battle_text(player,mob,atk_word="『StrengthRein』",str_up_num=up_num)
    battle_log = f"```c\n{text}``````diff\n{text1}``````diff\n{text2}```"
    await ch.send(content=battle_log)
    await battle.battle_result(player, mob)
    player.magic_lv(1)
    player.cut_mp(100)

# PowerCharge #
async def magic_3(player,mob):
    ch = mob.mob
    if player.magic_lv() < 1000:
        em = discord.Embed(description=f"熟練度が足りないようだ…")
        await ch.send(embed=em)
        return
    if player.now_mp < 200:
        em=discord.Embed(description="MPが足りないようだ…")
        await ch.send(embed=em)
        return
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    if not player.ID() in box.power_charge:
        box.power_charge[player.ID()] = 0
    box.power_charge[player.ID()] += 1
    power_charge_amount = box.power_charge[player.ID()]*50
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        text1 = f"{player.user} 『PowerCharge』->"
        text1 += f"{power_charge_amount}%分チャージ完了!"
        text2 = battle.create_battle_text(mob,player)
    # 戦闘処理（Player後手） #
    else:
        text1 = battle.create_battle_text(mob,player)
        if player.now_hp > 0:
            text2 = f"{player.user} 『PowerCharge』->"
            text2 += f"『IgnisStrike』の攻撃力が{100 + power_charge_amount}%に上昇!"
        else:
            text2 = f"{player.user} はやられてしまった…"
    battle_log = f"```diff\n{text1}``````diff\n{text2}```"
    await ch.send(content=battle_log)
    await battle.battle_result(player, mob)
    player.magic_lv(1)
    player.cut_mp(200)
    

# IgnisStrike #
async def magic_4(player,mob):
    ch = mob.mob
    if player.magic_lv() < 2000:
        em = discord.Embed(description=f"熟練度が足りないようだ…")
        await ch.send(embed=em)
        return
    if player.now_mp < 10:
        em=discord.Embed(description="MPが足りないようだ…")
        await ch.send(embed=em)
        return
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    up_num = 1 + ((player.magic_lv()-2000)/100000)
    if up_num > 5: up_num = 5
    if player.ID() in box.power_charge:
        num = box.power_charge[player.ID()]*0.5
        up_num += num
        del box.power_charge[player.ID()]
        str_up_text = f"```diff\nDischarge!! {up_num*100}%(+{num*100}%)```"
    else:
        str_up_text = ""
    # 戦闘処理（Player後手） #
    text1 = battle.create_battle_text(mob,player)
    text2 = battle.create_battle_text(player,mob,atk_word="『IgnisStrike』",str_up_num=up_num)
    battle_log = f"```diff\n{text1}```{str_up_text}```diff\n{text2}```"
    await ch.send(content=battle_log)
    await battle.battle_result(player, mob)
    player.magic_lv(1)
    player.cut_mp(10)

# MasterSpark #
async def magic_5(player,mob,final=False):
    ch = mob.mob
    if player.magic_lv() < 4000:
        em = discord.Embed(description=f"熟練度が足りないようだ…")
        await ch.send(embed=em)
        return
    if player.now_mp < 10:
        em=discord.Embed(description="MPが足りないようだ…")
        await ch.send(embed=em)
        return
    soul_fire_num = battle.pg.fetchdict(f"select item from player_tb where id = {player.ID()};")[0]["item"]["魂の焔"]
    if soul_fire_num < 32:
        em=discord.Embed(description="触媒が足りないようだ…")
        await ch.send(embed=em)
        return
    if final:
        magic_name = "FinalSpark"
        use_num = soul_fire_num
        up_num = 10 + ((player.magic_lv()-4000)/100000) + (use_num/100)
    elif not final:
        magic_name = "MasterSpark"
        use_num = 32
        up_num = 10 + ((player.magic_lv()-4000)/100000)
        if up_num > 30: up_num = 30
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    # 戦闘処理（Player後手） #
    text1 = battle.create_battle_text(mob,player)
    status.get_item(client.get_user(player.ID()),4,-use_num)
    text2 = battle.create_battle_text(player,mob,atk_word=f"『{magic_name}』",str_up_num=up_num)
    battle_log = f"```diff\n{text1}``````diff\n{text2}```"
    await ch.send(content=battle_log)
    await battle.battle_result(player, mob)
    player.magic_lv(1)
    player.cut_mp(10)

   
async def open_magic(user,ch):
    player = box.players[user.id]
    magic_em = discord.Embed(title="Player Magic Board",description="各魔法の数値は熟練度による補正を加算済みです。")
    magic_lv = player.magic_lv()
    percent_num_1 = 150+(magic_lv/1000)
    if percent_num > 300: percent_num = 300
    percent_num_2 = 300+((magic_lv-500)/1000)
    if percent_num > 500: percent_num = 500
    percent_num_4 = 100+((magic_lv-1000)/1000)
    if percent_num > 500: percent_num = 500
    if user.id in box.power_charge: percent_num4 += box.power_charge[user.id]*50
    percent_num_5 = 1000+((magic_lv-1000)/1000)
    if percent_num > 3000: percent_num = 3000
    if magic_lv >= 4000:
        soul_fire_num = battle.pg.fetchdict(f"select item from player_tb where id = {player.ID()};")[0]["item"]["魂の焔"]
        use_num = soul_fire_num
        up_num = 10 + ((magic_lv-4000)/100000) + (use_num/100)
        magic_em.add_field(
            name="`0.`FinalSpark",value=f"必要熟練度.**4000**\n消費MP.**10**\n消費触媒.**{box.items_emoji[4]}×{soul_fire_num}**\n攻撃力**{up_num*100}**%の魔法攻撃",
            inline=False)
    magic_em.add_field(
        name="`1.`BeeRay      ",value=f"必要熟練度.**0   **\n消費MP.**50 **\n攻撃力**{percent_num1}**%の攻撃魔法",
        inline=False)
    magic_em.add_field(
        name="`2.`StrengthRein",value=f"必要熟練度.**500 **\n消費MP.**100**\n攻撃力**{percent_num2}**%の攻撃魔法 後手確定 最大HPの**50**%の反動",
        inline=False)
    magic_em.add_field(
        name="`3.`PowerCharge ",value=f"必要熟練度.**1000**\n消費MP.**200**\n次に使用する『IgnisStrike』の威力が**50**%上昇",
        inline=False)
    magic_em.add_field(
        name="`4.`IgnisStrike ",value=f"必要熟練度.**2000**\n消費MP.**10 **\n攻撃力**{percent_num4}**%の攻撃魔法 『PowerCharge』毎に威力が**50**%上昇",
        inline=False)
    magic_em.add_field(
        name="`5.`MasterSpark ",value=f"必要熟練度.**4000**\n消費MP.**10 **\n消費触媒.**{box.items_emoji[4]}×32**\n攻撃力**{percent_num5}**%の魔法攻撃",
        inline=False)
    magic_em.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=magic_em)


async def use_magic(user,ch,magic):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if magic in ["0","FinalSpark","FS"]:
        await magic_5(player,mob,final=True)
    elif magic in ["1","BeeRay","BR"]:
        await magic_1(player,mob)
    elif magic in ["2","StrengthRein","SR"]:
        await magic_2(player,mob)
    elif magic in ["3","PowerCharge","PC"]:
        await magic_3(player,mob)
    elif magic in ["4","IgnisStrike","IS"]:
        await magic_4(player,mob)
    elif magic in ["5","MasterSpark","MS"]:
        await magic_5(player,mob)
