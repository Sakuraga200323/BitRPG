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

client = pg = pg2 = None
def first_set(c,p):
    global client, pg, pg2
    client = c
    pg = p
    pg2 = client.pg2

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
        self.client = client
        self.dtd = pg.fetchdict(f"select * from player_tb where id = {self.user.id};")[0]
        self.max_hp = self.now_hp = self.lv() * 100 + 10
        self.max_mp = self.now_mp = self.lv()
        self.now_defe = self.max_defe = self.lv() * 10 + 10 + self.defe_p()
        self.battle_ch = None
        self.name = str(self.user)
        magic_class = self.dtd["magic_class"]
        if magic_class == 2:
            self.now_defe = self.max_defe = int(self.max_defe*1.1)
        if magic_class == 3:
            self.max_mp = self.now_mp = int(self.max_mp*1.1)
        print(f"NewPlayerClass: {self.user}")
        weapons = pg2.fetchdict(f"select id from weapon_tb where player_id = {self.user.id} limit 5")
        if not weapons:
            name = random.choice(list(box.shop_weapons.keys())[:3])
            emoji,rank = box.shop_weapons[name][0],2
            weapon = self.create_weapon(name,emoji,rank)
            self.weapon(weapon)
            self.weapons(weapon)
            print(f"NewPlayerClass: {self.weapon().name} {self.weapon().id}")
             
           
    def ID(self):
        return self.user.id
        
    # データの取得
    def get_data(self, target):
        return pg.fetchdict(f"select {target} from player_tb where id = {self.user.id};")[0][target]

    # データの値の上書き
    def update_data(self, target, temp):
        if target == 'id':
            return None
        else:
            pg.execute(f'update player_tb set {target}={temp} where id = {self.user.id};')

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
        client.pg2.execute(f"INSERT INTO weapon_tb (id,player_id,name,emoji,rank) VALUES ({weapon_id},{self.user.id},'{name}','{box.shop_weapons[name][0]}',{rank});")
        box.weapons[weapon_id] = Weapon(weapon_id) 
        return box.weapons[weapon_id]

    def drop_weapon(self,weapon):
        w_id = weapon.id
        self.weapons(weapon=weapon,drop=True)
        client.pg2.execute(f"delete from weapon_tb where id = {w_id};")
        if w_id in box.weapons:
            del box.weapons[w_id]


    def get_weapon(self,weapon):
        if len(self.weapons()) < 5:
            weapon.player_id(self)
            self.weapons(weapon)
    
    def weapon(self,weapon=False):
        if weapon:
            self.update_data("weapon",weapon.id)
        weapon_ = self.get_data("weapon")
        if weapon_:
            return box.weapons[weapon_]
        else:
            return None

    def weapon_id(self):
        if self.weapon():
            weapon_ = box.weapons[self.weapon().id]
            return weapon_
        else:
            return None
    
    def weapons(self,weapon=False,drop=False):
        weapons_ = list(self.get_data("weapons"))
        if weapon:
            if not drop:
                weapons_.append(weapon.id)
            else:
                if weapon.id in weapons_:
                    weapons_.remove(weapon.id)
            pg.execute(f'update player_tb set weapons=ARRAY{weapons_} where id = {self.user.id};')
        if weapons_ != []:
            weapons_ = [ box.weapons[i] for i in weapons_ if i in box.weapons]
            return weapons_
        else:
            return []

    def weapons_id(self):
        if self.weapons() != []:
            weapon_ = [ box.weapons[i] for i in self.weapons()]
            return weapon_
        else:
            return []

    # レベル取得
    def lv(self, plus=None):
        if isinstance(plus,int):
            lv = self.plus('lv', plus)
            self.max_hp = self.now_hp = lv * 100 + 10
            self.max_mp = self.now_mp = lv
            self.now_defe = self.max_defe = self.lv() * 10 + 10 + self.defe_p()
            magic_class = self.dtd["magic_class"]
            if magic_class == 2:
                self.max_defe = self.now_defe = int(self.max_defe*1.1)
            if magic_class == 3:
                self.max_mp = self.now_mp = int(self.max_mp*1.1)
        return self.get_data("lv")

    def max_lv(self, plus=None):
        if isinstance(plus,int):
            self.plus('max_lv', plus)
        return self.get_data("max_lv")

    def str(self):
        return self.lv() * 10 + 10

    def str_p(self, plus=None):
        if isinstance(plus,int):
            self.plus('str_p', plus)
        return self.get_data("str_p")


    def STR(self):
        magic_class = self.dtd["magic_class"]
        result = self.str()+self.str_p()
        if magic_class == 1:
            result = int((self.str()+self.str_p())*1.1)
        if self.weapon():
            result += self.weapon().strength()
        if magic_class == 2:
            strength_magnification = (1 - (self.now_hp / self.max_hp))*4
            result += result*strength_magnification
        return int(result)

    def defe(self):
        return self.lv() * 10 + 10

    def defe_p(self, plus=None):
        if isinstance(plus,int):
            self.plus('def_p', plus)
        return self.get_data("def_p")

    def DEFE(self):
        magic_class = self.dtd["magic_class"]
        if magic_class == 2: return int((self.defe()+self.defe_p())*1.1)
        else: return self.defe()+self.defe_p()

    def agi(self):
        result = self.lv() * 10 + 10
        return result

    def agi_p(self, plus=None):
        if isinstance(plus,int):
            self.plus('agi_p', plus)
        return self.get_data("agi_p")

    def AGI(self):
        magic_class = self.dtd["magic_class"]
        if magic_class == 3: return int((self.agi()+self.agi_p())*1.1)
        else: return self.agi()+self.agi_p()

    def now_stp(self, plus=None):
        if isinstance(plus,int):
            self.plus('now_stp', plus)
        return self.get_data("now_stp")
   
    def STP(self, plus=None):
        return self.str_p() + self.defe_p() + self.agi_p() + self.now_stp()


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
            self.plus('kill_count', plus)
        return self.get_data("kill_count")

    def magic_class(self):
        magic_class =  self.get_data("magic_class")
        if magic_class == 1: return "Wolf"
        elif magic_class == 2: return "Armadillo"
        elif magic_class == 3: return "Orca"

    def magic_lv(self, plus=None):
        if isinstance(plus,int):
            self.plus('magic_lv', plus)
        return self.get_data("magic_lv")

    def money(self, plus=None):
        if isinstance(plus,int):
            self.plus('money', plus)
        return self.get_data("money")

    def share_stp(self, target, point):
        self.now_stp(-point)
        magic_class = self.magic_class()
        if magic_class == 3:
            self.now_mp = int(self.max_mp*1.1)
        if target == "str":
            return self.str_p(point)
        if target == "def":
            self.max_defe = self.lv() * 10 + 10 + self.defe_p()
            if magic_class == 2:
                self.max_defe = int(self.max_defe*1.1)
            return self.defe_p(point)
        if target == "agi":
            return self.agi_p(point)

    def now_exp(self, plus=None):
        if isinstance(plus,int):
            self.plus('now_exp', plus)
        return self.get_data("now_exp")

    def max_exp(self, plus=None):
        if isinstance(plus,int):
            self.plus('max_exp', plus)
        return self.get_data("max_exp")

    def get_exp(self, exp):
        exp = int(exp)
        all_exp = self.now_exp(exp) 
        lv = self.lv()+1
        lvup_count = 0
        max_lv = self.max_lv()
        def get_lvup_count(a,c):
            n = math.sqrt(a**2+(2*c))-a
            return int(n)
        lvup_count = min(get_lvup_count(lv,all_exp),max_lv-lv)
        use_exp = int((2*lv+lvup_count-1)*lvup_count/2)
        print(use_exp)
        self.now_exp(-use_exp)
        self.max_exp(exp)
        if lvup_count > 0:
            result_lv = self.lv(lvup_count)
            self.now_stp(lvup_count*10)
            self.max_hp = self.now_hp = result_lv * 100 + 10
            self.max_mp = self.now_mp = result_lv
            self.now_defe = self.max_defe = result_lv * 10 + 10 + self.defe_p()
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
        dmg = int(strength) - self.now_defe
        if self.now_defe <= 0:
            self.now_defe = self.max_defe
        else:
            self.now_defe = max(self.now_defe-int(strength),0)
        return max(dmg,0), self.now_defe

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
        self.now_defe = self.max_defe = self.lv() * 10 + 10 + self.defe_p()
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
        cmd = f"select * from weapon_tb where id = {id}"
        data =  pg2.fetchdict(cmd)
        if data:
            data = data[0]
            self._id = data["id"]
            self.id = data["id"]
            print(f"NewWeaponClass: {data['name']} {id}")
        else:
            print(f"{id}の武器の取得に失敗")

            
    def get_data(self, target):
        return pg2.fetchdict(f"select {target} from weapon_tb where id = {self._id};")[0][target]
    def update_data(self, target, value):
        if target == 'id':
            return None
        else:
            pg2.execute(f'update weapon_tb set {target}={value} where id = {self.id};')
            return self.get_data(target)
    def plus(self, target, plus):
        if target == 'id':
            return None
        else:
            if plus < 0:
                pg2.execute(f'update weapon_tb set {target}={target}{plus} where id = {self.id_};')
            else:
                pg2.execute(f'update weapon_tb set {target}={target}+{plus} where id = {self.id_};')
            return self.get_data(target)

    
    # レベル取得
    def lv(self, plus=None):
        if isinstance(plus,int):
            return self.plus('lv', plus)
        else:
            return self.get_data("lv")
    
    def rank(self,get_int=False):
        if get_int:
            return self.get_data("rank")
        else:
            rank_dict={1:"D",2:"C",3:"B",4:"A",5:"S"}
            return rank_dict[self.get_data("rank")]

    def limit_lv(self, plus=None):
        if isinstance(plus,int):
            return self.plus('limit_lv', plus)
        else:
            return self.get_data('limit_lv')

    def player_id(self, set_player=False):
        if set_player:
            return self.update_data('player_id',set_player.ID())
        else:
            return self.get_data('player_id')


    def emoji(self, set_emoji=None):
        if set_emoji:
            return self.update_data('emoji',set_emoji.ID())
        else:
            return self.get_data('emoji')
    def name(self, set=None):
        if set:
            return self.update_data('name',set)
        else:
            return self.get_data('name')
    def now_exp(self,num):
        if isinstance(num,int):
            return self.plus('now_exp', plus)
        else:
            return self.get_data('now_exp')

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
            self.max_hp = result * 100
            self.max_defe = result * 10
            if self.type == "UltraRare":
                self.max_defe *= 5
                self.max_hp *= 5
            elif self.lv() % 1000 == 0:
                self.max_defe *= 5
                self.max_hp *= 5
            elif self.lv() % 100 == 0:
                self.max_defe *= 2
                self.max_hp *= 2
            elif self.lv() % 10 == 0:
                self.max_defe *= 2
                self.max_hp *= 2
            self.max_hp = int(self.max_hp)
            self.max_defe = int(self.max_defe)
            self.now_defe = self.max_defe
            self.now_hp = self.max_hp
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
        elif self.lv() % 1000 == 0:
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
        self.now_defe = self.max_defe = self.lv() * 10
        self.battle_players = []
        return self.spawn()
