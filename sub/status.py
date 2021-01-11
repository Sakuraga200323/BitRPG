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

# ^^i で消費しないアイテムの {ID:名前} #
constant_items_name = {1:"冒険者カード", 4:"魂の焔", 5:"砥石", 6:"魔石", 7:"魔晶", 8:"魔硬貨"}


items_name = {
    1:"冒険者カード",
    2:"HP回復薬",3:"MP回復薬",
    4:"魂の焔",
    5:"砥石",6:"魔石",7:"魔晶",8:"魔硬貨",
    9:"HP全回復薬",10:"MP全回復薬",
}

items_id = {
    "冒険者カード":1,
    "HP回復薬":2,"MP回復薬":3,
    "魂の焔":4,
    "砥石":5,"魔石":6,"魔晶":7,"魔硬貨":8,
    "HP全回復薬":9,"MP全回復薬":10,
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


# ステータス #
async def open_status(user,ch):
    if not user.id in box.players:
        return
    p_data = box.players[user.id]
    mc = p_data.magic_class_
    embed = discord.Embed(title="Player Status Board",color=0xe1ff00 if mc == 1 else 0x8f6200 if mc == 2 else 0x2e3cff)
    embed.add_field(name=f"Player", value=f"{p_data.user.mention}", inline=False)
    embed.add_field(name=f"Level (Now/Limit)", value=f"`{p_data.lv()}/{p_data.max_lv()}`")
    embed.add_field(name=f"MagicLevel", value=f"`{p_data.magic_class()} Lv.{p_data.magic_lv()}`")
    if p_data.magic_class() == "Armadillo":
        embed.add_field(name=f"HitPoint (Now/Max)", value=f"`{p_data.now_hp}/{p_data.max_hp} (+10%)`", inline=False)
    else:
        embed.add_field(name=f"HitPoint (Now/Max)", value=f"`{p_data.now_hp}/{p_data.max_hp}`", inline=False)
    if p_data.magic_class() == "Orca":
        embed.add_field(name=f"MagicPoint (Now/Max)", value=f"`{p_data.now_mp}/{p_data.max_mp} (+10%)`", inline=False)
    else:
        embed.add_field(name=f"MagicPoint (Now/Max)", value=f"`{p_data.now_mp}/{p_data.max_mp}`", inline=False)
    if p_data.magic_class() == "Wolf":
        embed.add_field(name=f"Strength", value=f"`{p_data.STR()} (+{p_data.str_p()} +10%)`")
    else:
        embed.add_field(name=f"Strength", value=f"`{p_data.STR()} (+{p_data.str_p()})`")
    if p_data.magic_class() == "Armadillo":
        embed.add_field(name=f"Defense (Now/Limit)", value=f"`{p_data.now_defe}/{p_data.max_defe} (+{p_data.defe_p()} +10%)`")
    else:
        embed.add_field(name=f"Defense (Now/Limit)", value=f"`{p_data.now_defe}/{p_data.max_defe} (+{p_data.defe_p()})`")
    if p_data.magic_class() == "Orca":
        embed.add_field(name=f"Agility", value=f"`{p_data.AGI()} (+{p_data.agi_p()} +10%)`")
    else:
        embed.add_field(name=f"Agility", value=f"`{p_data.AGI()} (+{p_data.agi_p()})`")
    embed.add_field(name=f"StatusPoint", value=f"`{p_data.now_stp()}`")
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


# インベントリ #
async def open_inventory(user,ch):
    item_dtd = pg.fetchdict(f"select item from player_tb where id = {user.id};")[0]["item"]
    text = "`ID.アイテム名　　`┃`所持数`\n"
    for (item_name,item_emoji) in zip((items_name.values()),list(items_emoji_a.values())):
        if not item_dtd[item_name] == 0:
            item_id = items_id[item_name]
            text += f"`{item_id:<2}.`{item_emoji}`{change_abc(item_name):　<6}`┃`{item_dtd[item_name]}`\n"
    embed = discord.Embed(title="Player Inventory Bord",description=f"{text}")
    await ch.send(embed=embed)


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
                    title="Custom Status",
                    description=f"所持StatusPointを**{point-player.now_stp()}**(Max{player.now_stp()})超過しているので処理をキャセルンしました")
                await point_msg.edit(embed=em)
                return
            target_stp = player.share_stp(target,point)
            em = discord.Embed(
                title="Custom Status",
                description=f"**{target2}**の強化量を**+{point}**しました\n所持StatusPoint: **{player.now_stp()}**\n{target2}強化量: **{target_stp}**")
            await point_msg.edit(embed=em)


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


# アイテムの確保 #
def get_item(user, item_id, num):
    player = box.players[user.id]
    item = items_name[item_id]
    item_num = pg.fetchdict(f"SELECT item->'{item}' as item_num FROM player_tb where id = {user.id};")[0]["item_num"]
    pg.execute(f"update player_tb set item = item::jsonb||json_build_object('{item}', {item_num + num})::jsonb where id = {user.id};")
    


material_items = (4,5,6,7)

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
            cure_num = int(player.max_hp * 0.3)
            if player.now_hp + cure_num > player.max_hp:
                  player.now_hp = player.max_hp
                  text = f"<@{player.user.id}>のHPが全回復！"
            else:
                  player.now_hp += cure_num
                  text = f"<@{player.user.id}>のHPが{cure_num}回復"
            item_em = discord.Embed(description=text)
        else:
            item_em = discord.Embed(description=f"HPは既に満タンのようだ…無駄消費乙！")
    if item == "MP回復薬":
        print("MP回復薬:",player.user)
        if player.now_mp < player.max_mp:
            cure_num = int(player.max_mp * 0.3)
            if player.now_mp + cure_num > player.max_mp:
                  player.now_mp = player.max_mp
                  text = f"<@{player.user.id}>のMPが全回復！"
            else:
                  player.now_mp += cure_num
                  text = f"<@{player.user.id}>のMPが{cure_num}回復"
            item_em = discord.Embed(description=text)
        else:
            item_em = discord.Embed(description=f"MPは既に満タンのようだ…無駄消費乙！")
    if item == "HP全回復薬":
        print("HP全回復薬:",player.user)
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
        print("MP全回復薬:",player.user)
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
        print("魔硬貨:",player.user)
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
    

