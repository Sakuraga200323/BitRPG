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



# StunRain #
async def magic_1(player,mob):
    ch = mob.mob
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    build_up_num = 0.8 + (player.magic_lv()/100000)
    if random() <= 0.5:
        buff_num = 1
    else:
        buff_num = 0
    if player.now_mp < 80:
        up_num = buff_num = 0
        em=discord.Embed(description="MPが不足…！")
        await ch.send(embed=em)
    else:
        up_num = build_up_num
        player.magic_lv(1)
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        text1 = battle.create_battle_text(player,mob,atk_word="『StunRain』",str_up_num=up_num,buff=buff_num)
        text2 = battle.create_battle_text(mob,player)
    # 戦闘処理（Player後手） #
    else:
        text1 = battle.create_battle_text(mob,player)
        text2 = battle.create_battle_text(player,mob,atk_word="『StunRain』",str_up_num=up_num,buff=buff_num)
    magic_log = f"```diff\n{text1}``````diff\n{text2}```"
    await mob.mob.send(content=magic_log)
    await battle.battle_result(player, mob)
    player.cut_mp(80)
# PalePiscis #
async def magic_2(player,mob):
    ch = mob.mob
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    if player.magic_lv < 500:
        em=discord.Embed(description="魔法練度が不足…！")
        await ch.send(embed=em)
        return
    if player.now_mp < 150:
        em=discord.Embed(description="MPが不足…！")
        await ch.send(embed=em)
        return
    build_up_num = 1.1 + (player.magic_lv()/100000)
    if mob.ID() in box.stun:
        build_up_num += 0.5
        del box.stun[mob.ID()]
    if random() <= 0.5:
        buff_num = 1
    else:
        buff_num = 0
    up_num = build_up_num
    player.magic_lv(1)
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        text1 = battle.create_battle_text(player,mob,atk_word="『PalePiscis』",str_up_num=up_num,buff=buff_num)
        text2 = battle.create_battle_text(mob,player)
    # 戦闘処理（Player後手） #
    else:
        text1 = battle.create_battle_text(mob,player)
        text2 = battle.create_battle_text(player,mob,atk_word="『PalePiscis』",str_up_num=up_num,buff=buff_num)
    magic_log = f"```diff\n{text1}``````diff\n{text2}```"
    await mob.mob.send(content=magic_log)
    await battle.battle_result(player, mob)
    player.cut_mp(80)
# IgnisStrike #
async def magic_3(player,mob):
    pass
# StrengthRein+ #
async def magic_4(player,mob):
    pass
# PyrobolusLacrima #
async def magic_5(player,mob):
    pass

async def open_magic(user,ch):
    player = box.players[user.id]
    magic_em = discord.Embed(title="Player Magic Board",description="各魔法の数値は熟練度による補正を加算済みです。")
    magic_em.add_field(name="`1.`StunRain",value=f"必要熟練度.**0**\n消費MP.**80**\n攻撃力**{80+(player.magic_lv()/1000)}**%の攻撃魔法 **25**%で敵に**3**ターンStun付与 ",inline=False)
    magic_em.add_field(name="`2.`PalePiscis",value=f"必要熟練度.**500**\n消費MP.**150**\n攻撃力**{110+(player.magic_lv()/1000)}**%の攻撃魔法 敵がスタン状態の時攻撃力**{160+(player.magic_lv()/1000)}**%",inline=False)
    magic_em.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=magic_em)

async def use_magic(user,ch,magic):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if magic in ["1","StunRain","SR"]:
        await magic_1(player,mob)
    
