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

from sub import box, item, battle, help, stp, kaihou, rank, status
from anti_macro import anti_macro


class Postgres:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        psycopg2.extras.register_hstore(self.cur)

    def execute(self, sql):
        self.cur.execute(sql)

    def fetch(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    def fetchdict(self, sql):
        self.cur.execute (sql)
        results = self.cur.fetchall()
        dict_result = []
        for row in results:
            dict_result.append(dict(row))
        return dict_result


def inverse_lookup(d, x):
    for k,v in d.items():
        if x == v:
            return k
def split_n(text, n):
    return [ text[i*n:i*n+n] for i in range(len(text)/n) ]


# 時間軸、データベースのURL、ボットのToken、Client、pg変数設定
JST = timezone(timedelta(hours=+9), 'JST')
dsn = os.environ.get('DATABASE_URL')
token = os.environ.get('TOKEN')
client = discord.Client(intents=discord.Intents.all())
pg = Postgres(dsn)


# コマンド使用中のチャンネル、マクロ検知中のユーザー、検知に引っかかったユーザーと回数
cmd_lock = {}
macro_checking = []
doubt_count = {}


# 各特殊ゆーざーの皆さん
admin_list = [
    715192735128092713,
    710207828303937626,
    548058577848238080,]
clr_lv4 = [
    548058577848238080,
    561836530398789641]
clr_lv5 = [
    715192735128092713,
    710207828303937626,
    760514942205034497]

"""
create table player_tb(
    id bigint,
    lv bigint,
    max_exp bigint,
    now_exp bigint,
    now_stp bigint,
    str_p bigint,
    def_p bigint,
    agi_p bigint,
    magic_class int,
    magic_lv bigint,
    kill_count bigint,
    item jsonb,
    money bigint
)

"""

#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=f"起動中…"))
    """
    item_img = Image.open('image_files/game_icon.png')
    icon.item = icon.Item(
        get_icon(img,12,13),
        get_icon(img,24,2),
        get_icon(img,24,8),
        get_icon(img,42,8),
        get_icon(img,24,13)
    )"""

    for ch_data in pg.fetch("select id from mob_tb;")[0]:
        if not client.get_channel(ch_data):
            pg.execute(f"delete from mob_tb where id = {ch_data}")

    NOW = datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S")
    MEM = psutil.virtual_memory().percent
    LOG_CHANNELS = [i for i in client.get_all_channels() if i.name == "bitrpg起動ログ"]
    desc = (
        f"\n+Prefix\n^^"
        + f"\n+UsingMemory\n{MEM}%"
        + f"\n+Server\n{len(client.guilds)}")

    print(f"【報告】起動完了。\n使用メモリー{MEM}%")

    loop.start()

    await client.change_presence(activity=discord.Game(name=f"^^help║Server：C║Mem：{MEM} %"))
    for ch in LOG_CHANNELS:
        try:
            embed = discord.Embed(
                title = "BitRPG起動ログ",
                description = f"```diff\n{desc}```")
            embed.timestamp = datetime.now(JST)
            await ch.send(embed = embed)
        except:
            print("Error")

#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖

@tasks.loop(seconds=10)
async def loop():
    MEM = psutil.virtual_memory().percent
    sub_msg = ''
    if client.get_channel(761571389345759232).name=='true':
        sub_msg = "現在開発作業中につき停止中￤"
    await client.change_presence(activity=discord.Game(name=f"{sub_msg}^^url￤{len(client.guilds)}server"))

#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖

@client.event
async def on_guild_join(guild):
    log_ch = client.get_channel(752551728553132102)
    embed = discord.Embed(
        title="BitRPG導入ログ",
        description=f"{guild.name}({guild.id})が導入\n現在の導入数：{len(client.guilds)}"
    )
    embed.timestamp=datetime.now(JST)
    await log_ch.send(embed=embed)

#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖

@client.event
async def on_guild_remove(guild):
    log_ch = client.get_channel(752551728553132102)
    embed = discord.Embed(
        title="BitRPG撤去ログ",
        description=f"{guild.name}({guild.id})が撤去\n現在の導入数：{len(client.guilds)}"
    )
    embed.timestamp=datetime.now(JST)
    await log_ch.send(embed=embed)

#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖

ID = 763635688234942475
role_id = {
    "1️⃣":719176372773453835,
    "2️⃣":763640405534441472,
    "3️⃣":743323912837922906,
    "4️⃣":743323569668227143
}

@client.event
async def on_raw_reaction_add(payload):

    if payload.message_id == ID:
        if not payload.user_id in role_id.keys():return
        print(payload.user_id)
        guild_id = payload.guild_id
        guild = client.get_guild(guild_id)
        role = discord.utils.get(guild.roles, id=role_id[payload.emoji.name])

        if role is not None:
            print(role.name + " was found!")
            print(role.id)
            member = await guild.fetch_member(int(payload.user_id)); print("guild, member:",guild, member)
            if not member:
                return
            await member.add_roles(role)
            channel = await client.fetch_channel(payload.channel_id)
            em = discord.Embed(description=f"{role.mention}を{member.mention}に付与しました。")
            result_msg = await channel.send(embed=em)
            await asyncio.sleep(5)
            await result_msg.delete()
            print("done")

@client.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == ID:
        if not payload.user_id in role_id.keys():return
        print(payload.user_id)
        guild_id = payload.guild_id
        guild = client.get_guild(guild_id)
        role = discord.utils.get(guild.roles, id=role_id[payload.emoji.name])

        if role is not None:
            print(role.name + " was found!")
            print(role.id)
            member = await guild.fetch_member(int(payload.user_id)); print("guild, member:",guild, member)
            if not member:
                return
            await member.remove_roles(role)
            channel = await client.fetch_channel(payload.channel_id)
            em = discord.Embed(description=f"{role.mention}を{member.mention}から消去しました。")
            result_msg = await channel.send(embed=em)
            await asyncio.sleep(5)
            await result_msg.delete()
            print("done")

#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖

@client.event
async def on_message(message):
    global cmd_lock, macro_checking, doubt_count

    m_ctt = message.content
    m_em = message.embeds
    m_id = message.id
    m_ch = message.channel
    m_guild = message.guild
    m_author = message.author

    if m_author.id == 302050872383242240:
        if message.embeds:
            if message.embeds[0].description:
                desc = message.embeds[0].description
                if "表示順を" in desc:
                    id = desc.split("<@")[1].split(">")[0]

                    
    if m_ctt.startswith("^^") and not m_author.id in macro_checking and not m_author.bot:

        if client.get_channel(761571389345759232).name=='true':
            admin_user = m_author.id in admin_list+clr_lv4+clr_lv5
            clearance_lv3_user = "Clearance-Lv3" in [ i.name for i in m_author.roles]
            if not admin_user and not clearance_lv3_user:
                await m_ch.send('【警告】現在開発作業中につき、ClearanceLv3未満のプレイヤーのコマンド使用を制限しています。')
                return
        if cmd_lock.get(m_ch.id) is True:
            await m_ch.send("【警告】処理が終了するまで待機してください。\nコマンドロックが解除されない場合は`><fix`をお試しください。")
            return
        cmd_lock[m_ch.id] = True
        mob_id_list = [ i[0] for i in pg.fetch("select id from mob_tb;")]
        id = m_ch.id
        if not mob_id_list or (not id in mob_id_list):
            import sub.N_Mob
            mob_name = random.choice(list(sub.N_Mob.set.keys()))
            url = sub.N_Mob.set[mob_name]
            pg.execute(f"insert into mob_tb (name,id,lv,max_hp,now_hp,str,def,agi,img_url) values ('{mob_name}',{m_ch.id},1,10,10,10,10,10,'{url}');")
        try:
            try:
                check = random.random() >= 0.99
            finally:
                if check:
                    P_list = pg.fetch(f"select * from player_tb where id = {m_author.id};")
                    if not m_author.id in doubt_count:
                        doubt_count[m_author.id] = 0
                    check_flag = True
                    result = False
                    while check_flag == True:
                        flag = await m_ch.send("デデドン！！")
                        await asyncio.sleep(1)
                        check_id = flag.id
                        macro_checking.append(m_author.id)
                        img, num = await anti_macro.get_img(client)
                        cv2.imwrite('anti_macro/num_img/temp.png', img)
                        check_em = discord.Embed(
                            title = "マクロ検知ぃいい！！(迫真)",
                            description=f'{m_author.mention}さんのマクロチェックです。\n以下の画像に書かれている数字を20秒以内に**半角**で送信してください。\n※`CheckID『{check_id}』`')
                        check_em.set_image(url="attachment://temp.png")
                        await m_ch.send(embed=check_em,file=discord.File(fp="anti_macro/num_img/temp.png"))
                        def check(m):
                            if not m.author.id == m_author.id or m.channel.id != m_ch.id:
                                return 0
                            if not m.content in ['0','1','2','3','4','5','6','7','8','9']:
                                return 0
                            return 1
                        try:
                            answer = await client.wait_for('message', timeout=20, check=check)
                        except asyncio.TimeoutError:
                            doubt_count[m_author.id] += 1
                            temp = None
                            await m_ch.send(f'無回答!!　不正カウント+1(現在{doubt_count[m_author.id]})')
                            result = False
                        else:
                            temp = answer.content
                            if int(answer.content) == int(num):
                                await m_ch.send(f'正解!! 報酬として現レベル×10の経験値を配布しました。')
                                if not P_list == []:
                                    pg.execute(f'update player_tb set now_exp = now_exp + (lv*10) where id = {m_author.id};')
                                check_flag = False
                                result = True
                            elif str(num) != str(answer.content):
                                doubt_count[m_author.id] += 1
                                await m_ch.send(f'不正解!! 不正カウント+1(現在{doubt_count[m_author.id]})')
                                result = False
                        print(f"MacroCheck：({m_author.id}) TrueAnswer[{num}], UsersAnswer[{temp}]")
                        if doubt_count[m_author.id] >= 5:
                            check_flag = False
                            doubt_count[m_author.id] = 0
                            await m_ch.send(f'不正カウントが規定量に達しました。貴方のプレイヤーデータを即座に終了します。現在はテスト版なので、実際に消去はされません。')
                            # pg.execute(f"update player_tb set lv = 1, now_exp = 0, all_exp = 0, max_lv = 1000, str_stp = 0, def_stp = 0, agi_stp = o, stp = 0 where id = {m_author.id};")
                            # await m_ch.send(f"「この画像は誰が見てもわからんやろ！？」等の異議申し立てがある場合は`^^claim {check_id}`と送信してください。運営人の検知画像肉眼チェックの上然るべき対応をさせていただきます。")
                        embed=discord.Embed(title="マクロ検知ログ", color=0x37ff00)
                        embed.add_field(name="CheckID", value=check_id, inline=False)
                        embed.add_field(name="Result", value=result, inline=False)
                        embed.add_field(name="UserData", value=P_list, inline=False)
                        embed.set_image(url="attachment://temp.png")
                        await client.get_channel(763299968353304626).send(embed=embed, file=discord.File(fp="anti_macro/num_img/temp.png"))
            cmd_list = ["^^help","^^st","^^status","^^point","^^attack","^^atk","^^rank","^^item","^^reset","^^re"]


            # InviteURL #
            if m_ctt == "^^url":
                await m_ch.send(embed=discord.Embed(
                    title="Invite & Other URL",
                    description=(
                        "▶︎[BitRPGBot招待](https://discord.com/api/oauth2/authorize?client_id=715203558357598240&permissions=8&scope=bot)\n"
                        + "▶︎[公式鯖参加](https://discord.gg/NymwEUP)\n"
                        + "▶︎[公式HP](https://bitrpg.jimdosite.com/)\n"
                        + "▶︎[Github(運営メンバー紹介、コマンド、システム説明)](https://github.com/Sakuraga200323/BitRPG)"
                )))


            # ヘルプ #
            if m_ctt == "^^help":
                await m_ch.send("未実装です")
                return
                await help.help(client, m_ch, m_author)


            # ステータスの表示 #
            if m_ctt.startswith("^^st"):
                temp = m_ctt
                pattern = r"\^\^(st|^status|st (.+)|status (.+))$"
                result = re.search(pattern, temp)
                if result:
                    await status.send_bord(client, m_author, m_ch)


            # 戦闘 #
            if m_ctt.startswith("^^attack") or m_ctt.startswith("^^atk"):
                temp = m_ctt
                pattern = r"\^\^(atk|attack|atk (.+)|attack (.+))$"
                result = re.search(pattern, temp)
                if result:
                    await battle.cbt_proc(m_author,m_ch)


            # 戦闘から離脱 #
            if m_ctt.startswith("^^re"):
                temp = m_ctt
                pattern = r"\^\^(re|reset|reset (.+)|re (.+))$"
                result = re.search(pattern, temp)
                if result:
                    await battle.reset(m_author, m_ch)


            # STPの振り分け #
            if m_ctt.startswith("^^point"):
                pattern = r"^\^\^point (str|STR|def|DEF|agi|AGI) (\d{1,})$"
                result = re.search(pattern, m_ctt)
                if result:
                    stp.divid(m_author, m_ch, result)


            # チャンネルレベルランキングの表示 #
            if m_ctt == "^^rank m":
                ranking = rank.RankClass(client)
                ranking.channel(m_author,m_ch)


            # アイテム系 #
            if m_ctt.startswith("^^i"):
                pattern = r"\^\^(i|item) (.+)"
                pattern2 = r"^\^\^i$|^\^\^item$"
                result = re.search(pattern, m_ctt)
                result2 = re.search(pattern2, m_ctt)
                if result:
                    await item.use(client, m_ch, m_author, result.group(2))
                if result2:
                    await item.open(client, m_ch, m_author)


            # Lv上限解放 #
            if m_ctt == "^^gentotsu":
                await kaihou.kaihou_proc(client, m_ch, m_author)

            if m_ctt == '^^start':
                id_list = [ i[0] for i in pg.fetch("select id from player_tb;")]
                def check(m):
                    if not m.author.id == id:
                        return 0
                    return 1
                def check2(m):
                    if not m.author.id == id:
                        return 0
                    if not msg.content in ("y","Y","n","N"):
                        return 0
                    return 1
                if m_author.id in id_list:
                    await m_ch.send(f"【警告】登録済みです。全てのデータを消して再登録しますか？ yes->y no->n")
                    try:
                        msg = await client.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        return
                    else:
                        if msg.content in ("y","Y"):
                            await m_ch.send(f"再登録を致します。")
                            magic_type_flag = True
                        else:
                            pg.execute(f"delete from player_tb where id = {m_author.id}")
                            return
                await m_ch.send(f"{m_author.mention}さんの冒険者登録を開始。")
                magic_type_flag = False
                while not magic_type_flag is True:
                    magic_type_em = discord.Embed(
                        title=f"{m_author.name} の冒険者登録を開始",
                        description=
                            (f"所属する魔法領域の対応番号を**半角で**送信してください。"
                            +"\n`^^start`で際登録していただく事で変更は可能ですが、レベル等を引き継ぐ場合は"
                            +"[リアルマネー(BitCashギフトカード)](https://bitcash.jp/docs/purchase/familymart/index)で1000円請求します。"
                            +"詳しくは[GitHub](https://github.com/Sakuraga200323/BitRPG/blob/master/README.md)の**各システムの解説>魔法システム**"))
                    magic_type_em.add_field(name="1:Wolf",value="`火力特化の魔法領域です。攻撃がメインの魔法を習得し、最終的には千人力の火力を出します。`")
                    magic_type_em.add_field(name="2:Armadillo",value="`防御特化の魔法領域です。序盤から高い生存能力を持ち、最終的にはほぼ不死身になります。`")
                    magic_type_em.add_field(name="3:Orca",value="`テクニカル性特化の魔法領域です。バフメインの魔法を習得し、条件次第ではWolfにもArmadilloにも成りうる性能を誇ります。`")
                    await m_ch.send(embed=magic_type_em)
                    try:
                        msg = await client.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        await m_ch.send(f"時間切れです。もう一度`^^start`でやり直して下さい。")
                        continue
                    else:
                        respons = int(msg.content)
                        if not respons in (1,2,3):
                            await m_ch.send(f"【警告】1,2,3で答えて下さい。")
                            continue
                        select_magic_type = "Wolf" if respons == 1 else "Armadillo" if respons == 2 else "Orca" 
                        await m_ch.send(f"『{select_magic_type}』で宜しいですか？\nyes -> y\nno -> n")
                        try:
                            msg = await client.wait_for("message", timeout=10, check=check2)
                        except asyncio.TimeoutError:
                            await m_ch.send(f"時間切れです。もう一度`^^start`でやり直して下さい。")
                            continue
                        else:
                            if msg.content in ("y","Y"):
                                await m_ch.send(f"『{select_magic_type}』で登録します。")
                                magic_type_flag = True
                            elif msg.content in ("n","N"):
                                await m_ch.send(f"魔法領域の選択画面に戻ります。")
                if not magic_type_flag == True:
                    return
                await m_ch.send(embed=embed)
                jsonb_items = "'冒険者カード', 1, 'HP回復薬', 10, 'MP回復薬', 10, 'ドーピング薬', 1, '魔石', 1"
                cmd = (
                    f"INSERT INTO player_tb VALUES ("
                    +f"{m_author.id},1,0,0,10,0,0,0,{respons},0,0,jsonb_build_object({jsonb_items}),0"
                    +");"
                )
                print(f"NewPlayer：{m_author}({m_author.id}),{select_magic_type}")
                try:
                    pg.execute(cmd)
                except Exception as e:
                    await m_ch.send('type:' + str(type(e))
                    + '\nargs:' + str(e.args)
                    + '\ne自身:' + str(e))
                else:
                    embed = discord.Embed(
                        description=f"{name}は`冒険者カード×1`を獲得した。",
                        color=discord.Color.green())
                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/719855399733428244/740870252945997925/3ff89628eced0385.gif")
                    await m_ch.send(content = "冒険者登録が完了しました。" , embed=embed) 

                P_list = pg.fetch(f"select * from player_tb where id = {m_author.id};")[0]
                await status.send_bord(client, m_author, m_ch)
                embed = discord.Embed(title="ステータスの見方",description="基本的な使用方法を説明します")
                embed.add_field(name = f"Player", value = f"貴方の名前", inline = False)
                embed.add_field(name = f"Sex", value = f"貴方の性別", inline = False)
                embed.add_field(name = f"Lv", value = f"*現在のLv* / *Lv上限(魔石を250消費で解放)*")
                embed.add_field(name = f"HP", value = f"*現在のHP / 最高HP*")
                embed.add_field(name = f"MP", value = f"*現在のMP / 最高MP*")
                embed.add_field(name = f"STR", value = f"*攻撃力。強化による補正済みの値*\n`[強化量]`")
                embed.add_field(name = f"DEF", value = f"*防御力。同様*\n`[強化量]`")
                embed.add_field(name = f"AGI", value = f"*素早さ。同様*\n`[強化量]`")
                embed.add_field(name = f"STP", value = f"*使用可能なPoint10LvUP毎に50獲得*")
                embed.add_field(name = f"EXP", value = f"*獲得した総EXP*\n`[次のレベルまでの必要EXP]`")
                await m_ch.send(embed=embed)


        finally:
            cmd_lock[m_ch.id] = False


    if not m_author.bot:
        if m_ctt == '><report':
            embed = discord.Embed(
                title = '<Safe> -YUI- will help you!!',
                description = (
                    'こんにちは、開発者代理の**天乃 結**です!'
                    +'\nレポート確認開始! 今から5分間待つから、その間にレポートをできるだけ詳しく書いて送信してね。'
                    +'\n最初のメッセージしか送信しないから注意してね。ちなみに画像も一緒に送信できるよd(˙꒳​˙* )'))
            # embed.set_footer(text='待機中…')
            await m_ch.send(embed=embed)
            def check(m):
                if m.author.id != m_author.id:
                    return 0
                if m.channel.id != m_ch.id:
                    return 0
                return 1
            try:
                re_m = await client.wait_for('message', timeout=60, check=check)
            except asyncio.TimeoutError:
                await m_ch.send('これ以上待てないよォ…\n5分以内で終わらないくらい長い時は、先にまとめてかららコピペして送信するといいよ!')
            else:
                ans = re_m.content
                atch = None
                if re_m.attachments:
                    atch = re_m.attachments
                re_em = discord.Embed(description=ans)
                re_em.set_author(name=m_author)
                await client.get_channel(761516423959805972).send(embed=re_em, file=atch)
                await m_ch.send('レポートありがとう!無事届いたよ!')


        if m_ctt == '><fix':
            embed = discord.Embed(
                title = '<Safe> -YUI- will help you!!',
                description = (
                    'こんにちは、開発者代理の**天乃 結**です!'
                    +'\n私が来たからにはもう大丈夫!'
                    +'\n大体のバグを強制的に治しちゃうよ!'
                    +'\n診断していくから`y`か`n`で答えてね!'))
            await m_ch.send(embed=embed)
            def check(m):
                if m.author.id != m_author.id:
                    return 0
                if m.channel.id != m_ch.id:
                    return 0
                if not m.content in ('y','n'):
                    return 0
                return 1
            if m_ch.id in cmd_lock:
                em = discord.Embed(description='もしかしてコマンド処理が終わらないんじゃない?\n`y/n`')
                await m_ch.send(embed=em)
                try:
                    re_m = await client.wait_for('message', timeout=60, check=check)
                except asyncio.TimeoutError:
                    await m_ch.send('答えないんなら次行くね?')
                else:
                    ans = re_m.content
                    if ans == 'y':
                        cmd_lock[m_ch.id] = False
            """
            if m_author.id in cbt_user:
                em = discord.Embed(description='もしかしてコマンド処理が終わらないんじゃない?\n`y/n`')
                await m_ch.send(em=em)
                try:
                    re_m = await client.wait_for('message', timeout=60, check=check)
                except asyncio.TimeoutError:
                    await m_ch.send('答えないんなら次行くね?')
                else:
                    ans = re_m.content
                    if ans == 'y':
                        cmd_lock[m_ch.id] = False
            """
            embed = discord.Embed(
                description='これで全部かな?\nお待たせしてごめんね、修理完了したよ!\n今後ともBitRPGをよろしく!!')
            await m_ch.send(embed=embed)

            
            
            

        if m_ctt.startswith("--"):
            if not m_author.id in clr_lv4 and not m_author.id in clr_lv5 :
                await m_ch.send("**貴方のクリアランスはLv4未満です。プロトコル[SimpleSystemCall]の実行にはLv4以上のクリアランスが必要です。**")
                return
            if m_ctt == "--test anti_macro":
                try:
                    check = random.random() >= 0.0
                finally:
                    if check:
                        P_list = pg.fetch(f"select * from player_tb where id = {m_author.id};")
                        if not m_author.id in doubt_count:
                            doubt_count[m_author.id] = 0
                        check_flag = True
                        result = False
                        while check_flag == True:
                            flag = await m_ch.send("デデドン！！")
                            await asyncio.sleep(1)
                            check_id = flag.id
                            macro_checking.append(m_author.id)
                            img, num = await anti_macro.get_img(client)
                            cv2.imwrite('anti_macro/num_img/temp.png', img)
                            check_em = discord.Embed(
                                title = "マクロ検知ぃいい！！(迫真)",
                                description=f'{m_author.mention}さんのマクロチェックです。\n以下の画像に書かれている数字を20秒以内に**半角**で送信してください。\n※`CheckID『{check_id}』`')
                            check_em.set_image(url="attachment://temp.png")
                            await m_ch.send(embed=check_em,file=discord.File(fp="anti_macro/num_img/temp.png"))
                            def check(m):
                                if not m.author.id == m_author.id or m.channel.id != m_ch.id:
                                    return 0
                                if not m.content in ['0','1','2','3','4','5','6','7','8','9']:
                                    return 0
                                return 1
                            try:
                                answer = await client.wait_for('message', timeout=20, check=check)
                            except asyncio.TimeoutError:
                                doubt_count[m_author.id] += 1
                                temp = None
                                await m_ch.send(f'無回答!!　不正カウント+1(現在{doubt_count[m_author.id]})')
                                result = False
                            else:
                                temp = answer.content
                                if int(answer.content) == int(num):
                                    await m_ch.send(f'正解!! 報酬として現レベル×10の経験値を配布しました。')
                                    if not P_list == []:
                                        pg.execute(f'update player_tb set now_exp = now_exp + (lv*10) where id = {m_author.id};')
                                    check_flag = False
                                    result = True
                                elif str(num) != str(answer.content):
                                    doubt_count[m_author.id] += 1
                                    await m_ch.send(f'不正解!! 不正カウント+1(現在{doubt_count[m_author.id]})')
                                    result = False
                            print(f"MacroCheck：({m_author.id}) TrueAnswer[{num}], UsersAnswer[{temp}]")
                            if doubt_count[m_author.id] >= 5:
                                check_flag = False
                                doubt_count[m_author.id] = 0
                                await m_ch.send(f'不正カウントが規定量に達しました。貴方のプレイヤーデータを即座に終了します。')
                                pg.execute(f"delete from player_tb where id = {m_author.id};")
                                await m_ch.send(f"「この画像は誰が見てもわからんやろ！？」等の異議申し立てがある場合は`^^claim {check_id}`と送信してください。運営人の検知画像肉眼チェックの上然るべき対応をさせていただきます。")
                            embed=discord.Embed(title="マクロ検知ログ", color=0x37ff00)
                            embed.add_field(name="CheckID", value=check_id, inline=False)
                            embed.add_field(name="Result", value=result, inline=False)
                            embed.add_field(name="UserData", value=P_list, inline=False)
                            embed.set_image(url="attachment://temp.png")
                            await client.get_channel(763299968353304626).send(embed=embed, file=discord.File(fp="anti_macro/num_img/temp.png"))
                        

                        
    if m_ctt == "SystemCall":
        m_ctt = m_ctt.split("SystemCall")[1].strip("\n")
        await m_ch.send("** 【警告】プロトコル[SystemCall]の実行にはLv4以上のクリアランスが必要です。\nクリアランスLv4未満のユーザーの不正接続を確認次第、即座に対象のデータを終了します。**")
        if not m_author.id in clr_lv4 and not m_author.id in clr_lv5 :
            await m_ch.send("**貴方のクリアランスはLv4未満です。プロトコル[SystemCall]の実行にはLv4以上のクリアランスが必要です。**")
            return
        else:
            if m_author.id in clr_lv4:
                c_lv = 4
            elif m_author.id in clr_lv5:
                c_lv = 5
            await m_ch.send(f"**Lv{c_lv}クリアランスを認証。プロトコル[SystemCall]を開始、命令文を待機中です。**")
            await m_ch.send("\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/")
            def check(m):
                if m.author.id != m_author.id:
                    return 0
                if m.channel.id != m_ch.id:
                    return 0
                return 1
            try:
                remsg = await client.wait_for("message", timeout=40, check=check)
            except asyncio.TimeoutError:
                await m_ch.send("\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/")
                await m_ch.send("プロトコル[SystemCall]を終了します。")
            else:
                ctt = remsg.content
                try:
                    if ctt.startswith("active guild "):
                        cmd = ctt.split("active guild ")[1]
                        cmd_list = [
                            "announce",
                            "delete",
                            "create",
                            "update"
                        ]
                        if not cmd.split(" ")[0] in cmd_list:
                            await m_ch.send(f"`CommandError:bitrpg has no cmd to {cmd.split(' ')[0]}`")
                            return
                        if cmd.split(" ")[0] == "announce":
                            ctt = cmd.split("announce ")[1]
                            embed = discord.Embed(
                                title="Announcement!!",
                                description="<@&719176372773453835>\n" + ctt
                            )
                            await client.get_channel(726655141599510648).send(embed=embed)

                    if ctt.startswith("psql "):
                        cmd = ctt.split("psql ")[1]
                        await m_ch.send(f"`::DATABASE=> {cmd}`")
                        result = None
                        if "select" in cmd:
                            result = pg.fetch(cmd)
                            result = f"{result}"
                        else:
                            try:
                                pg.execute(cmd)
                            except Exception as error:
                                result = f"{error}"
                            else:
                                result = "Completed!"
                        if len(result) > 2000:
                            result = split_n(result, 2000)
                            for i in result:
                                await m_ch.send(f"```py\n{i}```")
                        else:
                            await m_ch.send(f"```py\n{result}```")

                    if ctt == ("active bot exit"):
                        await m_ch.send("`Exit!`")
                        sys.exit(0)
                finally:
                    await m_ch.send("\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/")
                    await m_ch.send("**すべての処理完了。プロトコル[SystemCall]を終了します。**")

                    
        
'''
update テーブル名 set 列名 = 値, 列名 = 値, ...
where 列名 = 値;
select 列名 from テーブル名
where 列名 = 値;
'''


client.run(token)
