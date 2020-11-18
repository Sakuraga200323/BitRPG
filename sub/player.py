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

from sub import box


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

    def update(self, tb_name, dtd, where = False):
        sql = f"UPDATE {tb_name} SET "
        for key, value in zip(dtd.keys(), dtd.items()):
            sql += f"{key} = {value}, "
        sql = sql.strip(", ")
        if not where == False:
            sql += " WHERE "
            for key, value in zip(where.keys(), where.items()):
                sql += f"{key} = {value}, "
            sql = sql.strip(", ")
        sql += ";"
        self.cur.execute(f"{sql}")

class Player:
    def __init__(self, client, id):
        self.pg = Postgres(dsn)
        self.client = client
        self.dtd = pg.fetchdict(f"select * from player_tb where id = {id};")[0]
        self.user = client.get_user(id)
        self.lv = self.dtd["lv"]
        self.max_hp = self.now_hp = self.lv * 110
        self.max_mp = self.now_mp = self.lv * 10
        self.str = self.defe = self.agi = self.lv * 10 + 10
        self.STR = self.str + self.dtd["str_p"]
        self.DEFE = self.defe + self.dtd["def_p"]
        self.AGI = self.agi + self.dtd["agi_p"]
        self.str_p = self.dtd["str_p"]
        self.defe_p = self.dtd["def_p"]
        self.agi_p = self.dtd["agi_p"]
        self.now_stp = self.dtd["now_stp"]
        self.all_stp = self.str_p + self.defe_p + self.agi_p + self.now_stp
        self.max_exp = self.dtd["max_exp"]
        self.now_exp = self.dtd["now_exp"]
        self.kill_count = self.dtd["kill_count"]
        self.magic_class = self.dtd["magic_class"]
        self.magic_lv = self.dtd["magic_lv"]
        self.money = self.dtd["money"]
        if not id in box.players:
            box.players[id] = self
        print(f"{self.user}:[{self.dtd}]")

