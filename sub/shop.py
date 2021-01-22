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
            + "\n`3.`武器購入"
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
        if not re.search(pattern, m.content) and not m.content == "0":return 0
        return 1
    try:
        msg = await client.wait_for("message", timeout=60, check=check3)
        await msg.delete()
    except asyncio.TimeoutError:
        await shop_msg.edit(embed=shop_em)
    else:
        respons = int(msg.content)

        if respons == 1:
            shop_em1 = discord.Embed(title="アイテムショップ",description=f"所持Cell:{player.money()}")
            menu_tuple = (
                    (f"` 1.`{items_emoji_a[2] }HP回復薬",         f"┗━Price: 100cell┃Info: HPを500回復 素材アイテム"),
                    (f"` 2.`{items_emoji_a[3] }MP回復薬",         f"┗━Price: 100cell┃Info: MPを500回復"),
                    (f"` 3.`{items_emoji_a[4] }魂の焔",           f"┗━Price: 10cell┃Info: 素材アイテム とある魔法の触媒"),
                    (f"` 4.`{items_emoji_a[5] }砥石",             f"┗━Price: 500cell┃Info: 素材アイテム"),
                    (f"` 5.`{items_emoji_a[6] }魔石",             f"┗━Price: 150cell┃Info: 250個でLv上限開放 素材アイテム"),
                    (f"` 6.`{items_emoji_a[7] }魔晶",             f"┗━Price: 1000cell┃Info: 素材アイテム"),
                    (f"` 7.`{items_emoji_a[8] }魔硬貨",           f"┗━Price: 2000cell┃Info: とある魔法の触媒"),
                    (f"` 8.`{items_emoji_a[9] }HP全回復薬",       f"┗━Price: 300cell┃Info: HPを100%回復"),
                    (f"` 9.`{items_emoji_a[10]}MP全回復薬",       f"┗━Price: 300cell┃Info: MPを100%回復"),
                    (f"`10.`{items_emoji_a[26]}型枠-インゴット",   f"┗━Price: 5cell┃Info: 素材アイテム"),
                    (f"`11.`{items_emoji_a[26]}型枠-強化素材チップ",f"┗━Price: 5cell┃Info: 素材アイテム"),
            )
            for i in menu_tuple:
                shop_em1.add_field(name=i[0],value=i[1],inline=False)
            await shop_msg.edit(
                content="```該当するアイテムの番号と購入数を半角スペースを空けて送信してください。0と送信すると終了します。\n例：HP回復薬を10個購入\n1 10```",
                embed=shop_em1
            )
            while True:
                try:
                    msg = await client.wait_for("message", timeout=60, check=check_buy)
                    await msg.delete()
                except asyncio.TimeoutError:
                    await shop_msg.edit(
                        content="```時間経過により処理終了済み```",
                        embed=shop_em1
                    )
                    break
                else:
                    pattern = r'^(\d+) (\d+)$'
                    result = re.search(pattern, msg.content)
                    if msg.content == "0":
                        await shop_msg.edit(
                            content="```処理終了済み```",
                            embed=shop_em1
                        )
                        break
                    item_id, item_num = int(result.group(1))+1, int(result.group(2))
                    cost_dict = {2:100,3:100,4:10,5:500,6:150,7:1000,8:2000,9:300,10:300,26:5}
                    if player.money() < cost_dict[item_id]*item_num:
                        await shop_msg.edit(
                            content=f"```{cost_dict[item_id]*item_num-player.money()}Cell足りません。\nそのまま購入を続けられます。終了する場合は0を送信。```",
                            embed=shop_em1
                        )
                        continue
                    status.get_item(user,item_id,item_num)
                    player.money(-cost_dict[item_id]*item_num)
                    await shop_msg.edit(
                        content=f"{cost_dict[item_id]*item_num}cellで{items_name[item_id]}{items_emoji_a[item_id]}x{item_num}を購入しました。\n\nそのまま購入を続けられます。終了する場合は0を送信。",
                        embed=shop_em1
                    )

        elif respons == 2:
            shop_em2 = discord.Embed(title="合成場",description=f"所持Cell:{player.money()}")
            menu_tuple = (
                    (f"\n` 1.`{items_emoji_a[7] }魔晶",      f"┗━Cost: 500cell {items_emoji_a[5]}×1 {items_emoji_a[6]}×1┃Info: 素材アイテム"),
                    (f"\n` 2.`{items_emoji_a[8] }魔硬貨",    f"┗━Cost: 750cell {items_emoji_a[4]}×1 {items_emoji_a[5]}×1 {items_emoji_a[7]}×1┃Info: とある魔法の触媒"),
                    (f"\n` 3.`{items_emoji_a[9] }HP全回復薬",f"┗━Cost: 200cell {items_emoji_a[2]}×1 {items_emoji_a[4]}×10]┃Info: HPを100%回復"),
                    (f"\n` 4.`{items_emoji_a[10]}MP全回復薬",f"┗━Cost: 200cell {items_emoji_a[3]}×1 {items_emoji_a[4]}×10]┃Info: MPを100%回復"),
                    (f"\n` 5.`{items_emoji_a[24]}黒色酸化鉄",f"┗━Cost: 100cell {items_emoji_a[23]}×1 {items_emoji_a[4]}×10]┃Info: 武器素材"),
                    (f"\n` 6.`{items_emoji_a[12]}キャラメル鋼",f"┗━Cost: 100cell {items_emoji_a[11]}×1 {items_emoji_a[4]}×10] {items_emoji_a[26]}×1┃Info: 武器素材"),
                    (f"\n` 7.`{items_emoji_a[14]}ブラッド鋼",f"┗━Cost: 100cell {items_emoji_a[13]}×1 {items_emoji_a[4]}×10] {items_emoji_a[26]}×1┃Info: 武器素材"),
                    (f"\n` 8.`{items_emoji_a[16]}ゴールド鋼",f"┗━Cost: 100cell {items_emoji_a[15]}×1 {items_emoji_a[4]}×10] {items_emoji_a[26]}×1┃Info: 武器素材"),
                    (f"\n` 9.`{items_emoji_a[18]}ダーク鋼",f"┗━Cost: 100cell {items_emoji_a[17]}×1 {items_emoji_a[4]}×10] {items_emoji_a[26]}×1┃Info: 武器素材"),
                    (f"\n`10.`{items_emoji_a[20]}ミスリル鋼",f"┗━Cost: 100cell {items_emoji_a[19]}×1 {items_emoji_a[4]}×10] {items_emoji_a[26]}×1┃Info: 武器素材"),
                    (f"\n`11.`{items_emoji_a[22]}オリハルコン鋼",f"┗━Cost: 100cell {items_emoji_a[21]}×1 {items_emoji_a[4]}×10] {items_emoji_a[26]}×1┃Info: 武器素材"),
                    (f"\n`12.`{items_emoji_a[29]}カーボンプレート",f"┗━Cost: 100cell {items_emoji_a[28]}×1 {items_emoji_a[4]}×10] {items_emoji_a[9]}×1┃Info: 武器強化素材"),
                    (f"\n`12.`{items_emoji_a[30]}カーボンチップ",f"┗━Cost: 100cell {items_emoji_a[29]}×1 {items_emoji_a[4]}×10] {items_emoji_a[27]}×1┃Info: 武器強化素材"),
            )
            for i in menu_tuple:
                shop_em2.add_field(name=i[0],value=i[1],inline=False)
            await shop_msg.edit(
                content="```該当するアイテムの番号と購入数を半角スペースを空けて送信してください。0と送信すると終了します。\n例：HP全回復薬を10個合成\n3 10```",
                embed=shop_em2
            )
            while True:
                try:
                    msg = await client.wait_for("message", timeout=60, check=check_buy)
                    await msg.delete()
                except asyncio.TimeoutError:
                    await shop_msg.edit(
                        content="```時間経過により処理終了済み```",
                        embed=shop_em2
                    )
                else:
                    pattern = r'^(\d+) (\d+)$'
                    result = re.search(pattern, msg.content)
                    if msg.content == "0":
                        await shop_msg.edit(
                            content="```処理終了済み```",
                            embed=shop_em2
                        )
                        break
                    item_id, item_num = int(result.group(1))+6, int(result.group(2))
                    item_name = items_name[item_id]
                    material_dict = {
                        7:((5,1),(6,1)),
                        8:((4,1),(5,1),(7,1)),
                        9:((2,1),(4,10)),
                        10:((3,1),(4,10)),
                        12:((11,1),(4,10),(26,1)),
                        14:((13,1),(4,10),(26,1)),
                        16:((15,1),(4,10),(26,1)),
                        18:((17,1),(4,10),(26,1)),
                        20:((19,1),(4,10),(26,1)),
                        22:((21,1),(4,10),(26,1)),
                        29:((28,1),(4,10),(9,1)),
                        30:((29,1),(4,10),(27,1)),
                    }
                    cost_dict = {7:500,8:750,9:200,10:200}
                    husoku_text = ""
                    for data in material_dict[item_id]:
                        i_name = items_name[data[0]]
                        if player.item_num(i_name) < data[1]*item_num:
                            husoku_text += f"{i_name}{items_emoji_a[data[0]]}×{data[1]*item_num-player.item_num(i_name)} "
                            continue
                    if husoku_text != "":
                        await shop_msg.edit(
                            content=f"{husoku_text}が不足しています。\nそのまま購入を続けられます。終了する場合は0を送信。",
                            embed=shop_em2
                        )
                        continue
                    if player.money() < cost_dict[item_id]*item_num:
                        await shop_msg.edit(
                            content=f"```{cost_dict[item_id]*item_num-player.money()}cell程お金が足りないようです。\nそのまま購入を続けられます。終了する場合は0を送信。```",
                            embed=shop_em2
                        )
                        continue
                    for data in material_dict[item_id]:
                        i_name = items_name[data[0]]
                        player.get_item(data[0],-data[1]*item_num)
                    player.get_item(item_id,item_num)
                    player.money(-cost_dict[item_id]*item_num)
                    shop_em2.description = f"所持Cell:{player.money()}"
                    await shop_msg.edit(
                        content=f"{cost_dict[item_id]*item_num}cellで{item_name}{items_emoji_a[item_id]}x{item_num}を合成しました。\nそのまま購入を続けられます。終了する場合は0を送信。",
                        embed=shop_em2
                    )



        elif respons == 3:
            split_weapons_key = tuple(split_list(box.shop_weapons,6))
            em_title = "武具店"
            rank_dict = {1:"D",2:"C",3:"B",4:"A",5:"S"}
            embeds = []
            weapons = []
            for page_num,weapons_name in zip(range(1,100),split_weapons_key):
                em = discord.Embed(title=em_title,description=f"所持Cell:{player.money()}")
                for num,weapon_name in zip(range(1,100),weapons_name):
                    weapon_data = box.shop_weapons[weapon_name]
                    em.add_field(name=f"\n`{num}.`{weapon_data[0]}{weapon_name}",value=f"┗━Price: {weapon_data[1]}cell┃MaxRank: {rank_dict[weapon_data[2]]}",inline=False)
                em.set_footer(text=f"Page.{page_num}/{len(split_weapons_key)}")
                embeds.append(em)
            embeds = tuple(embeds)
            page_num = 0
            await shop_msg.edit(
                content=f'`リアクション、ページ番号送信でページ切り替えです。`\n{box.menu_emojis["left"]}:一つページを戻す\n{box.menu_emojis["close"]}:処理を終了する\n{box.menu_emojis["right"]}:一つページを進める\n{box.menu_emojis["buy_mode"]}:購入モードに変更`\nMaxRankは購入時にランダムで決められるランクの最大値です`',
                embed=embeds[0]
            )
            shop_flag = True
            while True:
                buy_mode = False
                if shop_flag is False:
                    break
                if not buy_mode:
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
                        reaction,msg = None,None
                        reaction, user = await client.wait_for("reaction_add",check=check_react,timeout=60.0)
                    except asyncio.TimeoutError:
                        await shop_msg.edit(
                            content="```時間経過により処理終了済み```",
                            embed=embeds[0]
                        )
                        await shop_msg.clear_reactions()
                        break
                    else:
                        content=f'`リアクション、ページ番号送信でページ切り替えです。`\n{box.menu_emojis["left"]}:一つページを戻す\n{box.menu_emojis["close"]}:処理を終了する\n{box.menu_emojis["right"]}:一つページを進める\n{box.menu_emojis["buy_mode"]}:購入モードに変更`\nMaxRankは購入時にランダムで決められるランクの最大値です`'
                        if reaction:
                            before_page_num = page_num
                            emoji = str(reaction.emoji)
                            if emoji == box.menu_emojis["right"]:
                                if page_num < len(embeds)-1:
                                     page_num += 1
                            elif emoji == box.menu_emojis["close"]:
                                await shop_msg.edit(
                                    content="```処理終了済み```",
                                    embed=embeds[0]
                                )
                                await shop_msg.clear_reactions()
                                break
                            elif emoji == box.menu_emojis["left"]:
                                if page_num > 0:
                                     page_num -= 1
                            elif emoji == box.menu_emojis["buy_mode"]:
                                buy_mode = True
                            if before_page_num != page_num:
                                await shop_msg.clear_reactions()
                            if buy_mode:
                                await shop_msg.clear_reactions()
                                content=f'`購入モードです。対応する武器の番号を送信してください。武器スロットが５枠すべて埋まっていると購入できません。\n0を送信すると終了します。`'
                            shop_em3 = embeds[page_num]
                            await shop_msg.edit(content=content,embed=shop_em3)
                while buy_mode:
                    try:
                        msg = await client.wait_for("message", timeout=60, check=check3)
                        await msg.delete()
                    except asyncio.TimeoutError:
                        await shop_msg.edit(
                            content="```時間経過により処理終了済み```"
                        )
                        buy_mode = False
                        shop_flag = False
                        break
                    else:
                        if msg.content == "0":
                            await shop_msg.edit(content="```処理終了済み```"
                            )
                            buy_mode = False
                            shop_flag = False
                            break
                        weapon_id = int(msg.content) + (page_num)*6
                        weapon = box.npc_weapons[weapon_id]
                        if len(player.weapons()) >= 5:
                            await shop_msg.edit(
                                content=f"```既に５個の武器を所持しています。\n処理終了済み```"
                            )
                            shop_flag = False
                            break
                        if player.money() < weapon.create_cost:
                            await shop_msg.edit(
                                content=f"```{weapon.create_cost-player.money()}Cell足りません。\nそのまま購入を続けられます。終了する場合は0を送信。```"
                            )
                            continue
                        rank = 1
                        for i in range(1,weapon.max_rank-1):
                            if random.random() <= weapon.rate_of_rankup:
                                rank += 1
                                if rank == weapon.max_rank:
                                    buy_mode = False
                                    break
                        weapon_obj = player.create_weapon(weapon.name,weapon.emoji,rank)
                        player.get_weapon(weapon_obj)
                        player.money(-weapon.create_cost)
                        await shop_msg.edit(
                            content=f"{weapon.create_cost}cellで{weapon_obj.emoji()}{weapon_obj.name()}(Rank.{weapon_obj.rank()})を購入しました。\nそのまま購入を続けられます。終了する場合は0を送信。",
                        )
                        
                        

                    
