# coding: utf-8
# Your code here!
import math
import ast
import asyncio
from datetime import datetime, timedelta, timezone
import discord
from discord.ext import tasks
import glob
import os
import psutil
import psycopg2A
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
        print(f"{self.user}:[{self.dtd}]")
