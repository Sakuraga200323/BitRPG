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
    mc = p_data.magic_class_
    embed = discord.Embed(title="Player Status Board",color=0xe1ff00 if mc == 1 else 0x8f6200 if mc == 2 else 0x2e3cff)
    embed.add_field(name=f"Player", value=f"{p_data.user.mention}", inline=False)
    embed.add_field(name=f"Level (Now/Limit)", value=f"`{p_data.lv()}/{p_data.max_lv()}`")
    embed.add_field(name=f"MagicLevel", value=f"`{p_data.magic_class()} Lv.{p_data.magic_lv()}`")
    if p_data.magic_class() == "Armadillo":
        embed.add_field(name=f"HitPoint (Now/Max)", value=f"{p_data.now_hp}/{p_data.max_hp} (+10%)", inline=False)
    else:
        embed.add_field(name=f"HitPoint (Now/Max)", value=f"{p_data.now_hp}/{p_data.max_hp}`", inline=False)
    if p_data.magic_class() == "Orca":
        embed.add_field(name=f"MagicPoint (Now/Max)", value=f"{p_data.now_mp}/{p_data.max_mp} (+10%)", inline=False)
    else:
        embed.add_field(name=f"MagicPoint (Now/Max)", value=f"{p_data.now_mp}/{p_data.max_mp}", inline=False)
    strength_text = f"{p_data.STR()} (+{p_data.str_p()}"
    if p_data.magic_class() == "Wolf":
        strength_text += " +10%"
    if p_data.weapon():
        strength_text += f" {p_data.weapon().emoji()}+{p_data.weapon().strength()}"
    strength_text += ")"
    embed.add_field(name=f"Strength", value=strength_text)
    if p_data.magic_class() == "Armadillo":
        embed.add_field(name=f"Defense (Now/Limit)", value=f"{p_data.now_defe}/{p_data.max_defe} (+{p_data.defe_p()} +10%)")
    else:
        embed.add_field(name=f"Defense (Now/Limit)", value=f"{p_data.now_defe}/{p_data.max_defe} (+{p_data.defe_p()})")
    if p_data.magic_class() == "Orca":
        embed.add_field(name=f"Agility", value=f"{p_data.AGI()} (+{p_data.agi_p()} +10%)")
    else:
        embed.add_field(name=f"Agility", value=f"{p_data.AGI()} (+{p_data.agi_p()})")
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
        if not user.id == m.author.id:return 0
        pattern = r'^(\d+) (\d+)$'
        if not re.search(pattern, m.content) and not m.content == "0":return 0
        return 1
    try:
        msg = await client.wait_for("message", timeout=60, check=check3)
    except asyncio.TimeoutError:
        await menu_msg.edit(content="```時間経過により処理終了済み```")
    else:
        await msg.delete()
        respons = int(msg.content)
        if respons == 0:
            await menu_msg.edit(content="```時間経過により処理終了済み```")
            return
        if respons == 1:
            await w_inventory(player,ch)
        if respons == 2:
            if player.weapons() != []:
                em = discord.Embed(title="Set Weapon")
                weapons_num = []
                num = 0
                for weapon in player.weapons():
                    if player.weapon() and weapon.id == player.weapon().id:
                        em.add_field(name=f"▷{weapon.emoji()}{weapon.name()}",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                    else:
                        num += 1
                        em.add_field(name=f"`{num}.`{weapon.emoji()}`{weapon.name()}`",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                        weapons_num.append(weapon)
                msg0 = await ch.send(content="```装備する武器の番号を送信してください。\n0と送信するとキャンセルします。```",embed=em)
                def check3(m):
                    if not user.id == m.author.id:return 0
                    if not m.content.isdigit():return 0
                    return 1
                try:
                    msg = await client.wait_for("message", timeout=60, check=check3)
                    await msg.delete()
                except asyncio.TimeoutError:
                    await menu_msg.edit(content="```時間経過により処理終了済み```")
                else:
                    num = int(msg.content)
                    if num == 0:
                        await menu_msg.edit(content="```キャンセルされました```")
                    else:
                        weapon = weapons_num[num-1]
                        player.weapon(weapon=weapon)
                        em = discord.Embed(title="Set Weapon")
                        for weapon in player.weapons():
                            if player.weapon() and weapon.id == player.weapon().id:
                                em.add_field(name=f"▷{weapon.emoji()}{weapon.name()}",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                            else:
                                em.add_field(name=f"{weapon.emoji()}`{weapon.name()}`",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                            weapons_num.append(weapon)
                        await msg0.edit(content="```装備完了```",embed=em)
        if respons == 4:
            split_weapons = tuple(split_list(box.player_weapons,8))
            em_title = "Create Weapon"
            rank_dict = {1:"D",2:"C",3:"B",4:"A",5:"S"}
            embeds = []
            weapons = []
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
            weapon_drop_menu_msg = await ch.send(
                content=f'`リアクションでページ切り替えです。`\n{box.menu_emojis2["left"]}:一つページを戻す\n{box.menu_emojis2["close"]}:処理を終了する\n{box.menu_emojis2["right"]}:一つページを進める\n{box.menu_emojis2["create_mode"]}:作成モードに変更',
                embed=embeds[0]
            )
            menu_flag = True
            while True:
                create_mode = False
                if menu_flag is False:
                    break
                if not create_mode:
                    for emoji in tuple(box.menu_emojis2.values()):
                        await weapon_drop_menu_msg.add_reaction(emoji)
                    def check_react(r,u):
                        if r.message.id != shop_msg.id:
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
                        await weapon_drop_menu_msg.edit(
                            content="```時間経過により処理終了済み```",
                            embed=embeds[0]
                        )
                        await weapon_drop_menu_msg.clear_reactions()
                        break
                    else:
                       content=f'`リアクション、ページ番号送信でページ切り替えです。`\n{box.menu_emojis2["left"]}:一つページを戻す\n{box.menu_emojis2["close"]}:処理を終了する\n{box.menu_emojis2["right"]}:一つページを進める\n{box.menu_emojis2["create_mode"]}:作成モードに変更'
                       if reaction:
                            before_page_num = page_num
                            emoji = str(reaction.emoji)
                            if emoji == box.menu_emojis2["right"]:
                                if page_num < len(embeds)-1:
                                     page_num += 1
                            elif emoji == box.menu_emojis2["close"]:
                                await shop_msg.edit(
                                    content="```処理終了済み```",
                                    embed=embeds[0]
                                )
                                await weapon_drop_menu_msg.clear_reactions()
                                break
                            elif emoji == box.menu_emojis2["left"]:
                                if page_num > 0:
                                     page_num -= 1
                            elif emoji == box.menu_emojis2["create_mode"]:
                                create_mode = True
                            if before_page_num != page_num:
                                await weapon_drop_menu_msg.clear_reactions()
                            if create_mode:
                                await shop_msg.clear_reactions()
                                content=f'`購入モードです。対応する武器の番号を送信してください。武器スロットが５枠すべて埋まっていると購入できません。\n0を送信すると終了します。`'
                            shop_em3 = embeds[page_num]
                            await weapon_drop_menu_msg.edit(content=content,embed=shop_em3)
                while create_mode:
                    try:
                        msg = await client.wait_for("message", timeout=60, check=check3)
                        await msg.delete()
                    except asyncio.TimeoutError:
                        await weapon_drop_menu_msg.edit(
                            content="```時間経過により処理終了済み```"
                        )
                        create_mode = False
                        menu_flag = False
                        break
                    else:
                        if msg.content == "0":
                            await weapon_drop_menu_msg.edit(content="```処理終了済み```"
                            )
                            create_mode = False
                            menu_flag = False
                            break
                        weapon_id = int(msg.content) + (page_num)*6
                        weapon = box.npc_weapons[weapon_id]
                        if len(player.weapons()) >= 5:
                            await weapon_drop_menu_msg.edit(
                                content=f"```既に５個の武器を所持しています。\n処理終了済み```"
                            )
                            menu_flag = False
                            break
                        if player.money() < weapon.create_cost:
                            await weapon_drop_menu_msg.edit(
                                content=f"```{weapon.create_cost-player.money()}Cell足りません。\nそのまま購入を続けられます。終了する場合は0を送信。```"
                            )
                            continue
                        rank = 1
                        for i in range(1,weapon.max_rank-1):
                            if random.random() <= weapon.rate_of_rankup:
                                rank += 1
                                if rank == weapon.max_rank:
                                    create_mode = False
                                    break
                        weapon_obj = player.create_weapon(weapon.name,weapon.emoji,rank)
                        player.get_weapon(weapon_obj)
                        player.money(-weapon.create_cost)
                        await weapon_drop_menu_msg.edit(
                            content=f"{weapon.create_cost}cellで{weapon_obj.emoji()}{weapon_obj.name()}(Rank.{weapon_obj.rank()})を購入しました。\nそのまま購入を続けられます。終了する場合は0を送信。",
                        )
        if respons == 5:
            if player.weapons() != []:
                def check3(m):
                    if not user.id == m.author.id:return 0
                    if not m.content.isdigit():return 0
                    return 1
                em = discord.Embed(title="Drop Weapon")
                weapons_num = []
                num = 0
                for weapon in player.weapons():
                    if player.weapon() and weapon.id == player.weapon().id:
                        em.add_field(name=f"▷{weapon.emoji()}{weapon.name()}",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                    else:
                        num += 1
                        em.add_field(name=f"`{num}.`{weapon.emoji()}`{weapon.name()}`",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                        weapons_num.append(weapon)
                if num == 0:
                    await ch.send(embed=discord.Embed(title="Drop Weapon",description="現在装備中の武器以外に所持していません。"))
                    return
                drop_weapon_menu_msg = await ch.send(content="```消去する武器の番号を送信してください。\n0と送信するとキャンセルします。```",embed=em)
                while True:
                    try:
                        drop_weapon_num_msg = await client.wait_for("message", timeout=60, check=check3)
                        await drop_weapon_num_msg.delete()
                    except asyncio.TimeoutError:
                        await drop_weapon_menu_msg.edit(content="```時間経過により処理終了済み```")
                    else:
                        drop_weapon_num = int(drop_weapon_num_msg.content)
                        if drop_weapon_num == 0:
                            await drop_weapon_menu_msg.edit(content="```処理終了済み```")
                            break
                        else:
                            weapons_which_player_has = []
                            num = 0
                            for weapon in player.weapons():
                                if player.weapon() and not weapon.id == player.weapon().id:
                                    weapons_which_player_has.append(weapon)
                            player.drop_weapon(weapon=weapon)
                            weapon = weapons_which_player_has[drop_weapon_num-1]
                            em = discord.Embed(title="Drop Weapon")
                            for weapon,num in zip(player.weapons(),range(1,5)):
                                if player.weapon() and weapon.id == player.weapon().id:
                                    em.add_field(name=f"▷{weapon.emoji()}{weapon.name()}",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                                else:
                                    em.add_field(name=f"`{num}.`{weapon.emoji()}`{weapon.name()}`",value=f"`Rank.{weapon.rank()}┃Lv.{weapon.lv()}┃Atk.{weapon.strength()}`",inline=False)
                            await drop_weapon_menu_msg.edit(content="```消去完了。\n引き続き消去出来ます。\n終了する場合は0を送信。```",embed=em)
            
