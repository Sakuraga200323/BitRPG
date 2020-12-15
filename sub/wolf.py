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
async def magci_1(player,mob):
    await battle.battle_start(player,mob)
    dmg1 = calc.dmg(player.STR()*2,mob.defe())
    dmg2 = calc.dmg(mob.str(),player.DEFE()*0.8)
    if player.now_mp < 50:
        dmg = 0
    p_text = m_text = ""
    p_text += f"{player.user}の『BeeRay』->{dmg1}ダメージ！"
    p_text += f"\n{mob.name}({mob.cut_hp(dmg1)}/{mob.max_hp})\n{battle.hp_gauge(mob)}"
    m_text += f"{mob.name}を倒した！！" if mob.now_hp<=0 else f"{mob.name}の攻撃->"
    if not mob.now_hp <= 0:
        m_text += f"{str(dmg2)}の{t2}" if dmg2>=0 else battle.zero_dmg_text()
        m_text += f'\n{player.user}({player.cut_hp(dmg2)}/{player.max_hp})\n{hp_gauge(player)}'
    magic_log = f"```diff\n{p_text}``````diff\n{m_text}```"
    await mob.mob.send(content=magic_log)
    await battle.battle_result(player, mob)
    player.cut_mp(50)
#  StrengthRein #
async def magci_2(player,mob):
    pass
# IgnisStrike #
async def magci_3(player,mob):
    pass
# StrengthRein+ #
async def magci_4(player,mob):
    pass
# PyrobolusLacrima #
async def magci_5(player,mob):
    pass



async def use_magic(user,ch,magic):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if magic in [1,"BeeRay","BR"]:
        await magic_1(player,mob)
    
