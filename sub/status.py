# coding: utf-8
# Your code here!

# coding: utf-8
# Your code here!

import math
import ast
import asyncio
from datetime import datetime, timedelta, timezone
import discord
from discord.ext import tasks
import glob
import os
import psutil
import psycopg2
import psycopg2.extras
import random
import re
import traceback
from sub import box, calc

JST = timezone(timedelta(hours=+9), 'JST')

dsn = os.environ.get('DATABASE_URL')

def my_round(val, digit=0):
    p = 10 ** digit
    return (val * p * 2 + 1) // 2 / p

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

# ^^i で消費しないアイテムの {ID:名前} #
constant_items_name = {1:"冒険者カード", 4:"魂の焔", 5:"砥石", 6:"魔石", 7:"魔晶", 8:"魔硬貨"}


items_name = box.items_name

items_id = box.items_id

items_emoji = box.items_emoji

items_emoji_a = box.items_emoji

# 画像があるアイテムの {名前:画像URL} #
items_image = {
    "HP回復薬":"https://media.discordapp.net/attachments/719855399733428244/786984382673977374/hp_potion.gif",
    "MP回復薬":"https://media.discordapp.net/attachments/719855399733428244/786984396887556096/mp_potion.gif",
    "魔石":"https://media.discordapp.net/attachments/719855399733428244/757449362652790885/maseki.png",
    "魔硬貨":"https://media.discordapp.net/attachments/719855399733428244/786984393594896474/magic_coin.gif"
}

def change_num(a):
    a = str(a).translate(str.maketrans(dict(zip(list("0123456789"),list("⁰¹²³⁴⁵⁶⁷⁸⁹")))))
    return a
def change_abc(a):
    temp = 'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
    a = str(a).translate(str.maketrans(dict(zip(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),list(temp)))))
    return a

#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨

# ステータス #
async def open_status(user,ch):
    if not user.id in box.players:
        return
    p_data = box.players[user.id]
    mc = p_data.magic_class()
    embed = discord.Embed(title="Player Status Board",color=0xe1ff00 if mc == "Wolf" else 0x8f6200 if mc == "Armadillo" else 0x2e3cff if mc == "Orca" else discord.color.red())
    embed.add_field(name=f"Player", value=f"{p_data.user.mention}", inline=False)
    embed.add_field(name=f"Level (Now/Limit)", value=f"`{p_data.lv()}/{p_data.max_lv()}`")
    embed.add_field(name=f"MagicLevel", value=f"`{mc} Lv.{p_data.magic_lv()}`")
    if mc == "Armadillo":
        embed.add_field(name=f"HitPoint (Now/Max)", value=f"{p_data.now_hp}/{p_data.max_hp}\n(+10%)", inline=False)
    else:
        embed.add_field(name=f"HitPoint (Now/Max)", value=f"{p_data.now_hp}/{p_data.max_hp}", inline=False)
    if mc == "Orca":
        embed.add_field(name=f"MagicPoint (Now/Max)", value=f"{p_data.now_mp}/{p_data.max_mp}\n(+10%)", inline=False)
    else:
        embed.add_field(name=f"MagicPoint (Now/Max)", value=f"{p_data.now_mp}/{p_data.max_mp}", inline=False)
    strength_text = f"{p_data.STR()}\n(+{p_data.str_p()}"
    if mc == "Wolf":
        strength_text += "｜+10%"
    if mc == "Armadillo":
        rate = int((1 - (p_data.now_hp / p_data.max_hp))*4*100)
        if rate:
            strength_text += f"｜+{rate}%"
    if p_data.weapon():
        strength_text += f"｜+{p_data.weapon().strength()}{p_data.weapon().emoji()}"
    strength_text += ")"
    embed.add_field(name=f"Strength", value=strength_text)
    if mc == "Armadillo":
        embed.add_field(name=f"Defense (Now/Limit)", value=f"{p_data.now_defe}/{p_data.max_defe}\n(+{p_data.defe_p()}｜+10%)")
    else:
        embed.add_field(name=f"Defense (Now/Limit)", value=f"{p_data.now_defe}/{p_data.max_defe}\n(+{p_data.defe_p()})")
    if mc == "Orca":
        embed.add_field(name=f"Agility", value=f"{p_data.AGI()}\n(+{p_data.agi_p()}｜+10%)")
    else:
        embed.add_field(name=f"Agility", value=f"{p_data.AGI()}\n(+{p_data.agi_p()})")
    embed.add_field(name=f"StatusPoint", value=f"{p_data.now_stp()}")
    gauge_edge_reft = "<:_end:784330415624290306>"
    gauge_edge_right = "<:end_:784330344748417024>"
    def gauge(x,y):
        return round(x/y*15)*"━"
    if not p_data.STP() <= 0:
        all_stp = p_data.STP() - p_data.now_stp()
        s = f"{gauge(p_data.str_p(), all_stp)}"
        d = f"{gauge(p_data.defe_p(), all_stp)}"
        a = f"{gauge(p_data.agi_p(), all_stp)}"
        embed.add_field(name=f"StatusPointBalance (STR◆DEF◆AGI)", value=f"`Total: {all_stp}`\n{gauge_edge_reft}`{s}◆{d}◆{a}`{gauge_edge_right}", inline=False)
    have_exp = p_data.now_exp()
    must_exp = p_data.lv() + 1
    exp_gauge_num = int((have_exp / must_exp)*10)
    if exp_gauge_num > 10:
        exp_gauge_num = 10
    exp_gauge_1 = '<:1_:784323561052569642>'*exp_gauge_num
    exp_gauge_0 = (10 - exp_gauge_num) * '<:0_:784323507110150144>'
    embed.add_field(name = f"Experience", value=(
          f"`Total: {p_data.max_exp()}`"
        + f"\n{gauge_edge_reft}{exp_gauge_1 + exp_gauge_0}{gauge_edge_right}"
        + f"\n`({p_data.now_exp()} / {p_data.lv()+1})`"))
    embed.set_thumbnail(url=user.avatar_url)
    await ch.send(embed=embed)
    log_ch = client.get_channel(766997493195210774)
    await log_ch.send(embed=embed)

