  
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
import sub.box
import sub.calc

JST = timezone(timedelta(hours=+9), 'JST')

dsn = os.environ.get('DATABASE_URL')

class Postgres:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

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

standard_set = "name,sex,id,lv,max_hp,now_hp,max_mp,now_mp,str,def,agi,stp,str_stp, def_stp, agi_stp,all_exp,now_exp,money"
standard_mobset = "name,id,lv,max_hp,now_hp,str,def,agi,img_url"

token = os.environ.get('TOKEN')
client = discord.Client()

admin_list = [
    715192735128092713,
    710207828303937626,
    548058577848238080,
]




getmagic_list = [
    "001|Heal",
    "002|FireBall",
    "003|StrRein",
    "004|DefRein",
    "005|AgiRein",
    "006|LifeConversion"


]

loop = asyncio.get_event_loop()
pg = Postgres(dsn)


def split_list(l, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return:
    """
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]


def channel(ch):
    rank_list = []
    em_list = []
    result = pg.fetch("select id, lv from mob_tb order by lv desc;")[0:20]
    for id, lv in result:
        channel = client.get_channel(id)
        if channel:
            prace = channel.guild.name
        else:
            prace = "データ破損"
        rank_list.append((prace, lv))
    junni = 0
    rank_list = list(split_list(rank_list, 10))
    page = 0
    for i in rank_list:
        text = ""
        page += 1
        for data_set in i:
            junni + 1
            text += ( "\n" + f"[{junni}位]{i[0]} (Lv:{i[1]})")
        em = discord.Embed(
            title = f"PlayerRankBord(page.{page})",
            description = text
        )
        em_list.append(em)
    return em_list
           
