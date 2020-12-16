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



# StunFin #
async def magic_1(player,mob):
    ch = mob.mob
    await battle.battle_start(player,mob)
    build_up_num = 0.8 + (player.magic_lv()/1000/100)
    dmg1 = calc.dmg((player.STR()*build_up_num),mob.defe())
    dmg2 = calc.dmg(mob.str(),player.DEFE())
    if player.now_mp < 80:
        dmg1 = 0
        mp_text = 'MP不足で'
    else:
        mp_text = ""
    p_text = m_text = ""
    p_text += f"{player.user}の『StunFin』->{mp_text}{dmg1}ダメージ！"
    if random() <= 0.50 and not mp_text:
        p_text += f"{mob.name}がスタン！"
        box.stun[mob.mob.id] = 3
    p_text += f"\n{mob.name}({mob.cut_hp(dmg1)}/{mob.max_hp})\n{battle.hp_gauge(mob)}"
    m_text += f"{mob.name}を倒した！！" if mob.now_hp<=0 else f"{mob.name}の攻撃->"
    if not mob.now_hp <= 0:
        text = f"{str(dmg2)}のダメージ！"
        # バフチェック
        if ch.id in box.nerf:
            dmg2 *= 0.5
            dmg2 = int(dmg2)
            box.nerf[ch.id] -= 1
        if ch.id in box.stun:
            dmg2 = 0
            text = f"{mob.name}は動けない！"
            box.stun[ch.id] -= 1
        m_text += f"{text}"
        m_text += f'\n{player.user}({player.cut_hp(dmg2)}/{player.max_hp})\n{battle.hp_gauge(player)}'
    magic_log = f"```diff\n{p_text}``````diff\n{m_text}```"
    await mob.mob.send(content=magic_log)
    await battle.battle_result(player, mob)
    player.cut_mp(80)
    if not mp_text:
        player.magic_lv(1)
#  StrengthRein #
async def magic_2(player,mob):
    pass
# IgnisStrike #
async def magic_3(player,mob):
    pass
# StrengthRein+ #
async def magic_4(player,mob):
    pass
# PyrobolusLacrima #
async def magic_5(player,mob):
    pass



async def use_magic(user,ch,magic):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if magic in ["1","StunFin","ST"]:
        await magic_1(player,mob)
    
