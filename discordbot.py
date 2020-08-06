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
cur.execute('select id from player_tb;')
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
    for i in cur:
        print(i)

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
    
    
    if m_ctt.startswith("^^"):
        id_list = cur.execute('select id from player_tb;')
        id = m_author.id
        print(id, id_list)
        if not id in id_list:
            cur.execute('''INSERT INTO player_tb (
                name,
                id,lv,
                max_hp, now_hp,
                max_mp, now_mp,
                str, def, agi,
                stp,
                str_stp, def_stp, agi_stp,
                all_exp, now_exp,
                money, items) VALUES (
                m_author.name,
                m_author.id, 1 ,
                10 , 10,
                1 ,1 ,
                10, 10, 10,
                0,
                0, 0, 0,
                0, 0,
                0, {"冒険の書1"});'''
            )


'''
update テーブル名 set 列名 = 値, 列名 = 値, ...
where 列名 = 値;

select 列名 from テーブル名
where 列名 = 値;


'''


client.run(token)
