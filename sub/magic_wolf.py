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
    build_up_num = 1.5 + (player.magic_lv()/1000/100)
    dmg1 = calc.dmg(player.STR()*build_up_num,mob.defe())
    dmg2 = calc.dmg(mob.str(),player.DEFE()*0.5)
    if player.now_mp < 50:
        dmg1 = 0
        mp_text = 'MP不足で'
    else:
        mp_text = ""
    p_text = m_text = ""
    p_text += f"{player.user}の『BeeRay』->{mp_text}{dmg1}ダメージ！"
    p_text += f"\n{mob.name}({mob.cut_hp(dmg1)}/{mob.max_hp})\n{battle.hp_gauge(mob)}"
    m_text += f"{mob.name}を倒した！！" if mob.now_hp<=0 else f"{mob.name}の攻撃->"
    if not mob.now_hp <= 0:
        text = f"{str(dmg2)}ののダメージ！"
        # バフチェック
        if ch.id in box.nerf and box.nerf[ch.id] > 0:
            dmg2 *= 0.5
            dmg2 = int(dmg2)
            box.nerf[ch.id] -= 1
        if ch.id in box.stun and box.stun[ch.id] > 0:
            dmg2 = 0
            box.stun[ch.id] -= 1
        m_text += f"{text}" if dmg2>=0 else battle.zero_dmg_text()
        m_text += f'\n{player.user}({player.cut_hp(dmg2)}/{player.max_hp})\n{battle.hp_gauge(player)}'
    magic_log = f"```diff\n{p_text}``````diff\n{m_text}```"
    await mob.mob.send(content=magic_log)
    await battle.battle_result(player, mob)
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
    magic_em.add_field(name="BeeRay",Value=f"`必要熟練度： 0\nSTR{150+(player.magic_lv()/1000/100)}%の攻撃魔法`",inline=False)
    magic_em.add_field(name="StrengthRein",Value=f"`必要熟練度： 500\n未実装`",inline=False)
    magic_em.add_field(name="IgnisStrike",Value=f"`必要熟練度： 1000\n未実装`",inline=False)
    magic_em.add_field(name="StrengthRein+",Value=f"`必要熟練度： 2000\n未実装`",inline=False)
    magic_em.add_field(name="PyrobolusLacrima",Value=f"`必要熟練度： 4000\n未実装`",inline=False)
    magic_em.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=magic_em)

async def use_magic(user,ch,magic):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if magic in ["1","BeeRay","BR"]:
        await magic_1(player,mob)
    
