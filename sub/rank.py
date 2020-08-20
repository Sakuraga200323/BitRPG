  
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

admin_list = [
    715192735128092713,
    710207828303937626,
    548058577848238080,
]


loop = asyncio.get_event_loop()


getmagic_list = [
    "001|Heal",
    "002|FireBall",
    "003|StrRein",
    "004|DefRein",
    "005|AgiRein",
    "006|LifeConversion"
]


def split_list(l, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return:
    """
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]


class RankClass:
    def __init__(self, client):
        self.client = client
        self.loop = asyncio.get_event_loop()
        self.pg = Postgres(dsn)




    def channel(self, user, ch):
        rank_list = []
        id_list = []
        result = self.pg.fetch("select id, lv from mob_tb order by lv desc;")
        for data in result:
            id = data["id"]
            lv = data["lv"]
            channel = self.client.get_channel(id)
            if channel:
                prace = channel.guild.id
                if not prace in id_list:
                    rank_list.append((prace, lv))
                    id_list.append(prace)
                    print(prace, channel.guild.name)
            else:
                self.pg.execute(f'delete from mob_tb where id = {id};')
                continueao = list(dict.fromkeys(ao))
        d = {}
        for item in rank_list:
           if not item[0] in d:
               d[item[0]] = item[1]
               continue
           d[item[0]] = max(item[1], d[item[0]])
        rank_list = list(d.items())
        rank_list = rank_list[:20]
        junni = 0
        page = 0
        text = ""
        page += 1
        for data_set in rank_list:
            junni += 1
            g = self.client.get_guild(data_set[0])
            if g:
                g_name = g.name
            else:
                g_name = "名前データ破損"
            text += ( "\n" + f"[`{junni}位`]{g_name} (`Lv:{data_set[1]})`")
        em = discord.Embed(
            title = f"ChannelRankingBord(1~20)",
            description = text
        )
        loop.create_task(ch.send(embed=em)) 

        
