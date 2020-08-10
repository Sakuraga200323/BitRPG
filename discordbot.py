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
import random
import re
import traceback
import sub.box

JST = timezone(timedelta(hours=+9), 'JST')

dsn = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(dsn)
cur = conn.cursor()
token = os.environ.get('TOKEN')
client = discord.Client()

admin_list = [
    715192735128092713,
    710207828303937626,
    548058577848238080,
]


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=f"起動中…"))

    NOW = datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S")
    MEM = psutil.virtual_memory().percent

    LOG_CHANNELS = [i for i in client.get_all_channels() if i.name == "bit起動ログ"]
    desc = (f"\n+Bot\n{client.user}"
        + f"\n+BotID\n{client.user.id}"
        + f"\n+Prefix\n^^"
        + f"\n+UsingMemory\n{MEM}%")

    for ch in LOG_CHANNELS:
        try:
            embed = discord.Embed(
                title = "BitRPG起動ログ",
                description = f"```diff\n{desc}```")
            embed.timestamp = datetime.now(JST)
            await ch.send(embed = embed)
        except:
            print("Error")

    print(desc)

    loop.start()

    await client.change_presence(activity=discord.Game(name=f"^^help║Server：{len(client.guilds)}║Mem：{MEM} %"))


@tasks.loop(seconds=1)
async def loop():
    MEM = psutil.virtual_memory().percent
    await client.change_presence(activity=discord.Game(name=f"^^help║Server：{len(client.guilds)}║Mem：{MEM} %"))



@client.event
async def on_message(message):
    global cur, conn
    m_author = message.author
    m_ctt = message.content
    m_ch = message.channel
    
    
    if m_ctt.startswith("^^"):
        if m_ch.id in sub.box.cmd_ch:
            await m_ch.send("【警告】処理が終了するまで待機してください。")
            return
        sub.box.cmd_ch.append(m_ch.id)
        cur.execute('select id from player_tb;')
        id_list = cur.fetchone()
        id = m_author.id
        print(id, id_list)
        if not id_list or not id in id_list:
            flag = False
            while flag == False:
                await m_ch.send(
                    f"{m_author.mention}さんの冒険者登録を開始。"
                    "\n登録名を1分以内に送信してください。`next`と送信すると、ユーザー名がそのまま使用されます。\n`あとから設定し直すことが可能です。\n特殊文字非対応。`"
                )
                name_flag = False
                sex_flag = False
                def check(m):
                    if not m.author.id == id:
                        return 0
                    return 1
                while name_flag == False:
                    try:
                        msg = await client.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '・', m_author.name)
                        await m_ch.send(f"時間切れです。ユーザー名『{name}』をそのまま登録します。")
                    else:
                        name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '・', msg.content)
                        if name == "next":
                            name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '・', m_author.name)
                            await m_ch.send(f"ユーザー名『{name}』をそのまま登録します。")
                        else:
                            cur.execute('select name from player_tb;')
                            name_list = cur.fetchone()
                            if name in name_list:
                                await m_ch.send(f"『{name}』は既に使用されています。")
                                continue
                            await m_ch.send(f"『{name}』で登録します。")
                        name_flag = True
                            
                await m_ch.send("\n該当する性別の番号を20秒以内に送信してください。\n男性 -> 0\n女性 -> 1\n無記入 -> 2\n`半角全角は問いません。`")
                def check2(m):
                    if not m.author.id == id:
                        return 0
                    return 1
                while sex_flag == False:
                    try:
                        msg2 = await client.wait_for("message", timeout=20, check=check2)
                    except asyncio.TimeoutError:
                        sex = "無記入"
                        await m_ch.send(f"時間切れです。無記入として登録します。")
                    else:
                        sex = msg2.content
                        if not sex in ("0", "1", "１", "０", "2","２"):
                            await m_ch.send("0、1、2いずれかの番号を送信してください。")
                            continue
                        if sex in ("0", "０"):
                            sex = "男性"
                        if sex in ("1", "１"):
                            sex = "女性"
                        if sex in ("2", "２"):
                            sex = "無記入"
                        await m_ch.send(f"『{sex}』で登録します。")
                embed = discord.Embed(color = discord.Color.green())
                embed.add_field(name = "Name", value = name)
                embed.add_field(name = "Sex", value = sex)
                await m_ch.send(embed=embed)
                n = name
                s = sex
                i = '{"冒険者登録証明カード"}'
                cmd = (
                    'INSERT INTO player_tb (name,sex,id,lv,max_hp, now_hp,max_mp, now_mp,str, def, agi,stp,str_stp, def_stp, agi_stp,all_exp, now_exp,money, items) '
                    + f"VALUES ('{n}', '{s}', {id}, 1, 10 ,10, 1, 1, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, " + f"'{i}');")
                cur.execute(cmd)
                conn.commit()
                cur.close()
                conn.close()
                
                await m_ch.send("登録完了しました。")
                embed = discord.Embed(
                    description=f"{name}は`冒険者登録証明カード×1`を獲得した。",
                    color=discord.Color.green())
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/719855399733428244/740870252945997925/3ff89628eced0385.gif")
                await m_ch.send(embed=embed)
                flag = True
        if  m_ch.id in sub.box.cmd_ch:
            sub.box.cmd_ch.remove(m_ch.id)



    if m_ctt.startswith("SystemCall"):
        m_ctt = m_ctt.split("SystemCall")[1].strip("\n")
        await m_ch.send("** 【警告】プロトコル[SystemCall]の実行にはLv4以上のクリアランスが必要です。\nクリアランスLv4未満のユーザーの不正接続を確認次第、即座に対象のデータを終了します。**")
        if not m_author.id in admin_list:
            await m_ch.send("**貴方のクリアランスはLv1です。プロトコル[SystemCall]の実行にはLv4以上のクリアランスが必要です。**")
            return
        else:
            await m_ch.send("**Lv5クリアランスを認証。プロトコル[SystemCall]を実行します。**")
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        cur.execute('select id from player_tb;')
        if m_ctt == "^^player_tb":
            cur.execute('select * from player_tb;')
            await m_ch.send(cur.fetchone())
                
        await m_ch.send("**すべての処理完了。プロトコル[SystemCall]を終了します。**")
            
                
'''
update テーブル名 set 列名 = 値, 列名 = 値, ...
where 列名 = 値;

select 列名 from テーブル名
where 列名 = 値;

'''


client.run(token)
