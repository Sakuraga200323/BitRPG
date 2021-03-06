import ast
import asyncio
import cv2
from datetime import datetime, timedelta, timezone
import math
import mojimoji
import os
from random import random, randint, choice, sample
import re
import sys

import discord
from discord.ext import tasks, commands
import psutil
import psycopg2, psycopg2.extras
import traceback

from sub import box, status, avatar, calc,  magic_wolf, magic_orca, magic_armadillo

JST = timezone(timedelta(hours=+9), 'JST')

item_emoji = {
    1:"<:card:786514637289947176>",
    2:"<a:hp_potion_a:786982694479200336>",
    3:"<a:mp_potion_a:786982694839124021>",
    4:"<:soul_fire:786513145010454538>",
    5:"<a:toishi_a:786974865777229864>",
    6:"<:maseki:785641515561123921>",
    7:"<a:masuisyou_a:786982694948306974>",
    8:"<a:magic_coin_a:786966211594289153>",
    9:"<:hp_full_potion:788668620074385429>",
    10:"<:mp_full_potion:788668620314116106>",
}

item_emoji_a = {
    1:"<:card:786514637289947176>",
    2:"<a:hp_potion_a:786982694479200336>",
    3:"<a:mp_potion_a:786982694839124021>",
    4:"<:soul_fire:786513145010454538>",
    5:"<a:toishi_a:786974865777229864>",
    6:"<:maseki:785641515561123921>",
    7:"<a:masuisyou_a:786982694948306974>",
    8:"<a:magic_coin_a:786966211594289153>",
    9:"<:hp_full_potion:788668620074385429>",
    10:"<:mp_full_potion:788668620314116106>",
}


client = pg = None
def first_set(c,p):
    global client, pg
    client = c
    pg = p



async def abc_training(user,ch):
    abc_list = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    player = box.players[user.id]
    abc = choice(abc_list)
    abc_index = abc_list.index(abc)
    answer_abc_index = abc_index + randint(-4,4)
    if answer_abc_index < 2: answer_abc_index = 0
    if answer_abc_index > 25: answer_abc_index = 25
    answer_abc = abc_list[answer_abc_index]
    answer_abc_moved = answer_abc_index - abc_index
    em = discord.Embed(title=f"{user}のABC.Q!!",description=f"**{mojimoji.han_to_zen(abc)}**から**{mojimoji.han_to_zen(str(answer_abc_moved))}**個目にあたるアルファベットは何ですか？ 番号で答えなさい")
    abc_list.remove(answer_abc)
    abc_list2 = sample(abc_list,3)
    abc_list2.append(answer_abc)
    answer_choices_text = ""
    answer_num = answer_abc_num = 0
    for i in sample(abc_list2,4):
        answer_num += 1
        answer_choices_text += f"\n`{mojimoji.han_to_zen(str(answer_num))}.{mojimoji.han_to_zen(i)}`"
        if i == answer_abc:
            answer_abc_num = answer_num
    em.add_field(name="選択肢",value=answer_choices_text)
    await ch.send(embed=em)
    def check(m):
        if m.author.id != user.id: return 0
        if m.channel.id != ch.id: return 0
        if not m.content in tuple("1234"): return 0
        return 1
    try:
        answer_message = await client.wait_for("message",timeout=30,check=check)
    except asyncio.TimeoutError:
        result_text = "時間切れ！"
    else:
        if int(answer_message.content) == answer_abc_num:
            exp = int(player.lv()/5)+1
            lvup = player.get_exp(exp)[1]
            result_text = f"正解！ Exp+{exp}"
            if lvup > 0:
                result_text += f"\nLvUP {player.lv()-lvup} -> {player.lv()}"
        else:
            result_text = f"不正解！ 正解は{mojimoji.han_to_zen(str(answer_abc_num))}"
    em = discord.Embed(description=result_text)
    await ch.send(embed=em)

    
