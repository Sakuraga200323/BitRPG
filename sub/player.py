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
        self.id = id
        self.pg = Postgres(dsn)
        self.client = client
        self.dtd = self.pg.fetchdict(f"select * from player_tb where id = {id};")[0]
        self.user = client.get_user(id)
        self.lv = self.dtd["lv"]
        self.max_lv = self.dtd["max_lv"]
        self.max_hp = self.now_hp = self.lv * 100 + 10
        self.max_mp = self.now_mp = self.lv * 10
        self.str = self.defe = self.agi = self.lv * 10 + 10
        self.str_p = self.dtd["str_p"]
        self.defe_p = self.dtd["def_p"]
        self.agi_p = self.dtd["agi_p"]
        self.now_stp = self.dtd["now_stp"]
        self.all_stp = self.str_p + self.defe_p + self.agi_p + self.now_stp
        self.all_exp = self.dtd["max_exp"]
        self.now_exp = self.dtd["now_exp"]
        self.kill_count = self.dtd["kill_count"]
        self.magic_class = self.dtd["magic_class"]
        self.magic_lv = self.dtd["magic_lv"]
        self.money = self.dtd["money"]
        if not id in box.players:
            box.players[id] = self
            print(f"{self.user}:[{self.dtd}]")

    def share_stp(self, target, point):
        self.now_stp -= point
        if target == "str":
            self.str_p += point
            self.STR += point
            temp = self.str_p
        if target == "def":
            self.defe_p += point
            self.DEFE += point
            temp = self.defe_p
        if target == "agi":
            self.agi_p += point
            seld.AGI += point
            temp = self.agi_p
        self.pg.execute(f"UPDATE player_tb SET now_stp={self.now_stp},{target}_p={temp} WHERE id={self.id};")
        return temp
        self.dtd = self.pg.fetchdict(f"select * from player_tb where id = {id};")[0]

    def get_exp(self, exp):
        self.now_exp += exp
        self.all_exp += exp
        lvup_count = 0
        while self.now_exp >= self.lv:
            if self.max_lv >= self.now_lv:
                self.now_exp -= self.lv
                self.lv += 1
                lvup_count += 1
        if lvup_count > 0:
            self.now_stp += 10 * lvup_count
            self.str = self.defe = self.agi = self.lv * 10 + 10
            self.max_hp = self.now_hp = self.lv * 100 + 10
            self.max_mp = self.now_mp = self.lv
            psql = f"update player_tb set lv={self.lv},now_exp={self.now_exp},max_exp={self.max_exp},;"
        self.pg.execute(psql)
        return lvup_count
        self.dtd = self.pg.fetchdict(f"select * from player_tb where id = {id};")[0]

    def cut_hp(self, dmg):
        self.now_hp -= dmg if dmg <= self.now_hp else self.now_hp
        return self.now_hp

    def STR(self):
        return self.str + self.dtd["str_p"]
    def DEFE(self):
        return self.defe + self.dtd["def_p"]
    def AGI(self):
        return self.agi + self.dtd["agi_p"]
            

