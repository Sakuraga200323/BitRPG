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
    up_num = 1.5 + (player.magic_lv()/100000)
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
    up_num = 3 + (player.magic_lv()/100000)
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
    if not player.ID() in box.str_charge:
        box.power_charge[player.ID()] = 0
    box.power_charge[player.ID()] += 1
    power_charge_amount = box.power_charge[player.ID()]*50
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        text1 = f"{player.user} 『PowerCharge』->"
        text1 += f"『IdnisStrike』の攻撃力が{100 + power_charge_amount}%に上昇!"
        text2 = battle.create_battle_text(mob,player)
    # 戦闘処理（Player後手） #
    else:
        text1 = battle.create_battle_text(mob,player)
        if player.now_hp > 0:
            text2 = f"{player.user} 『PowerCharge』->"
            text2 += f"『IdnisStrike』の攻撃力が{100 + power_charge_amount}%に上昇!"
        else:
            text2 = f"{player.user} はやられてしまった…"
    battle_log = f"```diff\n{text1}``````diff\n{text2}```"
    await ch.send(content=battle_log)
    await battle.battle_result(player, mob)
    player.magic_lv(1)
    player.cut_mp(200)
    

# IgnisStrike #
async def magic_4(player,mob):
    if player.magic_lv() < 2000:
        await mob.mob.send(f"<@{player.id}> の熟練度が{2000 - player.magic_lv()}足りません。")
        return

# PyrobolusLacrima #
async def magic_5(player,mob):
    if player.magic_lv() < 4000:
        await mob.mob.send(f"<@{player.id}> の熟練度が{4000 - player.magic_lv()}足りません。")
        return

async def open_magic(user,ch):
    player = box.players[user.id]
    magic_em = discord.Embed(title="Player Magic Board",description="各魔法の数値は熟練度による補正を加算済みです。")
    magic_em.add_field(name="`1.`BeeRay",value=f"必要熟練度.**0**\n消費MP.**50**\n攻撃力**{150+(player.magic_lv()/1000)}**%の攻撃魔法",inline=False)
    magic_em.add_field(name="`2.`StrengthRein",value=f"必要熟練度.**500**\n消費MP.**100**\n攻撃力**{300+(player.magic_lv()/1000)}**%の攻撃魔法 後手確定 最大HPの**50**%の反動",inline=False)
    magic_em.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=magic_em)

async def use_magic(user,ch,magic):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if magic in ["1","BeeRay","BR"]:
        await magic_1(player,mob)
    if magic in ["2","StrengthRein","SR"]:
        await magic_2(player,mob)
    if magic in ["3","PowerCharge","PC"]:
        await magic_3(player,mob)
    
