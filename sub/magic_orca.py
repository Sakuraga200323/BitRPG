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
    if player.magic_lv() < 0:
        em=discord.Embed(description="魔法練度が不足…！")
        await ch.send(embed=em)
        return
    if player.now_mp < 80:
        em=discord.Embed(description="MPが不足…！")
        await ch.send(embed=em)
        return
    if random() <= 0.5:
        buff_num = 1
    else:
        buff_num = 0
    up_num = min(0.8 + (player.magic_lv()/100000),2)
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        player.magic_lv(1)
        player.cut_mp(80)
        text1 = battle.create_battle_text(player,mob,atk_word="『StunRain』",str_up_num=up_num,buff=buff_num)
        if mob.now_hp > 0:
            text2 = battle.create_battle_text(mob,player)
        else:
            text2 = f'{mob.name}を倒した！'
    # 戦闘処理（Player後手） #
    else:
        text1 = battle.create_battle_text(mob,player)
        if player.now_hp > 0:
            player.magic_lv(1)
            player.cut_mp(80)
            text2 = battle.create_battle_text(player,mob,atk_word="『StunRain』",str_up_num=up_num,buff=buff_num)
        else:
            text2 = f'{player.user}はやられてしまった…'
    magic_log = f"```diff\n{text1}``````diff\n{text2}```"
    await mob.mob.send(content=magic_log)
    await battle.battle_result(player, mob)

# PalePiscis #
async def magic_2(player,mob):
    magic_name = "PalePiscis"
    ch = mob.mob
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    if player.magic_lv() < 500:
        em=discord.Embed(description="魔法練度が不足…！")
        await ch.send(embed=em)
        return
    if player.now_mp < 150:
        em=discord.Embed(description="MPが不足…！")
        await ch.send(embed=em)
        return
    up_num = min(2 + ((player.magic_lv()-500)/100000),400)
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        if mob.ID() in box.stun:
            up_num += 0.5
        player.magic_lv(1)
        player.cut_mp(150)
        text1 = battle.create_battle_text(player,mob,atk_word=f"『{magic_name}』",str_up_num=up_num)
        if mob.now_hp > 0:
            text2 = battle.create_battle_text(mob,player)
        else:
            text2 = f'{mob.name}を倒した！'
    # 戦闘処理（Player後手） #
    else:
        text1 = battle.create_battle_text(mob,player)
        if mob.ID() in box.stun:
            up_num += 0.5
        if player.now_hp > 0:
            player.magic_lv(1)
            player.cut_mp(150)
            text2 = battle.create_battle_text(player,mob,atk_word=f"『{magic_name}』",str_up_num=up_num)
        else:
            text2 = f'{player.user}はやられてしまった…'
    magic_log = f"```diff\n{text1}``````diff\n{text2}```"
    await mob.mob.send(content=magic_log)
    await battle.battle_result(player, mob)

# GinHex #
async def magic_3(player,mob):
    magic_name = "GinHex"
    ch = mob.mob
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    if player.magic_lv() < 1000:
        em=discord.Embed(description="魔法練度が不足…！")
        await ch.send(embed=em)
        return
    if player.now_mp < 300:
        em=discord.Embed(description="MPが不足…！")
        await ch.send(embed=em)
        return
    magic_text = ''
    if mob.ID() in box.anti_magic:
        del box.anti_magic[mob.ID()]
        em=discord.Embed(description=f"{mob.name}のアンチマジックリエアをレジスト")
        await ch.send(embed=em)
        player.magic_lv(1)
        player.cut_mp(300)
        magic_text += '\nアンチマジックエリアをレジスト！'
    percent = min(0.25 + ((player.magic_lv()-500)/100000),0.75)
    if random.random() <= percent:
        box.stun[mob.ID()] = 3
        magic_text += f'\n{mob.name}に3ターンのStunを付与！'
    if random.random() <= percent:
        box.nerf[mob.ID()] = 3
        magic_text += f'\n{mob.name}に3ターンのNerfを付与！'
    if magic_text == '':
        magic_text = '何も起きなかった…'
    em=discord.Embed(description=magic_text)
    await ch.send(embed=em)
    return

