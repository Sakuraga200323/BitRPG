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
        self.user = client.get_user(id)
        self.pg = Postgres(dsn)
        self.client = client
        self.dtd = self.pg.fetchdict(f"select * from player_tb where id = {self.user.id};")[0]
        self.max_hp = self.now_hp = self.lv() * 100 + 10
        self.max_mp = self.now_mp = self.lv() * 10
        if not id in box.players:
            box.players[id] = self
            print(f"データ獲得：{self.user}")

    def get_data(self, target):
        return self.pg.fetchdict(f"select {target} from player_tb where id = {self.user.id};")[0][target]
    def plus_data(self, target, plus):
        if target == 'id':
            return None
        else:
            if plus < 0:
                self.pg.execute(f'update player_tb set {target}={target}{plus};')
            else:
                self.pg.execute(f'update player_tb set {target}={target}+{plus};')
            return self.get_data(target)

    def lv(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('lv', plus)
        else:
            result = self.get_data('lv')
        return result
    def max_lv(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('max_lv', plus)
        else:
            result = self.get_data('lv')
        return result

    def str(self):
        result = self.get_data('lv') * 10 + 10
        return result
    def str_p(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('str_p', plus)
        else:
            result = self.get_data('str_p')

    def defe(self):
        result = self.get_data('lv') * 10 + 10
        return result
    def defe_p(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('sdefe_p', plus)
        else:
            result = self.get_data('defe_p')

    def agi(self):
        result = self.get_data('lv') * 10 + 10
        return result
    def agi_p(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('agi_p', plus)
        else:
            result = self.get_data('agi_p')

    def now_stp(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('now_stp', plus)
        else:
            result = self.get_data('now_stp')
    def STP(self, plus=None):
        result = self.str_p + self.defe_p + self.agi_p + self.now_stp

    def now_exp(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('now_exp', plus)
        else:
            result = self.get_data('now_exp')
    def EXP(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('all_stp', plus)
        else:
            result = self.get_data('all_stp')

    def kill_count(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('kill_count', plus)
        else:
            result = self.get_data('kill_count')

    def magic_class(self):
        result = self.get_data('magic_class')
    def magic_lv(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('magic_lv', plus)
        else:
            result = self.get_data('magic_lv')

    def money(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('money', plus)
        else:
            result = self.get_data('money')

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
        self.EXP(exp)
        lvup_count = 0
        now_exp = self.now_exp() + exp
        lv = self.lv()
        while now_exp >= lv:
            if self.max_lv >= lv:
                lv += 1
                lvup_count += 1
        if lvup_count > 0:
            self.now_stp(10 * lvup_count)
            self.max_hp = self.now_hp = self.lv * 100 + 10
            self.max_mp = self.now_mp = self.lv

    def cut_hp(self, dmg):
        self.now_hp -= dmg if dmg <= self.now_hp else self.now_hp
        return self.now_hp

