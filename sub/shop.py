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

client = pg = None
def first_set(c,p):
    global client, pg
    client = c
    pg = p

def split_list(l, n):
    l = list(l)
    if len(l) <= n:
        return l
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]

items_name = box.items_name
items_emoji = box.items_emoji
items_emoji_a = box.items_emoji


async def shop(user, ch):
    # shop_msg1 -> ショプの最初のメッセージ
    # shop_msg2 -> コマンドの使いかたや状況の詳細を書き込むメッセージ
    player = box.players[user.id]
    shop_em = discord.Embed(
        title="Shop",
        description=(
            "\n`1.`アイテム購入"
            + "\n`2.`アイテム合成"
            + "\n`3.`~~武器購入~~"
    ))
    shop_msg = await ch.send(embed=shop_em)
    def check(m):
        if not user.id == m.author.id:return 0
        return 1
    def check2(m):
        if not user.id == m.author.id:return 0
        if not m.content in ("y","Y","n","N"):return 0
        return 1
    def check3(m):
        if not user.id == m.author.id:return 0
        if not m.content.isdigit():return 0
        return 1
    def check_buy(m):
        if not user.id == m.author.id:return 0
        pattern = r'^(\d+) (\d+)$'
        if not re.search(pattern, m.content) or not m.content == "0":return 0
        return 1
    try:
        msg = await client.wait_for("message", timeout=60, check=check3)
        await msg.delete()
    except asyncio.TimeoutError:
        await shop_msg.edit(embed=shop_em)
    else:
        respons = int(msg.content)
        while True:
            if respons == 1:
                shop_em1 = discord.Embed(title="アイテムショップ",description=f"所持Cell:{player.money()}")
                menu_tuple = (
                        (f"`1.`{items_emoji_a[2] }HP回復薬",  f"`┗━Price: 100cell┃Info: HPを30%回復`"),
                        (f"`2.`{items_emoji_a[3] }MP回復薬",  f"`┗━Price: 100cell┃Info: MPを30%回復`"),
                        (f"`3.`{items_emoji_a[4] }魂の焔",    f"`┗━Price: 10cell┃Info: 素材アイテム とある魔法の触媒`"),
                        (f"`4.`{items_emoji_a[5] }砥石",      f"`┗━Price: 500cell┃Info: 素材アイテム`"),
                        (f"`5.`{items_emoji_a[6] }魔石",      f"`┗━Price: 150cell┃Info: 250個でLv上限開放 素材アイテム`"),
                        (f"`6.`{items_emoji_a[7] }魔晶",      f"`┗━Price: 1000cell┃Info: 素材アイテム`"),
                        (f"`7.`{items_emoji_a[8] }魔硬貨",    f"`┗━Price: 2000cell┃Info: とある魔法の触媒`"),
                        (f"`8.`{items_emoji_a[9] }HP全回復薬",f"`┗━Price: 300cell┃Info: HPを100%回復`"),
                        (f"`9.`{items_emoji_a[10]}MP全回復薬",f"`┗━Price: 300cell┃Info: MPを100%回復`"),
                )
                for i in menu_tuple:
                    shop_em1.add_field(name=i[0],value=i[1])
                await shop_msg.edit(
                    content="`該当するアイテムの番号と購入数を半角スペースを空けて送信してください。0と送信すると終了します。\n例：HP回復薬を10個購入\n1 10`",
                    embed=shop_em1
                )
                while True:
                    try:
                        msg = await client.wait_for("message", timeout=60, check=check_buy)
                        await msg.delete()
                    except asyncio.TimeoutError:
                        await shop_msg.edit(
                            content="時間経過により処理終了済み",
                            embed=shop_em1
                        )
                    else:
                        pattern = r'^(\d+) (\d+)$'
                        result = re.search(pattern, msg.content)
                        item_id, item_num = int(result.group(1))+1, int(result.group(2))
                        cost_dict = {2:100,3:100,4:10,5:500,6:150,7:1000,8:2000,9:300,10:300}
                        if player.money() < cost_dict[item_id]*item_num:
                            await shop_msg.edit(
                                content=f"{cost_dict[item_id]*item_num-player.money()}Cell足りません",
                                embed=shop_em1
                            )
                            continue
                        status.get_item(user,item_id,item_num)
                        player.money(-cost_dict[item_id]*item_num)
                        shop_em21.description = f"所持Cell:{player.money()}"
                        await shop_msg.edit(
                            content=f"{cost_dict[item_id]*item_num}cellで{items_name[item_id]}{items_emoji_a[item_id]}x{item_num}を購入しました。\nまたのご来店をお待ちしております！",
                            embed=shop_em1
                        )

            elif respons == 2:
                shop_em2 = discord.Embed(title="合成場",description=f"所持Cell:{player.money()}")
                menu_tuple = (
                        (f"\n`1.`{items_emoji_a[7] }魔晶",      f"`┗━Cost: 500cell {items_emoji_a[5]}×1 {items_emoji_a[6]}×1┃Info: 素材アイテム`"),
                        (f"\n`2.`{items_emoji_a[8] }魔硬貨",    f"`┗━Cost: 750cell {items_emoji_a[4]}×1 {items_emoji_a[5]}×1 {items_emoji_a[7]}×1┃Info: とある魔法の触媒`"),
                        (f"\n`3.`{items_emoji_a[9] }HP全回復薬",f"`┗━Cost: 200cell {items_emoji_a[2]}×1 {items_emoji_a[4]}×10]┃Info: HPを100%回復`"),
                        (f"\n`4.`{items_emoji_a[10]}MP全回復薬",f"`┗━Cost: 200cell {items_emoji_a[3]}×1 {items_emoji_a[4]}×10]┃Info: MPを100%回復`"),
                )
                for i in menu_tuple:
                    shop_em2.add_field(name=i[0],value=i[1])
                await shop_msg.edit(
                    content="`該当するアイテムの番号と購入数を半角スペースを空けて送信してください。0と送信すると終了します。\n例：HP全回復薬を10個合成\n3 10`",
                    embed=shop_em1
                )
                while True:
                    try:
                        msg = await client.wait_for("message", timeout=60, check=check_buy)
                        await msg.delete()
                    except asyncio.TimeoutError:
                        await shop_msg.edit(
                            content="時間経過により処理終了済み",
                            embed=shop_em1
                        )
                    else:
                        pattern = r'^(\d+) (\d+)$'
                        result = re.search(pattern, msg.content)
                        item_id, item_num = int(result.group(1))+6, int(result.group(2))
                        item_name = items_name[item_id]
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
                            if player.item_num(i_name) < data[1]*item_num:
                                husoku_text += f"{i_name}{items_emoji_a[data[0]]}×{data[1]*item_num-item_dtd[i_name]} "
                                continue
                        if husoku_text != "":
                            await shop_msg.edit(
                                content=f"{husoku_text}が不足しています。",
                                embed=shop_em1
                            )
                            continue
                        if player.money() < cost_dict[item_id]*item_num:
                            await shop_msg.edit(
                                content=f"{cost_dict[item_id]*item_num-player.money()}cell程お金が足りないようです",
                                embed=shop_em1
                            )
                            continue
                        for data in material_dict[item_id]:
                            i_name = items_name[data[0]]
                            player.get_item(user,data[0],-data[1]*item_num)
                        player.get_item(user,item_id,item_num)
                        player.money(-cost_dict[item_id]*item_num)
                        shop_em2.description = f"所持Cell:{player.money()}"
                        await shop_msg.edit(
                            content=f"{cost_dict[item_id]*item_num}cellで{item_name}{items_emoji_a[item_id]}x{item_num}を合成しました。\nまたのご来店をお待ちしております！",
                            embed=shop_em2
                        )



            elif respons == 3:
                split_weapons_key = tuple(split_list(box.shop_weapons,10))
                em_title = "武具店"
                rank_dict = {1:"D",2:"C",3:"B",4:"A",5:"S"}
                embeds = []
                weapons = []
                for page_num,weapons_name in zip(range(1,100),split_weapons_key):
                    em = discord.Embed(title=em_title,description=f"所持Cell:{player.money()}")
                    for num,weapon_name in zip(range(1,11),weapons_name):
                        weapon_data = box.shop_weapons[weapon_name]
                        em.add_field(name=f"\n`{num}.`{weapon_data[0]}{weapon_name}",value=f"`┗━Price: {weapon_data[1]}cell┃MaxRank: {rank_dict[weapon_data[2]]}`")
                    embed.set_footer(text=f"Page.{page_num}/{len(split_weapons_key)}")
                    embeds.append(embed)
                embeds = tuple(embeds)
                page_num = 0
                await shop_msg.edit(
                    content="`対応する数字を送信で武器購入、リアクションでページ切り替えです。\nMaxRankは購入時にランダムで決められるランクの最大値です`",
                    embed=embeds[0]
                )
                while client:
                    buy_mode = False
                    for emoji in tuple(box.menu_emojis.values()):
                        await shop_msg.add_reaction(emoji)
                    def check_react(r,u):
                        if r.message.id != shop_msg.id:
                            return 0
                        if u.id != user.id:
                            return 0
                        if not str(r.emoji) in tuple(box.menu_emojis.values()):
                            return 0
                        return 1
                    try:
                        reaction, user = await client.wait_for("reaction_add",check=check_react,timeout=60.0)
                    except asyncio.TimeoutError:
                        await shop_msg.edit(
                            content="`時間経過により処理終了済み`",
                            embed=embeds[0]
                        )
                        await shop_msg.clear_reactions()
                        break
                    else:
                        emoji = str(reaction.emoji)
                        menu_em = discord.Embed(description=menu_text2,color=0xebebeb)
                        await menu_msg.edit(embed=menu_em)
                        if emoji == menu_emojis["right"]:
                            if page_num <= len(embeds)-1:
                                 page_num += 1
                        elif emoji == menu_emojis["close"]:
                            await shop_msg.edit(
                                content="`処理終了済み`",
                                embed=embeds[0]
                            )
                            await shop_msg.clear_reactions()
                            break
                        elif emoji == menu_emojis["left"]:
                            if page_num <= len(embeds)-1:
                                 page_num -= 1
                        elif emoji == menu_emojis["buy_mode"]:
                            buy_mode = True

                    await shop_msg.edit(
                        content='`対応する数字を送信で武器購入、リアクションでページ切り替えです。`\n{box.gui_emoji["left"]}:一つページを戻す\n{box.gui_emoji["close"]}:処理を終了する\n{box.gui_emoji["right"]}:一つページを進める\n{box.gui_emoji["buy_mode"]}:購入モードに変更`\nMaxRankは購入時にランダムで決められるランクの最大値です`',
                        embed=embeds[page_num]
                    )