#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨

# インベントリ #
async def i_inventory(player,ch):
    item_dtd = pg.fetchdict(f"select item from player_tb where id = {player.user.id};")[0]["item"]
    text = "`ID.アイテム名　　`┃`所持数`\n"
    for (item_name,item_emoji) in zip((box.items_name.values()),list(box.items_emoji.values())):
        if not item_dtd[item_name] == 0:
            item_id = box.items_id[item_name]
            text += f"`{item_id:<2}.`{item_emoji}`{change_abc(item_name):　<6}`┃`{item_dtd[item_name]}`\n"
    em = discord.Embed(title="Item Inventory Bord",description=f"{text}")
    await ch.send(embed=em)

# ウェポンインベントリ #
async def w_inventory(player,ch):
    em = discord.Embed(title="Weapon Inventory Bord")
    if player.weapons() != []:
        for weapon in player.weapons():
            if player.weapon() and weapon.id == player.weapon().id:
                em.add_field(name=f"{weapon.emoji()}{weapon.name()}",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
            else:
                em.add_field(name=f"{weapon.emoji()}`{weapon.name()}`",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
    await ch.send(embed=em)

async def open_inventory(user,ch):
    player = box.players[user.id]
    inventory_em1 = discord.Embed(
        title="Inventory",
        description=(
            "\n`1.`Item"
            + "\n`2.`Weapon"
    ))
    inventory_em2 = discord.Embed(description="`該当する番号を半角英数字で送信してください`")
    msg1 = await ch.send(embed=inventory_em1)
    msg2 = await ch.send(embed=inventory_em2)
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
    try:
        msg = await client.wait_for("message", timeout=60, check=check3)
        await msg.delete()
        await msg2.delete()
    except asyncio.TimeoutError:
        em = discord.Embed(description=f"指定がないので処理を終了しました")
        await shop_msg2.edit(embed=em)
    else:
        respons = int(msg.content)
        if respons == 1:
            await i_inventory(player,ch)
        if respons == 2:
            await w_inventory(player,ch)

#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨

# STP振り分け #
async def share_stp(user, ch):
    player = box.players[user.id]
    em = discord.Embed(
        title="Custom Status",
        description=f"強化する項目に対応する番号を送信してください\n`1.`┃`Strength(攻撃力)`\n`2.`┃`Defense (防御力)`\n`3.`┃`Agirity (俊敏力)`"
    )
    point_msg = await ch.send(embed=em)
    def check(m):
        if not user.id == m.author.id:return 0
        return 1
    def check2(m):
        if not user.id == m.author.id:return 0
        if not m.content.isdigit():return 0
        return 1
    try:
        msg = await client.wait_for("message", timeout=60, check=check2)
    except asyncio.TimeoutError:
        em = discord.Embed(
            title="BuildUp Status",
            description=f"指定がないので処理を終了しました")
        await point_msg.edit(embed=em)
    else:
        target,target2 = msg.content,""
        if target == "0":
            em = discord.Embed(
                title="BuildUp Status",
                description=f"処理をキャセルン")
            await point_msg.edit(embed=em)
            return
        elif target == "1":
            target,target2 = "str","Strength"
        elif target == "2":
            target,target2 = "def","Defense"
        elif target == "3":
            target,target2 = "agi","Agirity"
        else:
            em = discord.Embed(
                title="BuildUp Status",
                description=f"指定番号に対応する項目がないので処理をキャセルンしました")
            await ch.send(embed=em)
            return
        em = discord.Embed(
            title="BuildUp Status",
            description=f"**{target2}**を強化する量を送信してください\n所持StatusPoint: **{player.now_stp()}**"
        )
        await point_msg.edit(embed=em)
        try:
            msg2 = await client.wait_for("message", timeout=60, check=check2)
        except asyncio.TimeoutError:
            em = discord.Embed(
                title="BuildUp Status",
                description=f"指定がないので処理をキャセルンしました")
            await point_msg.edit(embed=em)
        else:
            point = int(msg2.content)
            if player.now_stp() < point:
                em = discord.Embed(
                    title="BuildUp Status",
                    description=f"所持StatusPointを**{point-player.now_stp()}**(Max{player.now_stp()})超過しているので処理をキャセルンしました")
                await point_msg.edit(embed=em)
                return
            target_stp = player.share_stp(target,point)
            em = discord.Embed(
                title="BuildUp Status",
                description=f"**{target2}**の強化量を**+{point}**しました\n所持StatusPoint: **{player.now_stp()}**\n{target2}強化量: **{target_stp}**")
            await point_msg.edit(embed=em)

#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨

# レベル上限解放 #
async def up_max_lv(user,ch):
    player = box.players[user.id]
    item_num = pg.fetchdict(f"SELECT item->'魔石' as item_num FROM player_tb where id = {user.id};")[0]["item_num"]
    if item_num < 250:
        husoku = 250 - item_num 
        em = discord.Embed(description=f"<@{user.id}> のレベル上限解放には魔石が{husoku}個不足しています")
        await ch.send(embed=em)
        return
    item_num -= 250
    player.max_lv(1000)
    player.get_exp(1)
    em = discord.Embed(description=f"<@{user.id}> のレベル上限が1000解放されました！")
    await ch.send(embed=em)
    get_item(user,6,-250)

#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨

# アイテムの確保 #
def get_item(user, item_id, num):
    player = box.players[user.id]
    item = box.items_name[item_id]
    item_num = pg.fetchdict(f"SELECT item->'{item}' as item_num FROM player_tb where id = {user.id};")[0]["item_num"]
    pg.execute(f"update player_tb set item = item::jsonb||json_build_object('{item}', {item_num + num})::jsonb where id = {user.id};")
    


material_items = (4,5,6,7)

#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨

# アイテムの使用 #
async def use_item(user, ch, item):
    player = box.players[user.id]
    if player.now_hp <= 0:
        em = discord.Embed(description=f"<@{user.id}> はもう死んでいる…")
        await ch.send(embed=em)
        return
    if item in list(items_name.keys()):
        item_name = items_name[item]
    elif not item in list(items_id.keys()):
        em = discord.Embed(description=f"{item}と言うアイテムは見たことがないようだ…")
        await ch.send(embed=em)
        return
    if items_id[item] in material_items:
        em = discord.Embed(description=f"{item}は素材系アイテムのようだ…")
        await ch.send(embed=em)
        return
    item_num = pg.fetchdict(f"SELECT item->'{item}' as item_num FROM player_tb where id = {user.id};")[0]["item_num"]
    if item_num <= 0:
        em = discord.Embed(description=f"<@{player.user.id}>のインベントリに{item}は無いようだ…")
        await ch.send(embed=em)
        return
    if not item in list(constant_items_name.values()):
        item_num -= 1
        pg.execute(f"update player_tb set item = item::jsonb||json_build_object('{item}', {item_num})::jsonb where id = {user.id};")
    item_em = None
    if item == "HP回復薬":
        print("HP回復薬:",player.user)
        if player.now_hp < player.max_hp:
            player.now_hp += 500
            text = f"<@{player.user.id}>のHPが500回復"
            item_em = discord.Embed(description=text)
        else:
            item_em = discord.Embed(description=f"HPは既に満タンのようだ…無駄消費乙！")
    if item == "MP回復薬":
        if player.now_mp < player.max_mp:
            player.now_mp += 500
            text = f"<@{player.user.id}>のMPが500回復"
            item_em = discord.Embed(description=text)
        else:
            item_em = discord.Embed(description=f"MPは既に満タンのようだ…無駄消費乙！")
    if item == "HP全回復薬":
        if player.now_hp < player.max_hp:
            cure_num = player.max_hp
            if player.now_hp + cure_num > player.max_hp:
                  player.now_hp = player.max_hp
                  text = f"<@{player.user.id}>のHPが全回復！"
            else:
                  player.now_hp += cure_num
                  text = f"<@{player.user.id}>のHPが{cure_num}回復"
            item_em = discord.Embed(description=text)
        else:
            item_em = discord.Embed(description=f"HPは既に満タンのようだ…無駄消費乙！")
    if item == "MP全回復薬":
        if player.now_mp < player.max_mp:
            cure_num = player.max_mp
            if player.now_mp + cure_num > player.max_mp:
                  player.now_mp = player.max_mp
                  text = f"<@{player.user.id}>のMPが全回復！"
            else:
                  player.now_mp += cure_num
                  text = f"<@{player.user.id}>のMPが{cure_num}回復"
            item_em = discord.Embed(description=text)
        else:
            item_em = discord.Embed(description=f"MPは既に満タンのようだ…無駄消費乙！")
    if item == "魔硬貨":
        result = random.choice(("裏","表"))
        item_em = discord.Embed(description=f"コインを投げた…{result}!")
    if item == "冒険者カード":
        players_ranking = [ i["id"] for i in pg.fetchdict(f"SELECT id FROM player_tb order by lv desc;") ]
        player_ranking = players_ranking.index(user.id) + 1
        embed = discord.Embed(title="Adventure Info")
        embed.add_field(name="Name",value=f"*{player.user.name}*")
        embed.add_field(name="MagicRegion",value=f"*{player.magic_class()}: Lv.{player.magic_lv()}*")
        embed.add_field(name="Money",value=f"*{player.money()}cell*")
        embed.add_field(name="KillCount",value=f"*{player.kill_count()}*")
        embed.add_field(name="LevelRanking",value=f"*{player_ranking} / {len(players_ranking)}*")
        if player.battle_ch:
            cbt_ch = client.get_channel(player.battle_ch)
            embed.add_field(name="BattlePlace",value=f"{cbt_ch.mention}")
        embed.set_thumbnail(url=user.avatar_url)
        embed.timestamp = datetime.now(JST)
        await ch.send(embed=embed)



    if item_em:
        if item in items_image:
            item_em.set_thumbnail(url=items_image[item])
        await ch.send(embed=item_em)

#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨

async def open_pouch(user,ch):
    player = box.players[user.id]
    item1_name = player.pouch(1)
    item2_name = player.pouch(2)
    item3_name = player.pouch(3)
    text = ''
    text += f'\n`1.`┃`{item1_name}`'
    text += f'\n`2.`┃`{item2_name}`'
    text += f'\n`3.`┃`{item3_name}`'
    pouch_em = discord.Embed(title='Player Pouch',description=text)
    await ch.send(embed=pouch_em)

async def use_pouch(user,ch,num):
    player = box.players[user.id]
    item_name = player.pouch(num)
    await use_item(user,ch,item_name)

async def set_pouch(user,ch,num,item):
    if not item in list(items_name.values()):
        em = discord.Embed(description=f"{item}と言うアイテムは見たことがないようだ…")
        await ch.send(embed=em)
        return
    player = box.players[user.id]
    player.pouch(num,set_item=item)
    text = f"Pouchの**{num}**枠目に**{item}**{box.items_emoji[box.items_id[item]]}をセット"
    pouch_em = discord.Embed(description=text)
    await ch.send(embed=pouch_em)
    

#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨

async def set_weapon(user,ch):
    player = box.players[user.id]
    menu_em = discord.Embed(
        title="Weapon Menu",
        description=(
            "\n`1.`武器一覧"
            + "\n`2.`武器装備"
            + "\n`3.`~~武器強化~~"
            + "\n`4.`武器作成"
            + "\n`5.`武器消去"
    ))
    menu_msg = await ch.send(embed=menu_em)
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
        if user.id != m.author.id:
            return 0
        pattern = r'^(\d+) (\d+)$'
        result = re.search(pattern, m.content)
        if result or m.content == "0":
            return 1
    try:
        msg = await client.wait_for("message", timeout=60, check=check3)
    except asyncio.TimeoutError:
        menu_msg.embeds[0].add_field(name="※tips",value="処理終了")
        await menu_msg.edit(embed=menu_msg.embeds[0])
    else:
        await msg.delete()
        respons = int(msg.content)
        if respons == 0:
            menu_msg.embeds[0].add_field(name="※tips",value="処理終了")
            await menu_msg.edit(embed=menu_msg.embeds[0])
        if respons == 1:
            await w_inventory(player,ch)
        if respons == 2:
            if player.weapons() != []:
                weapons_num = []
                def create_em():
                    global weapon_num
                    weapon_num = []
                    num = 0
                    em = discord.Embed(title="Set Weapon")
                    for weapon in player.weapons():
                        if player.weapon() and weapon.id == player.weapon().id:
                            em.add_field(name=f"▷{weapon.emoji()}{weapon.name()}",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                        else:
                            num += 1
                            em.add_field(name=f"`{num}.`{weapon.emoji()}`{weapon.name()}`",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                            weapons_num.append(weapon)
                    return em
                em = create_em()
                em.add_field(name="※tips",value="装備する武器の番号を送信してください。\n0と送信するとキャンセルします。")
                set_weapon_menu_msg = await ch.send(embed=em)
                try:
                    msg = await client.wait_for("message", timeout=60, check=check3)
                    await msg.delete()
                except asyncio.TimeoutError:
                    em = create_em()
                    em.add_field(name="※tips",valuet="処理終了")
                    await set_weapon_menu_msg.edit(embed=em)
                else:
                    num = int(msg.content)
                    if num == 0:
                        em = create_em()
                        em.add_field(name="※tips",value="処理終了")
                        await menu_msg.edit(embed=em)
                    else:
                        weapon = weapons_num[num-1]
                        player.weapon(weapon=weapon)
                        em = create_em()
                        em.add_field(name="※tips",value="処理終了")
                        await menu_msg.edit(embed=em)
        if respons == 3:
            def check4(m):
                if not user.id == m.author.id:return 0
                if not m.content.isdigit() and not m.content=="ok":return 0
                return 1
            def reload_em():
                weapons_obj = player.weapons()
                weapon_obj = player.weapon()
                weapons_em = discord.Embed(title="Buildup Weapon")
                for num,obj in zip(range(1,len(weapons_obj)+1),weapons_obj):
                    if obj.id == weapon_obj.id:
                        name = f"`{num}.`{obj.emoji()}**{obj.name()}**"
                    else:
                        name = f"`{num}.`{obj.emoji()}{obj.name()}"
                    value = f"Rank.{obj.rank()}┃Lv.{obj.lv()}/{obj.limit_lv()}┃Atk.{obj.strength()}"
                    weapons_em.add_field(name=name,value=value,inline=False)
                return weapons_em
            weapons_em = reload_em()
            weapons_em.add_field(name="※tips",value="強化する武器の番号を送信してください。")
            menu_msg = await ch.send(embed=weapons_em)
            while True:
                try:
                    re_msg = await client.wait_for("message",timeout=60,check=check3)
                    await re_msg.delete()
                except asyncio.TimeoutError:
                    weapons_em = reload_em()
                    weapons_em.add_field(name="※tips",value="処理終了")
                    await menu_msg.edit(embed=weapons_em)
                    break
                else:
                    weapon_num = int(re_msg.content)
                    if weapon_num == 0:
                        weapons_em.add_field(name="※tips",value="処理終了")
                        await menu_msg.edit(embed=weapons_em)
                        break
                    if not weapon_num in range(1,len(player.weapons())+1):
                        weapons_em.add_field(name="※tips",value="該当する武器がありません。")
                        await menu_msg.edit(embed=weapons_em)
                        continue
                    target_weapon_obj = player.weapons()[weapon_num-1]
                    materials = []
                    materials_info_set = (
                        (1,29,5),
                        (2,30,15)
                    )
                    material_exp_dict = {
                        29:5,
                        30:15
                    }
                    def reload_em2():
                        buildup_em = discord.Embed(title="Buildup Weapon")
                        buildup_em.add_field(name='強化武器',value=f"{target_weapon_obj.emoji()}{target_weapon_obj.name()}")
                        material_text = ""
                        for item_info in materials_info_set:
                            num = player.item_num(item_info[1])
                            if num:
                                material_text += f"{box.items_emoji[item_info[1]]}×{num} "
                        if material_text == "":
                            material_text = "強化素材がありません"
                        buildup_em.add_field(name=f"強化素材",value=material_text)
                        if materials != []:
                            use_material_text = ""
                            for item in materials:
                                use_material_text += f"{box.items_emoji[item[0]]}×{item[1]} "
                        else:
                            use_material_text = "未選択"
                        buildup_em.add_field(name=f"使用する強化素材",value=use_material_text)
                        return buildup_em
                    buildup_em = reload_em2()
                    buildup_em.add_field(name="※tips",value="素材の使用数を順番に入力してください。0も可能です。\n`ok`と送信すると強化を開始します。")
                    await menu_msg.edit(embed=buildup_em)
                    material_num_em = discord.Embed()
                    material_msg = await ch.send(embed=material_num_em)
                    for item_info in materials_info_set:
                        item_id = item_info[1]
                        item_num = player.item_num(item_id)
                        if item_num <= 0:
                            continue
                        em = discord.Embed(description=f"{box.items_emoji[item_id]}**{box.items_name[item_id]}**\n所持数: `{item_num}`")
                        await material_msg.edit(embed=em)
                        try:
                            re_material_num_msg = await client.wait_for("message",timeout=60,check=check3)
                        except asyncio.TimeoutError:
                            weapons_em = reload_em()
                            weapons_em.add_field(name="※tips",value="処理終了")
                            await menu_msg.edit(embed=weapons_em)
                        else:
                            if re_material_num_msg.content == "ok":
                                buildup_em = reload_em2()
                                buildup_em.add_field(name="※tips",value="武器強化を開始します。")
                                await menu_msg.edit(embed=buildup_em)
                                break
                            use_num = int(re_material_num_msg.content)
                            if item_num >= use_num:
                                materials.append((item_id,use_num))
                                buildup_em = reload_em2()
                                buildup_em.add_field(name="※tips",value="素材の使用数を順番に入力してください。0も可能です。\n`ok`と送信すると強化を開始します。")
                                await menu_msg.edit(embed=buildup_em)
                            else:
                                buildup_em = reload_em2()
                                em = discord.Embed(desciprion=f"所持数以下の数値にしてください。\n{box.items_emoji[item_id]}**{box.items_name[item_id]}**\n所持数: `{item_num}`")
                                await material_msg.edit(embed=em)
                    materials = tuple(materials)
                    all_exp = 0
                    await material_msg.delete()
                    if len(materials) > 0:
                        for info_set in materials:
                            item_id, item_num = info_set
                            all_exp += material_exp_dict[item_id]*item_num
                            # get_item(user, item_id,item_num)
                        await ch.send(content=f"現在未実装ですが、計算上**{all_exp}**Expを取得できます。")



        if respons == 4:
            split_num = 5
            split_weapons = tuple(split_list(box.player_weapons,split_num))
            em_title = "Create Weapon"
            rank_dict = {1:"D",2:"C",3:"B",4:"A",5:"S"}
            embeds = []
            weapons = []
            recipe_select_by_weapon_num = [ box.weapons_recipe[i[2]-1] for i in box.player_weapons]
            rankrate_select_by_weapon_num = [ box.rank_rate[i[2]-1] for i in box.player_weapons]
            for page_num,weapons_data in zip(range(1,100),split_weapons):
                em = discord.Embed(title=em_title,description=f"所持Cell:{player.money()}")
                for weapon_num_on_page,weapon_data in zip(range(1,100),weapons_data):
                    recipe_text = ""
                    for material_num,emoji in zip(box.weapons_recipe[weapon_data[2]-1],box.material_emoji):
                        if material_num > 0:
                            recipe_text += f"{emoji}×{material_num} "
                    em.add_field(name=f"\n`{weapon_num_on_page}.`{weapon_data[1]}{weapon_data[0]}",value=f"**Price**: {box.weapons_price[weapon_data[2]-1]}cell\n**Recipe**: {recipe_text}",inline=False)
                em.set_footer(text=f"Page.{page_num}/{len(split_weapons)}")
                embeds.append(em)
            embeds = tuple(embeds)
            page_num = 0
            embeds[0].add_field(
                name="※tips",
                value=f'{box.menu_emojis2["left"]}{box.menu_emojis2["right"]}:ページ切り替え\n{box.menu_emojis2["close"]}:処理終了\n{box.menu_emojis2["create_mode"]}:作成モードに変更'
            )
            weapon_drop_menu_msg = await ch.send(embed=embeds[0])
            menu_flag = True
            while True:
                create_mode = False
                if menu_flag is False:
                    break
                if not create_mode:
                    for emoji in tuple(box.menu_emojis2.values()):
                        await weapon_drop_menu_msg.add_reaction(emoji)
                    def check_react(r,u):
                        if r.message.id != weapon_drop_menu_msg.id:
                            return 0
                        if u.id != user.id:
                            return 0
                        if not str(r.emoji) in tuple(box.menu_emojis2.values()):
                            return 0
                        return 1
                    try:
                        reaction,msg = None,None
                        reaction, user = await client.wait_for("reaction_add",check=check_react,timeout=60.0)
                    except asyncio.TimeoutError:
                        embeds[0].add_field(name="※tips",value="処理終了")
                        await weapon_drop_menu_msg.edit(embed=embeds[0])
                        await weapon_drop_menu_msg.clear_reactions()
                        break
                    else:
                       footer_text=f'{box.menu_emojis2["left"]}{box.menu_emojis2["right"]}:ページ切り替え\n{box.menu_emojis2["close"]}:処理終了\n{box.menu_emojis2["create_mode"]}:作成モードに変更'
                       if reaction:
                            before_page_num = page_num
                            emoji = str(reaction.emoji)
                            if emoji == box.menu_emojis2["right"]:
                                page_num += 1
                            if emoji == box.menu_emojis2["left"]:
                                page_num -= 1
                            if emoji == box.menu_emojis2["right2"]:
                                page_num += 2
                            if emoji == box.menu_emojis2["left2"]:
                                page_num -= 2
                            if emoji == box.menu_emojis2["create_mode"]:
                                create_mode = True
                            if emoji == box.menu_emojis2["close"]:
                                embeds[0].add_field(name="※tips",value="処理終了")
                                await weapon_drop_menu_msg.edit(embed=embeds[0])
                                await weapon_drop_menu_msg.clear_reactions()
                                break
                            if before_page_num != page_num:
                                await weapon_drop_menu_msg.clear_reactions()
                            if create_mode:
                                await weapon_drop_menu_msg.clear_reactions()
                                footer_text=f'作成モードです。対応する武器の番号を送信してください。武器スロットが５枠すべて埋まっていると作成できません。\n`0`を送信すると終了します。'
                            page_num = max(0,(min(page_num,len(embeds)-1)))
                            shop_em3 = embeds[page_num]
                            shop_em3.add_field(name="※tips",value=footer_text)
                            await weapon_drop_menu_msg.edit(content=content,embed=shop_em3)
                while create_mode:
                    try:
                        msg = await client.wait_for("message", timeout=60, check=check3)
                        await msg.delete()
                    except asyncio.TimeoutError:
                        footer_text="処理終了"
                        if len(weapon_drop_menu_msg.embeds):
                            weapon_drop_menu_msg.embeds[0].add_field(name="※tips",value=footer_text)
                            await weapon_drop_menu_msg.edit(embed=weapon_drop_menu_msg.embeds[0])
                        create_mode = False
                        menu_flag = False
                        break
                    else:
                        msg_num = int(msg.content)
                        if msg_num > split_num or msg_num < 0:
                            footer_text=f"{msg_num}は指定できない数値です。"
                            if len(weapon_drop_menu_msg.embeds):
                                weapon_drop_menu_msg.embeds[0].add_field(name="※tips",value=footer_text)
                                await weapon_drop_menu_msg.edit(embed=weapon_drop_menu_msg.embeds[0])
                            continue
                        if msg.content == "0":
                            footer_text=f"処理終了"
                            if len(weapon_drop_menu_msg.embeds):
                                weapon_drop_menu_msg.embeds[0].add_field(name="※tips",value=footer_text)
                                await weapon_drop_menu_msg.edit(embed=weapon_drop_menu_msg.embeds[0])
                            create_mode = False
                            menu_flag = False
                            break
                        if len(player.weapons()) >= 5:
                            footer_text=f"武器インベントリがいっぱいなので処理を終了しました。"
                            if len(weapon_drop_menu_msg.embeds):
                                weapon_drop_menu_msg.embeds[0].add_field(name="※tips",value=footer_text)
                                await weapon_drop_menu_msg.edit(embed=weapon_drop_menu_msg.embeds[0])
                            menu_flag = False
                            break
                        weapon_num = int(msg.content) + (page_num)*split_num
                        weapon_info_id = box.player_weapons[weapon_num - 1][2] - 1
                        weapon_name = box.player_weapons[weapon_num - 1][0]
                        weapon_emoji = box.player_weapons[weapon_num - 1][1]
                        weapon_price = box.weapons_price[weapon_info_id]
                        weapon_recipe = tuple(box.weapons_recipe[weapon_info_id])
                        weapon_rank_rate = box.rank_rate[weapon_info_id]
                        materials_name = ("魂の焔","キャラメル鋼","ブラッド鋼","ゴールド鋼","ダーク鋼","ミスリル鋼","オリハルコン鋼","鉄")
                        husoku_text = ""
                        if msg_num > len(embeds)-1 or msg_num < 0:
                            footer_text=f"{msg_num}は指定できない数値です。"
                            if len(weapon_drop_menu_msg.embeds):
                                weapon_drop_menu_msg.embeds[0].add_field(name="※tips",value=footer_text)
                                await weapon_drop_menu_msg.edit(embed=weapon_drop_menu_msg.embeds[0])
                            continue
                        for name,emoji,num in zip(materials_name, box.material_emoji, weapon_recipe):
                            if num > player.item_num(name):
                                husoku_text += f"{emoji}×{num-player.item_num(name)} "
                        if player.money() < weapon_price:
                            husoku_text = f"{weapon_price-player.money()}Cell " +  husoku_text
                        if husoku_text != "":
                            footer_text=f"{husoku_text} が足りません。終了する場合は0を送信。"
                            if len(weapon_drop_menu_msg.embeds):
                                weapon_drop_menu_msg.embeds[0].add_field(name="※tips",value=footer_text)
                                await weapon_drop_menu_msg.edit(embed=weapon_drop_menu_msg.embeds[0])
                            continue
                        for name,num in zip(materials_name, weapon_recipe):
                            item_id = box.items_id[name]
                            if num > 0:
                                get_item(user,item_id,-num)
                        rank = 1
                        for i in (1,2,3,4):
                            if random.random() <=weapon_rank_rate:
                                rank += 1
                        weapon_obj = player.create_weapon(weapon_name,weapon_emoji,rank)
                        player.get_weapon(weapon_obj)
                        player.money(-weapon_price)
                        footer_text=f"{weapon_obj.emoji()}{weapon_obj.name()}(Rank.{weapon_obj.rank()})を作成しました。終了する場合は0を送信。"
                        if len(weapon_drop_menu_msg.embeds):
                            weapon_drop_menu_msg.embeds[0].add_field(name="※tips",value=footer_text)
                            await weapon_drop_menu_msg.edit(embed=weapon_drop_menu_msg.embeds[0])



        if respons == 5:
            if player.weapons() != []:
                weapons_num = []
                def create_em():
                    global weapon_num
                    weapon_num = []
                    num = 0
                    em = discord.Embed(title="Drop Weapon")
                    for weapon in player.weapons():
                        if player.weapon() and weapon.id == player.weapon().id:
                            em.add_field(name=f"▷{weapon.emoji()}{weapon.name()}",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                        else:
                            num += 1
                            em.add_field(name=f"`{num}.`{weapon.emoji()}`{weapon.name()}`",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                            weapons_num.append(weapon)
                    return em
                em = create_em()
                if len(player.weapons()) <= 0:
                    em.add_field(name="※tips",value="捨てられる武器がありません。\n処理終了")
                    await ch.send(embed=em)
                    return
                em.add_field(name="※tips",value="捨てる武器の番号を送信して下さい。\n`0`を送信すると処理停止。")
                drop_weapon_menu_msg = await ch.send(embed=em)
                while True:
                    try:
                        drop_weapon_num_msg = await client.wait_for("message", timeout=60, check=check3)
                        await drop_weapon_num_msg.delete()
                    except asyncio.TimeoutError:
                        em.add_field(name="※tips",value="処理終了")
                        await drop_weapon_menu_msg.edit(embed=em)
                        break
                    else:
                        drop_weapon_num = int(drop_weapon_num_msg.content)
                        if drop_weapon_num == 0:
                            em.add_field(name="※tips",value="処理終了")
                            await drop_weapon_menu_msg.edit(embed=em)
                            break
                        else:
                            weapons_which_player_has = []
                            num = 0
                            for weapon in player.weapons():
                                if player.weapon() and not weapon.id == player.weapon().id:
                                    weapons_which_player_has.append(weapon)
                            player.drop_weapon(weapon=weapon)
                            weapon = weapons_which_player_has[drop_weapon_num-1]
                            em = create_em()
                            em.add_field(name="※tips",value="指定武器を捨てました。\n`0`と送信すると処理終了。")
                            await drop_weapon_menu_msg.edit(embed=em)
            
