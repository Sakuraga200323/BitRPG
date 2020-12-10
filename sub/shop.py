import ast
import asyncio
import cv2
from datetime import datetime, timedelta, timezone
import math
import os
import random
import re
import sys
import discord
from discord.ext import tasks
import psutil
import psycopg2, psycopg2.extras
import traceback

from sub import box
JST = timezone(timedelta(hours=+9), 'JST')
pg = None

item_emoji = {
    1:"<:card:786514637289947176>",
    2:"<:hp_potion:786236538584694815>",
    3:"<:mp_potion:786236615575339029>",
    4:"<:soul_fire:786513145010454538>",
    5:"<:toishi:786513144691556364>",
    6:"<:maseki:785641515561123921>",
    7:"<:masuisyou:786516036673470504>",
    8:"<:magic_coin:786513121236746260>",
}

async def shop(client, ch, user):
    player = box.players[user.id]
    shop_em = discord.Embed(
        title="Shop",
        description=("`該当するサービスの番号を半角英数字で送信してください。`"
            + "\n`1`)アイテム購入"
            + "\n`2`)アイテム合成"
    ))
    shop_em_msg = await ch.send(embed=shop_em)
    def check(m):
        if not user.id == m.author.id:
            return 0
        return 1
    def check2(m):
        if not user.id == m.author.id:
            return 0
        if not m.content in ("y","Y","n","N"):
            return 0
        return 1
    try:
        msg = await client.wait_for("message", timeout=60, check=check)
    except asyncio.TimeoutError:
        await ch.send(f"冷やかしはお断りだよ！")
    else:
        respons = int(msg.content) if msg.content in ("1","2") else 0
        if respons == "1":
            service_em1 = discord.Embed(
                title="アイテム購入",
                description=("`該当するアイテムの番号と購入数を半角英数字で送信してください。\n例(HP回復薬を10個購入)『1 10』`"
                    + f"\n1){item_emoji[2]}`HP回復薬`[100cell]"
                    + f"\n2){item_emoji[3]}`MP回復薬`[100cell]"
                    + f"\n3){item_emoji[4]}`魂の焔  `[10cell]"
                    + f"\n4){item_emoji[5]}`砥石　  `[1000cell]"
                    + f"\n5){item_emoji[6]}`魔石　  `[500cell]"
                    + f"\n6){item_emoji[7]}`魔晶　  `[2000cell]"
                    + f"\n7){item_emoji[8]}`魔硬貨  `[3000cell]"
            ))
            await ch.send(embed=service_em1)
