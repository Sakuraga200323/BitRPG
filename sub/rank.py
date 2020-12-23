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

from sub import box, mob_data

JST = timezone(timedelta(hours=+9), 'JST')

pg = None

client = None

def split_list(l, n):
    if len(l) <= n:
        return l
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]


def mob_ranking_embeds(user, ch):
    guilds_id = []
    temp = pg.fetch("select id, lv from mob_tb order by lv desc;")
    mobs_data = tuple([ (i["id"],i["lv"]) for i in temp ])
    mobs_data2 = tuple([ i["id"] for i in temp ])
    mobs_result = []
    for data in mobs_data:
        if len(mobs_result) >= 100:
            break
        id = data[0]
        lv = data[1]
        channel = client.get_channel(id)
        if not channel:
            continue
        guild_id = channel.guild.id
        if not guild_id in guilds_id:
            mobs_result.append((id,lv))
            guilds_id.append(guild_id)
    split_mobs_result = tuple(split_list(mobs_result,10))
    embeds = []
    ranking_em_title = "Channel Ranking Bord"
    for page_num,data1 in zip(range(1,11),split_mobs_result):
        ranking_em_text = ""
        for mob_num,data2 in zip(range((page_num*10-9),(page_num*10+1)),data1):
            channel = client.get_channel(data2[0])
            if not channel: ch_name = "チャンネルデータ破損"
            else: ch_name = channel.name
            ranking_em_text += f"{mob_num:0>3}: {ch_name} (Lv.{data[1]})\n"
        ranking_em_text += f"・・・\n{mobs_data2.index(ch.id):0>3}: {ch.name} (Lv.{box.mobs[ch.id].lv()})\n"
        embed = discord.Embed(title=ranking_em_title,description=f"```css\n{ranking_em_text}```")
        embed.set_footer(text=f"Page.{page_num}｜{(page_num*10-9)}-{(page_num*10+1)}")
        embeds.append(embed)
    return tuple(embeds)



def player_ranking_embeds(user, ch):
    temp = pg.fetch("select id, lv from player_tb order by lv desc;")
    players_data = tuple([ (i["id"],i["lv"]) for i in temp ])
    players_data2 = tuple([ i["id"] for i in temp ])
    players_result = players_data
    split_players_result = tuple(split_list(players_result,10))
    embeds = []
    ranking_em_title = "Player Ranking Bord"
    for page_num,data1 in zip(range(1,11),split_players_result):
        ranking_em_text = ""
        for player_num,data2 in zip(range((page_num*10-9),(page_num*10+1)),data1):
            p = client.get_user(data2[0])
            if not p: player_name = "匿名"
            else: player_name = p
            ranking_em_text += f"{player_num:0>3}: {player_name} (Lv.{data2[1]})\n"
        ranking_em_text += f"・・・\n{players_data2.index(user.id)+1:" ">3}: {p} (Lv.{box.players[user.id].lv()})\n"
        embed = discord.Embed(title=ranking_em_title,description=f"```css\n{ranking_em_text}```")
        embed.set_footer(text=f"Page.{page_num}｜{(page_num*10-9)}-{(page_num*10+1)}")
        embeds.append(embed)
    return tuple(embeds)



async def open_ranking(user,ch):
    player = box.players[user.id]
    ranking_em = discord.Embed(
        title="Ranking",
        description=("`表示するランキングの番号を半角英数字で送信してください。`"
            + "\n`1.`Player Lv"
            + "\n`2.`Channel Lv"
    ))
    ranking_em_msg = await ch.send(embed=ranking_em)
    def check(m):
        if not user.id == m.author.id:
            return 0
        if not m.content in [ str(i) for i in range(0,11)]:
            return 0
        return 1
    def check2(m):
        if not user.id == m.author.id:
            return 0
        if not m.content in ("y","Y","n","N"):
            return 0
        return 1
    try:
        msg = await client.wait_for("message", timeout=60, check=check)
    except asyncio.TimeoutError:
        em = discord.Embed(description=f"指定がないので処理終了しました")
        await ch.send(embed=em)
    else:
        respons = int(msg.content)
        if respons == 1:
            ranking_flag = True
            embeds = player_ranking_embeds(user,ch)
            await ranking_em_msg.edit(embed=embeds[0])
            em = discord.Embed(description=f"番号を送信するとページが切り替わります 0と送信すると処理が停止してメッセージが残ります")
            await ch.send(embed=em)
            while ranking_flag:
                try:
                    msg2 = await client.wait_for("message", timeout=60, check=check)
                except asyncio.TimeoutError:
                    await ranking_em_mdg.delete()
                    em = discord.Embed(description=f"指定がないのでメッセージを消去しました")
                    await ch.send(embed=em)
                    ranking_flag = False
                else:
                    page_num = int(msg2.content)
                    if 0 < page_num <= len(embeds):
                        await ranking_em_msg.edit(embed=embeds[page_num-1])
                    if page_num == 0:
                        ranking_flag = False
                await msg2.delete()

                
        elif respons == 2:
            pass
