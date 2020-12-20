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


async def magic_1(player,mob):
    ch = mob.mob
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    if player.now_mp < 30:
        em=discord.Embed(description="MPが不足…！")
        await ch.send(embed=em)
        return
    if random() <= 0.25:
        buff_num = 2
    else:
        buff_num = 0
    up_num = 0.8 + (player.magic_lv()/100000)
    player.magic_lv(1)
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        text1 = battle.create_battle_text(player,mob,atk_word="『DrumFang』",str_up_num=up_num,buff=buff_num)
        text2 = battle.create_battle_text(mob,player)
    # 戦闘処理（Player後手） #
    else:
        text1 = battle.create_battle_text(mob,player)
        text2 = battle.create_battle_text(player,mob,atk_word="『DrumFang』",str_up_num=up_num,buff=buff_num)
    magic_log = f"```diff\n{text1}``````diff\n{text2}```"
    await mob.mob.send(content=magic_log)
    await battle.battle_result(player, mob)
    player.magic_lv(1)
    player.cut_mp(30)

# HealPrex #
async def magic_2(player,mob):
    ch = mob.mob
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    if player.magic_lv() < 500:
        em=discord.Embed(description="魔法練度が不足…！")
        await ch.send(embed=em)
        return
    if player.now_mp < 80:
        em=discord.Embed(description="MPが不足…！")
        await ch.send(embed=em)
        return
    healing_amount = player.max_hp - player.now_hp
    if healing_amount <= 0:
        em=discord.Embed(description="まだ回復力が無いようだ…")
        await ch.send(embed=em)
        return
    players = mob.battle_players
    players.remove(player.ID())
    if players == []:
        em=discord.Embed(description="回復出来る人が居ないようだ…")
        await ch.send(embed=em)
        return
    heal_text = ""
    for id in players:
        p = box.players[id]
        p.now_hp += healing_amount
        if p.now_hp > p.max_hp: p.now_hp = p.max_hp
        heal_text += f"\n<@{p.user.id}> のHPを{healing_amount}回復！"
    em=discord.Embed(description=heal_text)
    await ch.send(embed=em)
    player.magic_lv(1)
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
    magic_em.add_field(name="`1.`DrumFang",value=f"必要熟練度.**0**\n消費MP.**30**\n攻撃力**{80+(player.magic_lv()/1000)}**%の攻撃魔法 **25**%で敵に**5**ターンNerf付与 ",inline=False)
    magic_em.add_field(name="`2.`HealPrex",value=f"必要熟練度.**500**\n消費MP.**80**\n自分が受けているダメージ量 戦闘に参加している他のプレイヤーのHPを回復",inline=False)
    magic_em.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=magic_em)

async def use_magic(user,ch,magic):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if magic in ["1","DrumFang","DM"]:
        await magic_1(player,mob)
    if magic in ["2","HealPrex","HP"]:
        await magic_2(player,mob)
    
