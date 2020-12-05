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

from sub import box, mob_data

JST = timezone(timedelta(hours=+9), 'JST')

dsn = os.environ.get('DATABASE_URL')

class Postgres:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self.battle_ch_id = None

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

#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖#

class Player:
    def __init__(self, client, id):
        self.user = client.get_user(id)
        if not self.user:
            print(f"データ挿入失敗: {id}のuserがNone。")
        self.pg = Postgres(dsn)
        self.client = client
        self.dtd = self.pg.fetchdict(f"select * from player_tb where id = {self.user.id};")[0]
        self.max_hp = self.now_hp = self.lv() * 100 + 10
        self.max_mp = self.now_mp = self.lv() * 10
        if not id in box.players:
            box.players[id] = self
            print(f"Playerデータ挿入： {self.user}")
        self.battle_ch = None

    def print_alldata():
        print(self.id, self.lv(), self.max_lv(). self)

    def get_data(self, target):
        return self.pg.fetchdict(f"select {target} from player_tb where id = {self.user.id};")[0][target]
    def plus(self, target, plus):
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
            self.max_hp = self.now_hp = self.lv() * 100 + 10
            self.max_mp = self.now_mp = self.lv() * 10
        else:
            result = self.get_data('lv')
        return result
    def max_lv(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('max_lv', plus)
        else:
            result = self.get_data('max_lv')
        return result

    def str(self):
        result = self.lv() * 10 + 10
        return result
    def str_p(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('str_p', plus)
        else:
            result = self.get_data('str_p')
        return result
    def STR(self):
        return self.str() + self.str_p()

    def defe(self):
        result = self.lv() * 10 + 10
        return result
    def defe_p(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('def_p', plus)
        else:
            result = self.get_data('def_p')
        return result
    def DEFE(self):
        return self.defe() + self.defe_p()

    def agi(self):
        result = self.lv() * 10 + 10
        return result
    def agi_p(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('agi_p', plus)
        else:
            result = self.get_data('agi_p')
        return result
    def AGI(self):
        return self.agi() + self.agi_p()

    def now_stp(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('now_stp', plus)
        else:
            result = self.get_data('now_stp')
        return result
    def STP(self, plus=None):
        result = self.str_p() + self.defe_p() + self.agi_p() + self.now_stp()
        return result

    def now_exp(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('now_exp', plus)
        else:
            result = self.get_data('now_exp')
        return result
    def EXP(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('max_exp', plus) + self.now_exp(plus)
        else:
            result = self.get_data('max_exp') + self.self.now_exp(plus)
        return result

    def kill_count(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('kill_count', plus)
        else:
            result = self.get_data('kill_count')
        return result

    def magic_class(self):
        result = self.get_data('magic_class')
        return result
    def magic_lv(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('magic_lv', plus)
        else:
            result = self.get_data('magic_lv')
        return result

    def money(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('money', plus)
        else:
            result = self.get_data('money')
        return result

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
        now_exp = self.now_exp()
        lv = self.lv()
        while now_exp >= lv:
            if self.max_lv() >= lv:
                lvup_count += 1
        if lvup_count > 0:
            self.now_stp(10 * lvup_count)
            self.max_hp = self.now_hp = self.lv() * 100 + 10
            self.max_mp = self.now_mp = self.lv()
        return exo, lvup_count

    def cut_hp(self, dmg):
        self.now_hp -= dmg if dmg <= self.now_hp else self.now_hp
        return self.now_hp
    
    def battle_start(self, id):
        if self.battle_ch and id != self.battle_ch:
            print(self.user.name,"is already battling in",self.battle_ch)
            return False
        self.battle_ch  = id
        return True
    def battle_end(self):
        self.battle_ch = None
        self.now_hp = self.max_hp
        self.now_mp = self.max_mp



#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖#



class Mob:
    # id,lv
    def __init__(self, client, id):
        if client.get_channel(id):
            self.mob = client.get_channel(id)
            self.pg = Postgres(dsn)
            self.client = client
            self.battle_players = []
            try:
                self.pg.execute(f"insert into mob_tb (id,lv) values ({id},1);")
            except psycopg2.errors.UniqueViolation:
                pass
            else:
                print(f"新規Mobデータを挿入: {id}")
            self.dtd = self.pg.fetchdict(f"select lv from mob_tb where id = {id};")[0]
            self.max_hp = self.now_hp = self.dtd["lv"] * 110 + 10
            set = mob_data.select(self.dtd["lv"])
            self.type, self.name, self.img_url = set.values()
            if not id in box.mobs:
                box.mobs[id] = self

    def get_data(self, target):
        return self.pg.fetchdict(f"select {target} from mob_tb where id = {self.mob.id};")[0][target]
    def plus(self, target, plus):
        if target == 'id':
            return None
        else:
            if plus < 0:
                self.pg.execute(f'update mob_tb set {target}={target}{plus};')
            else:
                self.pg.execute(f'update mob_tb set {target}={target}+{plus};')
            return self.get_data(target)

    def lv(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('lv', plus)
            self.max_hp = self.now_hp = self.lv() * 100 + 10
        else:
            result = self.get_data('lv')
        return result

    def str(self):
        result = self.lv() * 10 + 10
        return result

    def defe(self):
        result = self.lv() * 10 + 10
        return result

    def agi(self):
        result = self.lv() * 10 + 10
        return result

    def exp(self):
        if self.lv() % 1000 == 0:
            exp = self.lv()*100
            money = random.randint(9000, 11000)
        elif self.lv() % 100 == 0:
            exp = self.lv()*5
            money = random.randint(4000, 6000)
        elif self.lv() % 10 == 0:
            exp = self.lv() * 1.5
            money = random.randint(100, 200)
        else:
            exp = self.lv()
            money = random.randint(1, 10)
        exp *= 0.45
        exp = round(exp) + 1
        if self.type == "UltraRare":
            exp *= 100
            money = 100000
        return exp, money

    def cut_hp(self, dmg):
        self.now_hp -= dmg if dmg <= self.now_hp else self.now_hp
        return self.now_hp

    def spawn(self):
        set = mob_data.select(self.dtd["lv"])
        self.type, self.name, self.img_url = set.values()
        self.max_hp = self.now_hp = self.lv() * 100 + 10
        embed=discord.Embed(
            title=f"<{self.type}> {self.name} が出現！",
            description=f"Lv:{self.lv()} HP:{self.max_hp}"
        )
        embed.set_image(url=self.img_url)
        return embed

    def player_join(self, id):
        if id in self.battle_players:
            return False
        else:
            self.battle_players.append(id)
            return True
    def player_leave(self, id):
        if not id in self.battle_players:
            return False
        else:
            self.battle_players.remove(id)
            return True

    def battle_end(self):
        for p_id in self.battle_players:
            if p_id in box.players:
                box.players[p_id].battle_end()
        self.battle_players_id = []
        return self.spawn()

