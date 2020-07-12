import asyncio
from datetime import datetime, timedelta, timezone
import discord
import pymongo
from pymongo import MongoClient
import psutil
import random
import re
import traceback

JST = timezone(timedelta(hours=+9), 'JST')
client = discord.Client()
token = os.environ['TOKEN']
mongo_url = "mongodb+srv://sakuraga200323:tsukumo0308@cluster0.vfmoe.mongodb.net/bitrpg-database?retryWrites=true&w=majority"

cclist = []

@client.event
async def on_ready():
    pass



@client.event
async def on_message(message):
    global cclist
    m_ch = message.channel
    m_ctt = message.content
    m_author = message.author
    m_guild = message.guild


    if m_ctt.startswith("^^"):
        pattern = r'^\^\^(.+)'
        result = re.search(pattern, m_ctt)
        if not result:
            return
        msg_ctt = resutl.group(1)
        if m_ch.id in cclist:
            await m_ch.send("処理中")
            return
        cclist.append(m_ch.id)

        # データの追加
        if collection.count_documents({}) == 0:
            player_info = {
                "_id": m_author.id,
                "max_hp":10, "now_hp":10,
                "max_mp":1, "now_mp":1,
                "all_exp":0, "now_exp":0,
                "now_stp":0,
                "str":10, "def":10, "agi":10,
                "str_p":0, "def_p":0, "agi_p":0,
                "mp_p":0, "hp_p":0,
                "magics":{}, "items":{}}
            collection.insert_one(player_info)
    

        #=====Command-start=====#

        if m_ctt.split()[0].startswith('at'):
            m_ctt = m_ctt.split()[0]
            pattern = ['atk', 'attack','attacking']
            if not m_ctt in cmd_list:
                return
            import sub.battle
            sub.battle(m_author, m_ch, m_ctt)
                

        #=====Command-e n d=====#


        if m_ch.id in cclist:
            cclist.remove(m_ch.id)

            
client.run(token)
