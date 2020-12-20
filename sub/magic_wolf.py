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
    if player.now_mp < 50:
        em=discord.Embed(description="MPが足りないようだ…")
        await ch.send(embed=em)
        return
    ch = mob.mob
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    build_up_num = 1.5 + (player.magic_lv()/100000)
    up_num = build_up_num
    player.magic_lv(1)
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
    up_num = 2 + (player.magic_lv()/100000)
    player.magic_lv(1)
    # 戦闘処理（Player後手） #
    text1 = battle.create_battle_text(mob,player)
    text2 = battle.create_battle_text(player,mob,atk_word="『StrengthRein』",str_up_num=up_num)
    text3 = f"{player.user}に{int(player.max_hp/5)}の反動"
    if 0 >= player.cut_hp(int(player.max_hp/5)):
        text3 += "\n{player.user}は死んでしまった！"
    battle_log = f"```diff\n{text1}``````diff\n{text2}``````css\n{text3}```"
    await ch.send(content=battle_log)
    await battle.battle_result(player, mob)
    player.cut_mp(100)

# IgnisStrike #
async def magic_3(player,mob):
    if player.magic_lv() < 1000:
        await mob.mob.send(f"<@{player.id}> の熟練度が{1000 - player.magic_lv()}足りません。")
        return
    pass

# StrengthRein+ #
async def magic_4(player,mob):
    if player.magic_lv() < 2000:
        await mob.mob.send(f"<@{player.id}> の熟練度が{2000 - player.magic_lv()}足りません。")
        return
    pass

# PyrobolusLacrima #
async def magic_5(player,mob):
    if player.magic_lv() < 4000:
        await mob.mob.send(f"<@{player.id}> の熟練度が{4000 - player.magic_lv()}足りません。")
        return
    pass

async def open_magic(user,ch):
    player = box.players[user.id]
    magic_em = discord.Embed(title="Player Magic Board",description="各魔法の数値は熟練度による補正を加算済みです。")
    magic_em.add_field(name="`1.`BeeRay",value=f"MagicLv.**0** MP.**50**\n攻撃力**{150+(player.magic_lv()/1000)}**%の攻撃魔法",inline=False)
    magic_em.add_field(name="`2.`StrengthRein",value=f"未実装",inline=False)
    magic_em.add_field(name="`3.`IgnisStrike",value=f"未実装",inline=False)
    magic_em.add_field(name="`4.`StrengthRein+",value=f"未実装",inline=False)
    magic_em.add_field(name="`5.`PyrobolusLacrima",value=f"未実装",inline=False)
    magic_em.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=magic_em)

async def use_magic(user,ch,magic):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if magic in ["1","BeeRay","BR"]:
        await magic_1(player,mob)
    if magic in ["2","StrengthRein","SR"]:
        await magic_2(player,mob)
    
