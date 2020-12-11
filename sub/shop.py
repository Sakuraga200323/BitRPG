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


items_name = {
    1:"冒険者カード",
    2:"HP回復薬",
    3:"MP回復薬",
    4:"魂の焔",
    5:"砥石",
    6:"魔石",
    7:"魔晶",
    8:"魔硬貨"
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
}

async def shop(client, ch, user):
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
        await ch.send(f"冷やかしはお断りだよ！")
    else:
        respons = int(msg.content) if msg.content in ("1","2") else 0
        if respons == 1:
            service_em1 = discord.Embed(
                title="アイテム購入",
                description=("`該当するアイテムの番号と購入数を半角英数字で送信してください。\n例(HP回復薬を10個購入)『1 10』`"
                    + f"\n`1.`{items_emoji[2]}`HP回復薬　`[`100`cell]"
                    + f"\n`2.`{items_emoji[3]}`MP回復薬　`[`100`cell]"
                    + f"\n`3.`{items_emoji[4]}`魂の焔　  `[`10`cell]"
                    + f"\n`4.`{items_emoji[5]}`砥　石　  `[`1000`cell]"
                    + f"\n`5.`{items_emoji[6]}`魔　石　  `[`500`cell]"
                    + f"\n`6.`{items_emoji[7]}`魔　晶　  `[`2000`cell]"
                    + f"\n`7.`{items_emoji[8]}`魔硬貨 　 `[`3000`cell]"
            ))
            await shop_em_msg.edit(embed=service_em1)
            try:
                msg = await client.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                await ch.send(f"冷やかしはお断りだよ！")
            else:
                pattern = r'^(\d+) (\d+)$'
                result = re.search(pattern, msg.content)
                if not result:
                    await ch.send('ちゃんと注文して')
                    return
                item_id, item_num = int(result.group(1))+1, int(result.group(2))
                cost_dict = {2:100,3:100,4:10,5:1000,6:500,7:2000,8:3000}
                if player.money() < cost_dict[item_id]*item_num:
                    await ch.send(f"{cost_dict[item_id]*item_num-player.money()}cell程お金が足りないようです。")
                    return
                status.get_item(client,user,item_id,item_num)
                player.money(-cost_dict[item_id])
                await ch.send(f"{cost_dict[item_id]*item_num}cellで{item_name[item_id]}{items_emoji[item_id]}x{item_num}を購入しました。またのご来店をお待ちしております！")
        elif respons == 2:
            service_em2 = discord.Embed(
                title="アイテム購入",
                description=("`該当するアイテムの番号と購入数を半角英数字で送信してください。\n例(HP回復薬を10個購入)『1 10』`"
                    + f"\n`1.`{items_emoji[7]}`魔　晶　  `[`750`cell {items_emoji[5]}×1 {items_emoji[6]}×1]"
                    + f"\n`2.`{items_emoji[8]}`魔硬貨 　 `[`1000`cell {items_emoji[4]}×1 {items_emoji[5]}×1 {items_emoji[7]}×1]"
            ))
            await shop_em_msg.edit(embed=service_em2)
            try:
                msg = await client.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                await ch.send(f"冷やかしはお断りだよ！")
            else:
                pattern = r'^(\d+) (\d+)$'
                result = re.search(pattern, msg.content)
                if not result:
                    await ch.send('ちゃんと注文して')
                    return
                item_id, item_num = int(result.group(1))+6, int(result.group(2))
                item_name = items_name[item_id]
                item_dtd = pg.fetchdict(f"select item from player_tb where id = {user.id};")[0]["item"]
                material_dict = {
                    7:((5,1),(6,1)),
                    8:((4,1),(5,1),(7,1))}
                cost_dict = {7:750,8:1000}
                husoku_text = ""
                for data in material_dict[item_id]:
                    i_name = items_name[data[0]]
                    if item_dtd[i_name] < data[1]:
                        husoku_text += f"{i_name}{items_emoji[data[0]]}×{data[1]-item_dtd[i_name]} "
                        continue
                    status.get_item(client,user,data[0],-data[1])
                if husoku_text != "":
                    await ch.send(f"{husoku_text}が足りないです。")
                    return
                if player.money() < cost_dict[item_id]*item_num:
                    await ch.send(f"{cost_dict[item_id]*item_num-player.money()}cell程お金が足りないようです。")
                    return
                status.get_item(client,user,item_id,item_num)
                player.money(-cost_dict[item_id])
                await ch.send(f"{cost_dict[item_id]*item_num}cellで{item_name}{items_emoji[item_id]}x{item_num}を合成しました。またのご来店をお待ちしております！")
            
                
                









