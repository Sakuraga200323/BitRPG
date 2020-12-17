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
    ch = mob.mob
    await battle.battle_start(player,mob)
    build_up_num = 1.5 + (player.magic_lv()/100000)
    if player.now_mp < 50: up_num = 0
    else: up_num = build_up_num
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        text1 = battle.create_battle_text(player,mob,atk_word="『BeeRay』",str_up_num=up_num)
        text2 = battle.create_battle_text(mob,player)
    # 戦闘処理（Player後手） #
    else:
        text1 = battle.create_battle_text(mob,player)
        text2 = battle.create_battle_text(player,mob,str_up_num=up_num)
    battle_log = f"```diff\n{text1}``````diff\n{text2}```"
    await ch.send(content=battle_log)
    await battle_result(player, mob)
    player.cut_mp(50)
    if not mp_text:
        player.magic_lv(1)
#  StrengthRein #
async def magic_2(player,mob):
    if player.magic_lv() <= 500:
        await mob.mob.send(f"<@{player.id}> の熟練度が{500 - player.magic_lv()}足りません。")
        return
    pass
# IgnisStrike #
async def magic_3(player,mob):
    if player.magic_lv() <= 1000:
        await mob.mob.send(f"<@{player.id}> の熟練度が{1000 - player.magic_lv()}足りません。")
        return
    pass
# StrengthRein+ #
async def magic_4(player,mob):
    if player.magic_lv() <= 2000:
        await mob.mob.send(f"<@{player.id}> の熟練度が{2000 - player.magic_lv()}足りません。")
        return
    pass
# PyrobolusLacrima #
async def magic_5(player,mob):
    if player.magic_lv() <= 4000:
        await mob.mob.send(f"<@{player.id}> の熟練度が{4000 - player.magic_lv()}足りません。")
        return
    pass

async def open_magic(user,ch):
    player = box.players[user.id]
    magic_em = discord.Embed(title="Player Magic Board",description="各魔法の数値は熟練度による補正を加算済みです。")
    magic_em.add_field(name="`1.`BeeRay",value=f"必要熟練度： **0**\nSTR**{150+(player.magic_lv()/1000)}**%の攻撃魔法",inline=False)
    magic_em.add_field(name="`2.`StrengthRein",value=f"`必要熟練度： 500\n未実装`",inline=False)
    magic_em.add_field(name="`3.`IgnisStrike",value=f"`必要熟練度： 1000\n未実装`",inline=False)
    magic_em.add_field(name="`4.`StrengthRein+",value=f"`必要熟練度： 2000\n未実装`",inline=False)
    magic_em.add_field(name="`5.`PyrobolusLacrima",value=f"`必要熟練度： 4000\n未実装`",inline=False)
    magic_em.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=magic_em)

async def use_magic(user,ch,magic):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if magic in ["1","BeeRay","BR"]:
        await magic_1(player,mob)
    
