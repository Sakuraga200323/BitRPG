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

pg = None

#➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖#

"""
create table player_tb(
    id bigint,
    lv bigint,
    max_lv bigint
    max_exp bigint,
    now_exp bigint,
    now_stp bigint,
    str_p bigint,
    def_p bigint,
    agi_p bigint,
    magic_class int,
    magic_lv bigint,
    kill_count bigint,
    item jsonb,
    money bigint,
    primary key (id)
)"""


class Player:
    def __init__(self, client, id):
        self.user = client.get_user(id)
        if not self.user:
            print(f"データ挿入失敗: {id}のuserがNone。")
            return
        self.pg = pg
        self.client = client
        self.dtd = self.pg.fetchdict(f"select * from player_tb where id = {self.user.id};")[0]
        print(list(self.dtd.values())[1:12])
        data_list = [
            self.dtd["lv"], self.dtd["max_lv"], 
            self.dtd["max_exp"], self.dtd["now_exp"], 
            self.dtd["now_stp"], self.dtd["str_p"], self.dtd["def_p"], self.dtd["agi_p"], 
            self.dtd["magic_class"], self.dtd["magic_lv"], 
            self.dtd["kill_count"], self.dtd["item"], self.dtd["money"]
        ]
        [
            self.lv_, self.max_lv_, 
            self.max_exp_, self.now_exp_, 
            self.now_stp_, self.str_p_, self.defe_p_, self.agi_p_, 
            self.magic_class_, self.magic_lv_, 
            self.kill_count_, self.item_, self.money_
        ] = data_list
        self.max_hp = self.now_hp = self.lv_ * 100 + 10
        self.max_mp = self.now_mp = self.lv_ * 10
        self.battle_ch = None
        if not id in box.players:
            box.players[id] = self
            print(f"Playerデータ挿入： {self.user}")
        

    # データの取得
    def get_data(self, target):
        return self.pg.fetchdict(f"select {target} from player_tb where id = {self.user.id};")[0][target]

    # データの値の加算
    def plus(self, target, plus):
        if target == 'id':
            return None
        else:
            if plus < 0:
                self.pg.execute(f'update player_tb set {target}={target}{plus} where id = {self.user.id};')
            else:
                self.pg.execute(f'update player_tb set {target}={target}+{plus} where id = {self.user.id};')
            return self.get_data(target)

    # レベル取得
    def lv(self, plus=None):
        if isinstance(plus,int):
            self.lv_ = self.plus('lv', plus)
            self.max_hp = self.now_hp = self.lv_ * 100 + 10
            self.max_mp = self.now_mp = self.lv_ * 10
        self.lv_ =  self.get_data("lv")
        return self.lv_

    def max_lv(self, plus=None):
        if isinstance(plus,int):
            self.max_lv_ = self.plus('max_lv', plus)
        self.max_lv_ =  self.get_data("max_lv")
        return self.max_lv_

    def str(self):
        return self.lv() * 10 + 10

    def str_p(self, plus=None):
        if isinstance(plus,int):
            self.str_p_ = self.plus('str_p', plus)
        self.str_p_ =  self.get_data("str_p")
        return self.str_p_

    def STR(self):
        return self.str() + self.str_p()

    def defe(self):
        return self.lv() * 10 + 10

    def defe_p(self, plus=None):
        if isinstance(plus,int):
            self.defe_p_ = self.plus('def_p', plus)
        self.defe_p_ =  self.get_data("def_p")
        return self.defe_p_

    def DEFE(self):
        return self.defe() + self.defe_p()

    def agi(self):
        result = self.lv() * 10 + 10
        return result

    def agi_p(self, plus=None):
        if isinstance(plus,int):
            self.agi_p_ = self.plus('agi_p', plus)
        self.agi_p_ =  self.get_data("agi_p")
        return self.agi_p_

    def AGI(self):
        return self.agi() + self.agi_p()

    def now_stp(self, plus=None):
        if isinstance(plus,int):
            self.now_stp_ = self.plus('now_stp', plus)
        self.now_stp_ =  self.get_data("now_stp")
        return self.now_stp_
   
    def STP(self, plus=None):
        return self.str_p() + self.defe_p() + self.agi_p() + self.now_stp()

    def now_exp(self, plus=None):
        if isinstance(plus,int):
            self.now_exp_ = self.plus('now_exp', plus)
        self.now_exp_ =  self.get_data("now_exp")
        return self.now_exp_

    def max_exp(self, plus=None):
        if isinstance(plus,int):
            self.now_exp_ = self.plus('now_exp', plus)
            self.max_exp_ = self.plus('max_exp', plus)
        self.max_exp_ =  self.get_data("max_exp")
        return self.max_exp_

    def kill_count(self, plus=None):
        if isinstance(plus,int):
            self.kill_count_ = self.plus('kill_count', plus)
        self.kill_count_ =  self.get_data("kill_count")
        return self.kill_count_

    def magic_class(self):
        self.magic_class_ =  self.get_data("magic_class")
        return self.magic_class_

    def magic_lv(self, plus=None):
        if isinstance(plus,int):
            self.magic_lv_ = self.plus('magic_lv', plus)
        self.magic_lv_ =  self.get_data("magic_lv")
        return self.magic_lv_

    def money(self, plus=None):
        if isinstance(plus,int):
            self.money_ = self.plus('money', plus)
        self.money_ =  self.get_data("money")
        return self.money_

    def share_stp(self, target, point):
        self.now_stp(-point)
        if target == "str":
            self.str_p(point)
            temp = self.str_p_
        if target == "def":
            self.defe_p(point)
            temp = self.defe_p_
        if target == "agi":
            self.agi_p(point)
            temp = self.agi_p_
        return temp

    def get_exp(self, exp):
        self.max_exp(exp)
        lvup_count = 0
        self.now_exp()
        while self.now_exp() >= self.lv() and self.max_lv() > self.lv():
            lvup_count += 1
            self.now_exp(-self.lv(1))
        if lvup_count > 0:
            self.now_stp(lvup_count*10)
            self.max_hp = self.now_hp = self.lv() * 100 + 10
            self.max_mp = self.now_mp = self.lv()
        return exp, lvup_count

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
            self.pg = pg
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
                self.pg.execute(f'update mob_tb set {target}={target}{plus} where id = {self.mob.id};')
            else:
                self.pg.execute(f'update mob_tb set {target}={target}+{plus} where id = {self.mob.id};')
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
        str_correction ={
            "Bicorn":1.3,
            "GoblinSoldier":1,
            "Golem":1,
            "Kerberos":1.3,
            "LizardGoblin":1.1,
            "Lorg":1,
            "Manticore":1.3,
            "Mummy":1,
            "Orc":1.2,
            "Phelios":0.7,
            "Roguenite":1.2,
            "Skeleton":0.8,
            "Sludge":1,
            "Succubus":0.8,
            "Theaf":0.9,
            "Valkyrie":1.3,
        }
        if self.name in str_correction:
            return int(result*str_correction[self.name])
        else:
            return result

    def defe(self):
        result = self.lv() * 10 + 10
        defe_correction ={
            "Bicorn":1.3,
            "GoblinSoldier":1,
            "Golem":2,
            "Kerberos":1.3,
            "LizardGoblin":1.1,
            "Lorg":0.8,
            "Manticore":1.3,
            "Mummy":0.8,
            "Orc":1.2,
            "Phelios":0.7,
            "Roguenite":1.2,
            "Skeleton":0.8,
            "Sludge":1.5,
            "Succubus":0.8,
            "Theaf":0.8,
            "Valkyrie":1.3,
        }
        if self.name in defe_correction:
            return int(result*defe_correction[self.name])
        else:
            return result

    def agi(self):
        result = self.lv() * 10 + 10
        agi_correction ={
            "Bicorn":1.3,
            "GoblinSoldier":1,
            "Golem":0.7,
            "Kerberos":1.3,
            "LizardGoblin":1.2,
            "Lorg":0.8,
            "Manticore":1.3,
            "Mummy":0.8,
            "Orc":1.2,
            "Phelios":1.2,
            "Roguenite":1,
            "Skeleton":1,
            "Sludge":0.8,
            "Succubus":1.1,
            "Theaf":1.5,
            "Valkyrie":1.3,
        }
        if self.name in agi_correction:
            return int(result*agi_correction[self.name])
        else:
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
        exp *= 0.75
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
        self.battle_players = []
        return self.spawn()

