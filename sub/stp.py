
# coding: utf-8
# Your code here!
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

from sub import box, calc, player

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


async def divid(client, user, ch, result):
    pg = Postgres(dsn)
    p_data = box.players[user.id]
    target = result.group(1)
    point = int(result.group(2))
    if not target in ("str","def","agi"):
        await ch.send(f"{target}は強化項目の一覧にありません。`str`,`def`,`agi` の中から選んでください。")
        return
    if p_data.now_stp < point:
        await ch.send(f"{p_data.user.mention}の所持ポイントを{point - p_data.now_stp}超過しています。{p_data.now_stp}以下にしてください。")
        return
    result = p_data.share_stp(target, point)
    print("Point:" ,user.id)
    await ch.send(f"{p_data.user.mention}の{target}を{point}強化。強化量が+{result}になりました。")
