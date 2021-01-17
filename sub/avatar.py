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

from sub import box, mob_data, status

JST = timezone(timedelta(hours=+9), 'JST')

client = pg = None
def first_set(c,p):
    global client, pg
    client = c
    pg = p

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

def set_client(c,pg):
    client = c
    pg = pg

#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨
class Player:
    def __init__(self, client, id):
        self.user = client.get_user(id)
        if not self.user:
            print(f"Playerデータ取得失敗: {id}のuserがNone。")
            return
        self.pg = pg
        self.pg2 = client.pg2
        self.client = client
        self.dtd = pg.fetchdict(f"select * from player_tb where id = {self.user.id};")[0]
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
        self.max_mp = self.now_mp = self.lv_
        self.now_defe = self.max_defe = self.lv_ * 10 + 10 + self.defe_p_
        magic_class = self.dtd["magic_class"]
        if magic_class == 2:
            self.now_defe = self.max_defe = int(self.max_defe*1.1)
        if magic_class == 3:
            self.max_mp = self.now_mp = int(self.max_mp*1.1)
        self.battle_ch = None
        self.name = str(self.user)
        self.weapon_id = self.dtd['weapon']
        self.weapons_id = list(self.dtd['weapons'])
        print(self.weapons_id)
        if self.weapons_id == [] or not self.weapon_id:
            self.weapon_id = int(datetime.now(JST).strftime("%d%m%y%H%M%S%f"))
            self.weapons_id = [self.weapon_id]
            weapon_name = random.choice(list(box.shop_weapons.keys())[0:3])
            weapon_info = box.shop_weapons[weapon_name]
            self.create_weapon(weapon_name,weapon_info[0],2)
        self.weapons = []
        self.weapon = None
        for i in self.weapons_id:
            box.weapons[i] = Weapon(i)
            self.weapons.append(box.weapons[i])
            if self.weapon_id == i:
                self.weapon = box.weapons[i]
             
            
           
    def ID(self):
        return self.user.id
        
    # データの取得
    def get_data(self, target):
        return pg.fetchdict(f"select {target} from player_tb where id = {self.user.id};")[0][target]

    # データの値の加算
    def plus(self, target, plus):
        if target == 'id':
            return None
        else:
            if plus < 0:
                pg.execute(f'update player_tb set {target}={target}{plus} where id = {self.user.id};')
            else:
                pg.execute(f'update player_tb set {target}={target}+{plus} where id = {self.user.id};')
            return self.get_data(target)

    def create_weapon(self,name,emoji,rank):
        weapon_id = int(datetime.now(JST).strftime("%y%d%m%H%M%S%f"))
        client.pg2.execute(f"INSERT INTO weapon_tb VALUES ({weapon_id},{self.user.id},'{name}','{box.shop_weapons[name][0]}',{rank}),1,0,1000;")
        box.weapons[weapon_id] = Weapon(weapon_id)
        weapon = box.weapons[weapon_id]
        weapon.set_owner(self)
        player.get_weapon(weapon)
        return weapon


    def get_weapon(self,weapon):
        if len(player.weapons) < 5:
            weapon.set_player(self)

    # レベル取得
    def lv(self, plus=None):
        if isinstance(plus,int):
            self.lv_ = self.plus('lv', plus)
            self.max_hp = self.now_hp = self.lv_ * 100 + 10
            self.max_mp = self.now_mp = self.lv_
            self.now_defe = self.max_defe = self.lv_ * 10 + 10 + self.defe_p_
            magic_class = self.dtd["magic_class"]
            if magic_class == 2:
                self.max_defe = self.now_defe = int(self.max_defe*1.1)
            if magic_class == 3:
                self.max_mp = self.now_mp = int(self.max_mp*1.1)
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
        magic_class = self.dtd["magic_class"]
        if magic_class == 1: return int((self.str()+self.str_p())*1.1)
        if self.weapon: return int((self.str()+self.str_p())*1.1) + self.weapon.strength()
        else: return self.str()+self.str_p()

    def defe(self):
        return self.lv() * 10 + 10

    def defe_p(self, plus=None):
        if isinstance(plus,int):
            self.defe_p_ = self.plus('def_p', plus)
        self.defe_p_ =  self.get_data("def_p")
        return self.defe_p_

    def DEFE(self):
        magic_class = self.dtd["magic_class"]
        if magic_class == 2: return int((self.defe()+self.defe_p())*1.1)
        else: return self.defe()+self.defe_p()

    def agi(self):
        result = self.lv() * 10 + 10
        return result

    def agi_p(self, plus=None):
        if isinstance(plus,int):
            self.agi_p_ = self.plus('agi_p', plus)
        self.agi_p_ =  self.get_data("agi_p")
        return self.agi_p_

    def AGI(self):
        magic_class = self.dtd["magic_class"]
        if magic_class == 3: return int((self.agi()+self.agi_p())*1.1)
        else: return self.agi()+self.agi_p()

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

    def item_num(self, target):
        if target in box.items_name:
            target = box.items_name[target]
        if not target in box.items_id:
            return None
        else:
            return pg.fetchdict(f"select item from player_tb where id = {self.user.id};")[0]["item"][target]

    def get_item(self, target, num):
        if target in box.items_name:
            target = box.items_name[target]
        if not target in box.items_name.keys():
            return None
        item_num = pg.fetchdict(f"select item from player_tb where id = {self.user.id};")[0]["item"][target]
        try:
            pg.execute(f"update player_tb set item = item::jsonb||json_build_object('{target}', {item_num + num})::jsonb where id = {self.user.id};")
        except:
            return None
        else:
            return item_num + num

    def pouch(self,space_id,set_item=None):
        if set_item in box.items_name:
            set_item = box.items_name[target]
        if set_item:
            pg.execute(f"update player_tb set pouch = pouch::jsonb||json_build_object('{space_id}', '{set_item}')::jsonb where id = {self.user.id};")
        return pg.fetchdict(f"select pouch from player_tb where id = {self.user.id};")[0]["pouch"][str(space_id)]
        
    def kill_count(self, plus=None):
        if isinstance(plus,int):
            self.kill_count_ = self.plus('kill_count', plus)
        self.kill_count_ =  self.get_data("kill_count")
        return self.kill_count_

    def magic_class(self):
        self.magic_class_ =  self.get_data("magic_class")
        if self.magic_class_ == 1: return "Wolf"
        elif self.magic_class_ == 2: return "Armadillo"
        elif self.magic_class_ == 3: return "Orca"

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
        magic_class = self.magic_class()
        if magic_class == 3:
            self.now_mp = int(self.max_mp*1.1)
        if target == "str":
            return self.str_p(point)
        if target == "def":
            self.max_defe = self.lv_ * 10 + 10 + self.defe_p_
            if magic_class == 2:
                self.max_defe = int(self.max_defe*1.1)
            return self.defe_p(point)
        if target == "agi":
            return self.agi_p(point)

    def get_exp(self, exp):
        exp = int(exp)
        self.max_exp(exp)
        lvup_count = 0
        now_exp = self.now_exp()
        lv = self.lv()
        while now_exp >= lv and self.max_lv() > lv:
            lvup_count += 1
            lv += 1
            now_exp -= lv
        if lvup_count > 0:
            self.lv(lvup_count)
            self.now_exp(now_exp-self.now_exp())
            self.now_stp(lvup_count*10)
            self.max_hp = self.now_hp = self.lv() * 100 + 10
            self.max_mp = self.now_mp = self.lv()
            self.now_defe = self.max_defe = self.lv_ * 10 + 10 + self.defe_p_
            magic_class = self.dtd["magic_class"]
            if magic_class == 2:
                self.max_defe = self.now_defe = int(self.max_defe*1.1)
            if magic_class == 3:
                self.max_mp = self.now_mp = int(self.max_mp*1.1)
        return exp, lvup_count

    def cut_hp(self, dmg):
        self.now_hp -= dmg if dmg<=self.now_hp else self.now_hp
        return self.now_hp

    def cut_mp(self, use_mp):
        self.now_mp -= use_mp if use_mp<=self.now_mp else self.now_mp
        return self.now_mp

    def cut_defe(self, strength):
        if self.now_defe <= 0:
            dmg = strength
            defe = 0
            self.now_defe = self.max_defe
        else:
            if strength > self.now_defe:
                dmg = strength - self.now_defe
                defe = 0
                self.now_defe = 0
            elif strength < self.now_defe:
                dmg = 0
                self.now_defe -= strength
                defe = self.now_defe
        return dmg, defe

    def damaged(self,strength):
        dmg,defe = self.cut_defe(int(strength))
        hp = self.cut_hp(dmg)
        return dmg, defe, hp

    def battle_start(self, id):
        if self.battle_ch and id != self.battle_ch:
            print(self.user.name,"is already battling in",self.battle_ch)
            return False
        self.battle_ch  = id
        return True

    def battle_end(self):
        self.battle_ch = None
        self.max_hp = self.now_hp = self.lv() * 100 + 10
        self.max_mp = self.now_mp = self.lv()
        self.now_defe = self.max_defe = self.lv_ * 10 + 10 + self.defe_p_
        magic_class = self.dtd["magic_class"]
        if magic_class == 2:
            self.max_hp = self.now_hp = int(self.max_hp*1.1)
            self.max_defe = self.now_defe = int(self.max_defe*1.1)
        if magic_class == 3:
            self.max_mp = self.now_mp = int(self.max_mp*1.1)



