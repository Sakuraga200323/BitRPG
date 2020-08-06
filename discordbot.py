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
    m_author = message.author
    m_ctt = message.content
    m_ch = message.channel
    
    
    if m_ctt.startswith("^^"):
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()
        cur.execute('select id from player_tb;')
        id_list = cur.fetchone()
        id = m_author.id
        print(id, id_list)
        if not id_list:
            await m_ch.send(
                f"{m_author.mention}さんの冒険者登録を開始。"
                "\n登録名を1分以内に送信してください。`next`と送信すると、ユーザー名がそのまま使用されます。\n`あとから設定し直すことが可能です。\n特殊文字非対応。`"
            )
            def check(m):
                if not m.author.id == id:
                    return 0
                return 1
            try:
                msg = await client.wait_for("message", timeout=60, check=check)
            except TimeoutError:
                name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '・', m_author.name)
                await m_ch.send(f"時間切れです。ユーザー名『{name}』をそのまま登録します。")
            else:
                name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '・', msg.content)
                if name == "next":
                    name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '・', m_author.name)
                    await m_ch.send(f"ユーザー名『{name}』をそのまま登録します。")
                else:
                    await m_ch.send(f"『{name}』で登録します。")
            await m_ch.send("\n該当する性別の番号を20秒以内に送信してください。\n男性 -> 0\n女性 -> 1\n無記入 -> 3\n`半角全角は問いません。`")
            def check2(m):
                if not m.author.id == id:
                    return 0
                return 1
            try:
                msg2 = await client.wait_for("message", timeout=20, check=check2)
                if not msg2.content in ("0", "1", "１", "０"):
                    await m_ch.send("0か1の番号を送信してください")
            except TimeoutError:
                sex = "無記入"
                await m_ch.send(f"時間切れです。無記入として登録します。")
            else:
                sex = msg2.content
                if sex in ("0", "０"):
                    sex = "男性"
                if sex in ("1", "１"):
                    sex = "女性"
                if sex in ("3", "３"):
                    sex = "無記入"
                await m_ch.send(f"『{sex}』で登録します。")
            embed = discord.Embed(color = discord.Color.green())
            embed.add_field(name = "Name", value = name)
            embed.add_field(name = "Sex", value = sex)
            await m_ch.send(embed=embed)
            n = name
            s = sex
            cmd = ('INSERT INTO player_tb (name,sex,id,lv,max_hp, now_hp,max_mp, now_mp,str, def, agi,stp,str_stp, def_stp, agi_stp,all_exp, now_exp,money, items) '
                   + f"VALUES ({n},{s},{id},1 ,10 , 10,1 ,1 ,10, 10, 10,0,0, 0, 0,0, 0,0, " + "'{\"冒険者登録証明カード\"}');")
            print(cmd)
            cur.execute(cmd)
            await m_ch.send("登録完了しました。")
            embed = discord.Embed(
                description=f"{name}は`険者登録証明カード×1`を獲得した。",
                color=discord.Color.green())
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/719855399733428244/740870252945997925/3ff89628eced0385.gif")
            await m_ch.send(embed=embed)
                
                
'''
update テーブル名 set 列名 = 値, 列名 = 値, ...
where 列名 = 値;

select 列名 from テーブル名
where 列名 = 値;

'''

client.run(token)
