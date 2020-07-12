import asyncio
from datetime import datetime, timedelta, timezone
import discord
import pymongo
from pymongo import MongoClient
import random
import re
import traceback

JST = timezone(timedelta(hours=+9), 'JST')
client = discord.Client()
mongo_url = "mongodb+srv://sakuraga200323:tsukumo0308@cluster0.vfmoe.mongodb.net/bitrpg-database?retryWrites=true&w=majority"
cluster = MongoClient(mongo_url)
db = cluster["BitRPG-DataBse"]
collection = db["BitRPG-Player"]

import sub-library.box

def proc_def(player, ch, m_ctt):
    cmd_players = sub_library.box.cmd_players
    cbt_players = sub_library.box.cbt_players
    cbt_channels = sub_library.box.cbt_channels
    if player.id in cmd_players:
        await ch.send("処理中です。")
        return
    if p_data["now_hp"] <= 0:
        await ch.send(f"{player.mention}は既に死亡しています。\n戦闘からの離脱は`^^reset`です。")
        return
    if not ch.id in cbt_channels:
        cbt_channels[ch.id] = [player.id]
    if not player.id in cbt_channels[ch.id]:
        cbt_channels[ch.id].append(player.id)
    p_data = collection.find({'_id': player.id})
    m_data = collection.find({'_id': ch.id})
    import sub.calc
    dmg1 = sub.clac.dmg_def(p_data['str'], m_data['def'])
    dmg2 = sub.clac.dmg_def(m_data['str'], p_data['def'])
    text1 = text2 = text3 = ""
    msg_text = f"\\\ini{text1}\\\ini\\\{text2}\\\"
    bar = "■"
    result = False
    def make_bar(a,b):
        c = round(a/b*20)
        return f"[{(bar * max(0, c)): <20}]"
    if p_data['agi'] >= m_data['agi']:
        mob_hp = m_data['now_hp'] - dmg1
        text1 = f"{player}の攻撃！{dmg1}ダメージ！\n敵のHP:{mob_hp}/{m_data['max_hp']}\n"
        mob_hpbar = make_bar(mob_hp, m_data["max_hp"])
        text1 += mob_hpbar
        if mob_hp <= 0:
            text2 = "敵は既に死んでいる！" 
            result = True
        else:
            player_hp = p_data['now_hp'] - dmg2
            text2 = f"敵の攻撃！{dmg2}ダメージ！\n{player}のHP:{player_hp}/{p_data['max_hp']}\n"
            player_hpbar = make_bar(player_hp, p_data["max_hp"])
            text2 += player_hpbar
            if player_hp <= 0:
                result_msg += f"\n\\\ini\n{player}はやられてしまった！\\\"
    else:
        player_hp = p_data["now_hp"] - dmg2
        text1 = f"敵の攻撃！{dmg2}ダメージ！\n{player}のHP:{player_hp}/{p_data['max_hp']}\n"
        player_hpbar = make_bar(player_hp, p_data['max_hp'])
        text1 += player_hpbar
        if player_hp <= 0:
            text2 = f"{player}はやられてしまっている！"
        else:
            mob_hp = m_data['now_hp'] - dmg1
            text2 = f"{player}の攻撃！{dmg1}ダメージ！\n敵のHP:{mob_hp}/{m_data['max_hp']}\n"
            mob_hpbar = make_bar(mob_hp, m_data["max_hp"])
            text2 += mob_hpbar
            if mob_hp <= 0:
                result = True
    if result == True:
        import sub.lvup
        sub.lvup(player, m_data["lv"])
        