# ImmortalRecover #
async def magic_4(player,mob):
    ch = mob.mob
    start_check = await battle.battle_start(player,mob)
    if start_check is False: return
    if player.magic_lv() < 2000:
        em=discord.Embed(description="魔法練度が不足…！")
        await ch.send(embed=em)
        return
    if player.now_mp < 600:
        em=discord.Embed(description="MPが不足…！")
        await ch.send(embed=em)
        return
    players = mob.battle_players
    players.remove(player.ID())
    if players == []:
        em=discord.Embed(description="回復出来る人が居ないようだ…")
        await ch.send(embed=em)
        return
    recover_text = ""
    for id in players:
        p = box.players[id]
        if p.now_hp <= 0: p.now_hp = 1
        recover_text += f"\n<@{p.user.id}> をHP1で強制復活！"
    em=discord.Embed(title="HealPrex",description=heal_text)
    await ch.send(embed=em)
    player.magic_lv(1)
    player.cut_mp(80)

# PyrobolusLacrima #
async def magic_5(player,mob):
    pass

async def open_magic(user,ch):
    player = box.players[user.id]
    magic_lv = player.magic_lv()
    use_num = battle.pg.fetchdict(f"select item from player_tb where id = {player.ID()};")[0]["item"]["魂の焔"]
    percent_num_0 = 1000 + ((magic_lv-4000)/1000) + use_num
    percent_num_1 = min(80+(magic_lv/1000),300)
    percent_num_2 = min(200+((magic_lv-500)/1000),400)
    percent_num_3 = min(0.25 + ((player.magic_lv()-500)/100000),0.75)*100
    percent_num_4 = min(100+((magic_lv-2000)/1000),800) + (box.power_charge[user.id]*50 if user.id in box.power_charge else 0)
    percent_num_5 = min(1000+((magic_lv-4000)/1000),3000)
    magic_tuple = (
       # ('None',4000,
       #     f'必要熟練度.**4000**\n消費MP.**10 **\n消費触媒.**{box.items_emoji[4]}×{use_num}**\nStrength**{percent_num_0:.2f}**% 後手確定'),
        ('StunRain',0,
            f'必要熟練度.**0   **\n消費MP.**80 **\nStrength**{percent_num_1:.2f}**%'),
        ('PainPiscis',500,
            f'必要熟練度.**500 **\n消費MP.**150**\nStrength**{percent_num_2:.2f}**% 対象がStun状態の時Strength倍率+50%'),
        ('GinHex',1000,
            f'必要熟練度.**1000**\n消費MP.**300**\nアンチマジックエリアをレジスト **{percent_num_3:.2f}**%で敵に3ターンのStun付与 **{percent_num_3:.2f}**%で敵に3ターンのNerf付与'),
        ('ImmortalRecover',2000,
            f'必要熟練度.**2000**\n消費MP.**600**\n死亡している全味方をHP**1**で強制復活'),
       # ('MasterSpark ',4000,
       #     f'必要熟練度.**4000**\n消費MP.**10 **\n消費触媒.**{box.items_emoji[4]}×32**\nStrength**{percent_num_5:.2f}**% 後手確定'),
    )
    magic_em = discord.Embed(title="Player Magic Board",description=f"魔法熟練度.**{magic_lv}**\n小数点第2位未満四捨五入")
    for magic,num in zip(magic_tuple,range(1,6)):
        magic_name = magic[0]
        magic_info = '>>> '+magic[2]
        if magic_lv < magic[1]:
            magic_name = f'`{magic[0]}`'
            magic_info = f"`{magic[2].replace('*','')}`"
        magic_em.add_field(name=f'`{num}.`'+magic_name,value=magic_info,inline=False)
    magic_em.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=magic_em)

async def use_magic(user,ch,magic):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    if magic in ["1","StunRain","SR"]:
        await magic_1(player,mob)
    if magic in ["2","PalePiscis","PP"]:
        await magic_2(player,mob)
    if magic in ["3","GinHex","GH"]:
        await magic_3(player,mob)
    