#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨
class Weapon:
    """
    psql2 create table weapon_tb(
        id bigint primary key,
        player_id bigint,
        name text,
        emoji text,
        rank int,
        lv bigint default 1,
        now_exp bigint default 0,
        limit_lv bigint default 1000
    )
    """

    def __init__(self,id):
        self.pg = client.pg2
        self.client = client
        self.dtd = client.pg2.fetchdict(f"select * from weapon_tb where id = {id};")[0]
        self.id_ = self.dtd["id"]
        self.player_id_ = self.dtd["id"]
        self.name = self.dtd["name"]
        self.emoji = self.dtd["emoji"]
        self.rank_ = self.dtd["rank"]
        self.lv_ = self.dtd["lv"]
        self.now_exp_ = self.dtd["now_exp"]
        self.limit_lv_ = self.dtd["limit_lv"]

    def get_data(self, target):
        return self.pg.fetchdict(f"select {target} from weapon_tb where id = {self.id_};")[0][target]
    def update_data(self, target, value):
        if target == 'id':
            return None
        else:
            self.pg.execute(f'update weapon_tb set {target}={value} where id = {self.id_};')
            return self.get_data(target)
    def plus(self, target, plus):
        if target == 'id':
            return None
        else:
            if plus < 0:
                self.pg.execute(f'update weapon_tb set {target}={target}{plus} where id = {self.id_};')
            else:
                self.pg.execute(f'update weapon_tb set {target}={target}+{plus} where id = {self.id_};')
            return self.get_data(target)

    # レベル取得
    def lv(self, plus=None):
        if isinstance(plus,int):
            self.lv_ = self.plus('lv', plus)
        self.lv_ =  self.get_data("lv")
        return self.lv_
    
    def rank(self,get_int=False):
        if get_int:
            return self.get_data("rank")
        else:
            rank_dict={1:"D",2:"C",3:"B",4:"A",5:"S"}
            return rank_dict[self.get_data("rank")]

    def lv(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('lv', plus)
        else:
            result = self.get_data('lv')
        return result

    def limit_lv(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('limit_lv', plus)
        else:
            result = self.get_data('limit_lv')
        return result

    def player_id(self, set_owner=None):
        if set_owner.ID() in box.players:
            self.update_data('player_id',set_owner.ID())   
        return self.get_data('player_id')

    def set_owner(self,player):
        self.player_id(set_owner=player)
        player.weapons_id = [ i.id_ for i in player.weapons()]
        self.pg.execute(f'update player_tb set weapons = ARRAY({player.weapons_id}) where id = {player.ID()}')

    def now_exp(self,num):
        if isinstance(plus,int):
            result = self.plus('now_exp', plus)
        else:
            result = self.get_data('now_exp')

    def get_exp(self, exp):
        exp = int(exp)
        lvup_count = 0
        now_exp = self.now_exp()
        lv = self.lv()
        while now_exp >= lv and self.limit_lv() > lv:
            lvup_count += 1
            lv += 1
            now_exp -= lv
        if lvup_count > 0:
            self.lv(lvup_count)
            self.now_exp(now_exp-self.now_exp())
        return lvup_count

    def strength(self,x=False):
        rank_dict={1:0.5,2:0.75,3:1.0,4:1.25,5:1.5}
        str_x = rank_dict[self.rank(get_int=True)]
        return int(self.lv()*5*str_x)



#🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨
class Mob:
    # id,lv
    def __init__(self, client, id):
        if client.get_channel(id):
            self.mob = client.get_channel(id)
            self.pg = pg
            self.client = client
            self.battle_players = []
            try:
                pg.execute(f"insert into mob_tb (id,lv) values ({id},1);")
            except psycopg2.errors.UniqueViolation:
                pass
            else:
                print(f"新規Mobデータを挿入: {id}")
            self.dtd = pg.fetchdict(f"select lv from mob_tb where id = {id};")[0]
            self.max_hp = self.now_hp = self.dtd["lv"] * 110
            set = mob_data.select(self.dtd["lv"])
            self.type, self.name, self.img_url = set.values()
            self.now_defe = self.max_defe = self.dtd["lv"] * 10
            if not id in box.mobs:
                box.mobs[id] = self
                
    def ID(self):
        return self.mob.id

    def get_data(self, target):
        return pg.fetchdict(f"select {target} from mob_tb where id = {self.mob.id};")[0][target]
    def plus(self, target, plus):
        if target == 'id':
            return None
        else:
            if plus < 0:
                pg.execute(f'update mob_tb set {target}={target}{plus} where id = {self.mob.id};')
            else:
                pg.execute(f'update mob_tb set {target}={target}+{plus} where id = {self.mob.id};')
            return self.get_data(target)

    def lv(self, plus=None):
        if isinstance(plus,int):
            result = self.plus('lv', plus)
            self.max_hp = self.now_hp = self.lv() * 100
            self.now_defe = self.max_defe = self.dtd["lv"] * 10
        else:
            result = self.get_data('lv')
        return result

    def weapon(self,get_all=True,get_using=False,sort='lv'):
        if get_all:
            return self.get_data('weapons')
        

    def str(self):
        num = self.lv() * 10
        if self.type == "UltraRare":num*=5
        elif self.lv() % 1000 == 0:num*=10
        elif self.lv() % 100 == 0:num*=5
        elif self.lv() % 10 == 0:num*=2
        return num

    def defe(self):
        num = self.lv() * 10
        if self.type == "UltraRare":num*=5
        elif self.lv() % 1000 == 0:num*=10
        elif self.lv() % 100 == 0:num*=5
        elif self.lv() % 10 == 0:num*=2
        return num

    def agi(self):
        num = self.lv() * 10
        if self.type == "UltraRare":num*=5
        elif self.lv() % 1000 == 0:num*=0
        elif self.lv() % 100 == 0:num*=5
        elif self.lv() % 10 == 0:num*=2
        return num

    def STR(self):
        num = self.str()
        return num
    def DEFE(self):
        num = self.defe()
        return num
    def AGI(self):
        num = self.agi()
        return num


    def reward(self):
        exp,money = int(self.lv()/2+1),random.randint(30,100)
        if self.type == "UltraRare":
            exp *= 100
            money *= 100
        elif self.type == "Rare":
            exp *= 5
            money *= 5
        if self.lv() % 1000 == 0:
            exp *= 100
            money *= 100
        elif self.lv() % 100 == 0:
            exp *= 5
            money *= 5
        elif self.lv() % 10 == 0:
            exp *= 2
            money *= 2
        return exp, money

    def cut_hp(self, dmg):
        self.now_hp -= dmg if dmg <= self.now_hp else self.now_hp
        return self.now_hp

    def cut_defe(self, strength):
        if self.now_defe <= 0:
            dmg = strength
            defe = 0
            self.now_defe = self.max_defe
        else:
            if strength > self.now_defe:
                dmg = strength - self.now_defe
                self.now_defe = 0
                defe = 0
            elif strength < self.now_defe:
                dmg = 0
                self.now_defe -= strength
                defe = self.now_defe
        return dmg, defe

    def damaged(self,str):
        dmg,defe = self.cut_defe(int(str))
        hp = self.cut_hp(dmg)
        return dmg, defe, hp

    def spawn(self):
        set = mob_data.select(self.lv())
        self.type, self.name, self.img_url = set.values()
        self.max_hp = self.now_hp = self.lv() * 100
        embed=discord.Embed(
            title=f"<{self.type}> {self.name} が出現！",
            description=f"Lv.{self.lv()} HP.{self.max_hp}"
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
        self.now_defe = self.max_defe = self.dtd["lv"] * 10
        self.battle_players = []
        return self.spawn()
