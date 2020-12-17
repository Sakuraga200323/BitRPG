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

from sub import box, status
JST = timezone(timedelta(hours=+9), 'JST')
pg = None
client = None

items_name = {
    1:"冒険者カード",
    2:"HP回復薬",
    3:"MP回復薬",
    4:"魂の焔",
    5:"砥石",
    6:"魔石",
    7:"魔晶",
    8:"魔硬貨",
    9:"HP全回復薬",
    10:"MP全回復薬",
}

items_emoji = {
    1:"<:card:786514637289947176>",
    2:"<:hp_potion:786236538584694815>",
    3:"<:mp_potion:786236615575339029>",
    4:"<:soul_fire:786513145010454538>",
    5:"<:toishi:786513144691556364>",
    6:"<:maseki:785641515561123921>",
    7:"<:masuisyou:786516036673470504>",
    8:"<:magic_coin:786513121236746260>",
    9:"<:hp_full_potion:788668620074385429>",
    10:"<:mp_full_potion:788668620314116106>",
}

items_emoji_a = {
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


async def shop(user, ch):
    player = box.players[user.id]
    shop_em = discord.Embed(
        title="Shop",
        description=("`該当するサービスの番号を半角英数字で送信してください。`"
            + "\n`1.`アイテム購入"
            + "\n`2.`アイテム合成"
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
        em = discord.Embed(description=f"冷やかしはお断りだよ！")
        await ch.send(embed=em)
    else:
        respons = int(msg.content) if msg.content in ("1","2") else 0
        if respons == 1:
            service_em1 = discord.Embed(
                title="アイテム購入",
                description=("`該当するアイテムの番号と購入数を半角英数字で送信してください。\n例(HP回復薬を10個購入)『1 10』`"
                    + f"\n`1.`{items_emoji_a[2] }`HP回復薬　`[100cell]\n`Info: HPを30%回復`"
                    + f"\n`2.`{items_emoji_a[3] }`MP回復薬　`[100cell]\n`Info: MPを30%回復`"
                    + f"\n`3.`{items_emoji_a[4] }`魂の焔　  `[10cell]\n`Info: 素材アイテム`"
                    + f"\n`4.`{items_emoji_a[5] }`砥　石　  `[500cell]\n`Info: 素材アイテム`"
                    + f"\n`5.`{items_emoji_a[6] }`魔　石　  `[150cell]\n`Info: 250個でLv上限開放 素材アイテム`"
                    + f"\n`6.`{items_emoji_a[7] }`魔　晶　  `[1000cell]\n`Info: 素材アイテム`"
                    + f"\n`7.`{items_emoji_a[8] }`魔硬貨 　 `[2000cell]\n`Info: とある魔法の触媒`"
                    + f"\n`8.`{items_emoji_a[9] }`HP全回復薬`[300cell]\n`Info: HPを100%回復`"
                    + f"\n`9.`{items_emoji_a[10]}`MP全回復薬`[300cell]\n`Info: MPを100%回復`"
            ))
            await shop_em_msg.edit(embed=service_em1)
            try:
                msg = await client.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                em = discord.Embed(description=f"冷やかしはお断りだよ、出直してきな！")
                await ch.send(embed=em)
            else:
                pattern = r'^(\d+) (\d+)$'
                result = re.search(pattern, msg.content)
                if not result:
                    em = discord.Embed(description=f"ちゃんと注文して")
                    await ch.send(embed=em)
                    return
                item_id, item_num = int(result.group(1))+1, int(result.group(2))
                cost_dict = {2:100,3:100,4:10,5:500,6:150,7:1000,8:2000,9:300,10:300}
                if player.money() < cost_dict[item_id]*item_num:
                    em = discord.Embed(description=f"{cost_dict[item_id]*item_num-player.money()}cell程お金が足りないようです。")
                    await ch.send(embed=em)
                    return
                status.get_item(user,item_id,item_num)
                player.money(-cost_dict[item_id])
                await ch.send(f"{cost_dict[item_id]*item_num}cellで{items_name[item_id]}{items_emoji_a[item_id]}x{item_num}を購入しました。またのご来店をお待ちしております！")

        elif respons == 2:
            service_em2 = discord.Embed(
                title="アイテム購入",
                description=("`該当するアイテムの番号と購入数を半角英数字で送信してください。\n例(HP回復薬を10個購入)『1 10』`"
                    + f"\n`1.`{items_emoji_a[7] }`魔　晶  　`[500cell {items_emoji_a[5]}×1 {items_emoji_a[6]}×1]\n`Info: 素材アイテム`"
                    + f"\n`2.`{items_emoji_a[8] }`魔硬貨  　`[750cell {items_emoji_a[4]}×1 {items_emoji_a[5]}×1 {items_emoji_a[7]}×1]\n`Info: とある魔法の触媒`"
                    + f"\n`3.`{items_emoji_a[9] }`HP全回復薬`[200cell {items_emoji_a[2]}×1 {items_emoji_a[4]}×10]\n`Info: HPを100%回復`"
                    + f"\n`4.`{items_emoji_a[10]}`MP全回復薬`[200cell {items_emoji_a[3]}×1 {items_emoji_a[4]}×10]\n`Info: MPを100%回復`"
            ))
            await shop_em_msg.edit(embed=service_em2)
            try:
                msg = await client.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                em = discord.Embed(description=f"冷やかしはお断りだよ、出直してきな！")
                await ch.send(embed=em)
            else:
                pattern = r'^(\d+) (\d+)$'
                result = re.search(pattern, msg.content)
                if not result:
                    em = discord.Embed(description=f"ちゃんと注文して")
                    await ch.send(embed=em)
                    return
                item_id, item_num = int(result.group(1))+6, int(result.group(2))
                item_name = items_name[item_id]
                item_dtd = pg.fetchdict(f"select item from player_tb where id = {user.id};")[0]["item"]
                material_dict = {
                    7:((5,1),(6,1)),
                    8:((4,1),(5,1),(7,1)),
                    9:((2,1),(4,10)),
                    10:((3,1),(4,10)),
                }
                cost_dict = {7:500,8:750,9:200,10:200}
                husoku_text = ""
                for data in material_dict[item_id]:
                    i_name = items_name[data[0]]
                    if item_dtd[i_name] < data[1]*item_num:
                        husoku_text += f"{i_name}{items_emoji_a[data[0]]}×{data[1]*item_num-item_dtd[i_name]} "
                        continue
                if husoku_text != "":
                    em = discord.Embed(description=f"{husoku_text}が足りないです。")
                    await ch.send(embed=em)
                    return
                if player.money() < cost_dict[item_id]*item_num:
                    em = discord.Embed(description=f"{cost_dict[item_id]*item_num-player.money()}cell程お金が足りないようです。")
                    await ch.send(embed=em)
                    return
                for data in material_dict[item_id]:
                    i_name = items_name[data[0]]
                    status.get_item(user,data[0],-data[1]*item_num)
                status.get_item(user,item_id,item_num)
                player.money(-cost_dict[item_id]*item_num)
                em = discord.Embed(description=f"{cost_dict[item_id]*item_num}cellで{item_name}{items_emoji_a[item_id]}x{item_num}を合成しました。またのご来店をお待ちしております！")
                await ch.send(embed=em)












