import ast
import asyncio
import cv2
from datetime import datetime, timedelta, timezone
import math
import os
from random import random, randint, choice, shuffle
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


pg = None
client = None



async def abc_training(user,ch):
    abc_list = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    player = box.players[user.id]
    abc = choice(abc_list)
    abc_index = abc_list.index(abc)
    answer_abc_index = abc_index + randint(-4,4)
    if answer_abc_index < 0: answer_abc_index = 0
    if answer_abc_index > 27: answer_abc_index = 27
    answer_abc = abc_list[answer_abc_index]
    answer_abc_moved = answer_abc_index - abc_index
    em = discord.Embed(title="ABC.Q!!",description=f"**{abc}**から**{answer_abc_moved}**個目にあたるアルファベットは何ですか？ 番号で答えなさい")
    abc_list2 = sample(abc_list.remove(abc),3)
    answer_choices_text = ""
    answer_num = 0
    for i in abc_list (abc_list2.append(answer_abc)):
        answer_num += 1
        answer_choices_text += f"\n`{answer_num}.`*{i}*"
    em.add_field(name="選択肢",value=answer_choices_text)
    await ch.send(embed=em)
    def check(m):
        if m.author.id != user.id: return 0
        if m_channel.id != user.id: return 0
        if not m.content in taple("1234"): return 0
        return 1
    try:
        aswer_message = await client.wait_for("message",timeout=30,check=check)
    except asyncio.Timeouterror:
        result_text = "時間切れ！"
    else:
        if int(answer_message.content) == answer_abc_moved:
            exp = int(player.lv()/3)+1
            player.get_exp(exp)
            return_text = "正解！ exp+{exp}"
        else:
            return_text = "不正解！"
    em = discord.Embed(description=return_text)
    await ch.send(embed=em)

