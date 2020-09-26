import ast
import asyncio
from datetime import datetime, timedelta, timezone
import math
import os
import random
import re

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

class Player:
    def __init__(self, client, user):
        if isinstance(user, int):
            id = user
        else:
            id = user.id
        self.data_dict = pg.fetch_dict(f"select * from player_tb where id = {id};")

    def data(self, target):
        if target in self.data_dict.keys():
            return self.data_dict[target]
        else:
            return None

    def update(self,target,new_num):
        if new_num and target:
            try:
                pg.execute(f"update player_tb set {target} = {new_num} where id = {id};")
            except:
                return False:
            else:
                return True

        

    def hp_cut(self, dmg):
        if isinstance(dmg, int):
            self.data_dict["now_hp"] -= dmg
        if self.data_dict["now_hp"] < 0:
            self.data_dict["now_hp"] = 0
        result = self.data_dict["now_hp"]
        pg.execute(f"update player_tb set now_hp = {result} where id = {id};")
        return result

    def str(self, x = None):
        target = "str"
        if x:
            self.data_dict[target] = x
            self.update(target, x)
        return self.data_dict[target]
    def def():
        target = "def"
        if x:
            self.data_dict[target] = x
            self.update(target, x)
        return self.data_dict[target]
    def agi(self, x):
        target = "agi"
        if x:
            self.data_dict[target] = x
            self.update(target, x)
        return self.data_dict[target]
    def stp(self, x):
        target = "stp"
        if x:
            self.data_dict[target] = x
            self.update(target, x)
        return self.data_dict[target]
    def (self, x):
        target = ""
        if x:
            self.data_dict[target] = x
            self.update(target, x)
        return self.data_dict[target]
    def str_stp(self, x):
        target = "str_stp"
        if x:
            self.data_dict[target] = x
            self.update(target, x)
        return self.data_dict[target]
    def def_stp(self, x):
        target = "def_stp"
        if x:
            self.data_dict[target] = x
            self.update(target, x)
        return self.data_dict[target]
    def agi_stp(self, x):
        target = "agi_stp"
        if x:
            self.data_dict[target] = x
            self.update(target, x)
        return self.data_dict[target]


def rename_request(client, user, ch):
    global client; client = client
    player = Player(client, user.id)
    
