import ast
import asyncio
import cv2
from datetime import datetime, timedelta, timezone
import math
import os
from random import random, randint, choice
import re
import sys

import discord
from discord.ext import tasks, commands
import psutil
import psycopg2, psycopg2.extras
import traceback

from sub import box, status, avatar, calc,  magic_wolf, magic_orca, magic_armadillo

JST = timezone(timedelta(hours=+9), 'JST')

client = pg = None
def first_set(c,p):
    global client, pg
    client = c
    pg = p


# ⬜⬜⬜BattleStartチェック⬜⬜⬜ #
async def battle_start(player, mob):
    ch = mob.mob
    user = player.user
    if not user.id in box.players:
        print("box.playersに存在しないPlayer.idを取得")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from player_tb;")]:
            box.players[user.id] = player
            print(f"Playerデータ挿入(battle.py->cbt_proc)： {player.user}")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from mob_tb;")]:
            box.mobs[user.id] = mob
            print(f"Mobデータ挿入(battle.py->cbt_proc)： {mob.name}")
    if not player.battle_start(ch.id):
        channel = client.get_channel(player.battle_ch)
        if channel:
            em = discord.Embed(description=f"<@{user.id}> は現在『{channel.mention}』で戦闘中")
            await ch.send(embed=em)
            return False
        em = discord.Embed(description=f"<@{user.id}> が認識できないチャンネルで戦闘中 データの上書き開始")
        await ch.send(embed=em)
        player.battle_end()
        if player.battle_start(ch.id):
            em = discord.Embed(description=f"上書き完了 戦闘に参加")
            await ch.send(embed=em)
        else:
            em = discord.Embed(description=f"上書き失敗 戦闘に参加できていません")
            await ch.send(embed=em)
            return False
    if player.now_hp <= 0:
        em = discord.Embed(description=f"<@{user.id}> は既に死亡しています")
        await ch.send(embed=em)
        return False
    mob.player_join(user.id)
    return True


# ⬜⬜⬜BattleResultEmbed作成⬜⬜⬜ #
async def battle_result(player, mob):
    types = ("Normal","Elite","Catastrophe","WorldEnd","Rare","UltraRare","UltraEro")
    reward_items = { # {id:(num,item was droped)}
        2:(randint(3,6),random()<=0.05 or mob.type in types[2:]),
        3:(randint(3,6),random()<=0.05 or mob.type in types[2:]),
        4:(randint(1,5),True),
        5:(randint(1,2),mob.name in ("モノリス",'ゴールド-モノリス') or mob.type in types[1:]),
        6:(randint(3,6),random()<=0.03 or mob.type in types[2:]),
        11:(randint(3,6),(random()<=0.05 and mob.lv()%10==0) or mob.type in ("UltraRare",)),
        13:(randint(3,6),(random()<=0.05 and mob.lv()%10==0) or mob.type in ("UltraRare",)),
        15:(randint(2,5),(random()<=0.05 and mob.lv()%100==0) or mob.type in ("UltraRare",)),
        17:(randint(2,5),(random()<=0.05 and mob.lv()%100==0) or mob.type in ("UltraRare",)),
        19:(randint(1,3),(random()<=0.05 and mob.lv()%100==0) or mob.type in ("UltraRare","UltraEro")),
        21:(randint(1,3),(random()<=0.05 and mob.lv()%100==0) or mob.type in ("UltraRare","UltraEro")),
        23:(randint(3,6),(random()<=0.025 or mob.type in types[1:])),
        25:(1,mob.name in ("ドワーフ") and random()<=0.01),
    }
    ch = mob.mob
    user = player.user
    result_em = stp_em = item_em = spawn_em = None
    anti_magic_em = None
    if mob.now_hp <= 0 :
        if mob.ID() in box.anti_magic:
            box.anti_magic.remove(mob.ID())
        if mob.mob.id in box.nerf:
            del box.nerf[mob.mob.id]
        if mob.mob.id in box.stun:
            del box.stun[mob.mob.id]
        result_desc = ""
        now = datetime.now(JST).strftime("%H:%M %b")
        exp, money = mob.reward()[0]+1, int(mob.reward()[1]/len(mob.battle_players))
        guild = client.get_guild(719165196861702205)
        if  now in ['23:18 Sat']:
            exp *= 3
            await ch.send("**初代開発者**『今日生きているからといって、明日生きているとは限らない。』")
        print(f"『{mob.name:　<10}』(Lv.{mob.lv()})を{[ str(client.get_user(i)) for i in mob.battle_players]}が討伐")
        roles_mention = (
            '<@&800263879607189515>', 
            '<@&800262422774415381>',
            '<@&763409546424352769>',
            '<@&800261859927654401>',
            '<@&800261583732604928>',
            '<@&763359264672579605>',
            '<@&763404511318245416>',
            '<@&799961431536697366>',
        )
        roles = tuple([ discord.utils.get(guild.roles,mention=i) for i in roles_mention])
        for p_id in mob.battle_players:
            p = box.players[p_id]
            EXP = exp
            member = guild.get_member(p_id)
            if member:
                for role in roles[:-1]:
                    if role in member.roles:
                        EXP += (exp*0.1)
            EXP = int(EXP)
            up_exp, up_lv = p.get_exp(EXP)
            p.kill_count(1)
            p.money(money)
            if p.ID() == player.ID():
                result_desc += f"\n*<@{p_id}>*"
            else:
                result_desc += f"\n<@{p_id}>"
            result_desc += f"\n> Exp+{EXP} Cell+{money}"
            if up_lv > 0:
                result_desc += f"\n> LvUP {p.lv()-up_lv} → {p.lv()}"
            p.battle_end()
        result_em = discord.Embed(title="Result",description=result_desc,color=discord.Color.green())
        # ドロップアイテムfor #
        drop_item_text = ''
        member = guild.get_member(player.ID())
        user_is_frontier = False
        if member:
            user_is_frontier = roles[-1] in member.roles
        for id in reward_items:
            num,item_was_droped = reward_items[id]
            if item_was_droped:
                status.get_item(player.user,id,num)
                drop_item_text += f"{box.items_emoji[id]}×{num} "
            else:
                if user_is_frontier:
                    if random() <= 0.001:
                        status.get_item(player.user,id,num)
                        drop_item_text += f"(開拓者Bonus!!{box.items_emoji[id]}×{num}) "
        result_em.add_field(name=f"Drop Item",value=f"<@{user.id}>\n>>> {drop_item_text}")
        if random() <= 0.001:
            player.now_stp(500)
            result_em.add_field(name=f"Lucky Bonus",value=f"<@{user.id}>\n>>> STP+500")
        if mob.lv() % 100 == 0:
            player.money(1000)
            result_em.add_field(name=f"Last Attack Bonus",value=f"<@{user.id}>\n>>> Cell+1000")
        if len([ch.name for ch in mob.mob.guild.text_channels if ch.name.startswith('⚙️lv1-')]):
            ch_name = [ch.name for ch in mob.mob.guild.text_channels if ch.name.startswith('🔒lvup-')][0].split('🔒lvup-')[1]
            if not mob.mob.name.startswith(ch_name):
                mob.lv(update=1)
        else:
            mob.lv(plus=1)
        spawn_em = mob.battle_end()
        irregular_text = ''
        if mob.type in ("Elite","UltraRare",""):
            box.anti_magic.append(mob.ID())
            irregular_text += f"{mob.name} のアンチマジックエリアが発動！"
        if mob.type in ("WoldEnd","UltraRare",""):
            box.sleep[mob.ID()] = 3
            irregular_text += f"\n{mob.name} は眠っている…"
        if irregular_text != '':
            anti_magic_em = discord.Embed(description=irregular_text)
    return result_em, spawn_em, anti_magic_em


# ⬜⬜⬜BattleText作成⬜⬜⬜ #
def create_battle_text(a,b,set_strength=False,strength_rate=1,dodge_rate=1,critical_rate=0.05,atk_word="攻撃",buff=0):
    if a.now_hp <= 0:
        if a.ID() in box.players:
            battle_text = f"{a.name} はやられてしまった"
        else:
            battle_text = f"{a.name} を倒した"
    else:
        a_is_player = a.ID() in box.players
        a_is_mob = not a.ID() in box.players
        b_is_player = b.ID() in box.players
        b_is_mob = not b.ID() in box.players
        head_text = "・"
        plus_or_minus = ""
        if a_is_player:
            a_mark,b_mark = "<:emoji_33:804704525860208650>","<:emoji_34:804704652305236038>"
        else:
            b_mark,a_mark = "<:emoji_33:804704525860208650>","<:emoji_34:804704652305236038>"
        battle_text = f"{a_mark} **{a.name}**の{atk_word}"
        irregular_text = ''
        a_strength = int(a.STR()*strength_rate)
        if set_strength:
            print(set_strength)
            a_strength = set_strength
        a_id = a.ID()
        a_was_stun,a_was_nerf,a_was_fleeze,a_was_berserk,a_was_angry,a_was_sleep = False,False,False,False,False,False
        if (a_id in box.sleep) :
            a_strength = 0
            a_was_sleep = True
            irregular_text = f'\n{head_text}[`Sleep`]眠っているようだ…'
            box.sleep[a_id] -= 1
            if box.sleep[a_id] <= 0:
                del box.sleep[a_id]
        if a_id in box.fleez and a_strength:
            a_strength = 0
            irregular_text = f'\n{head_text}[`Fleeze`]攻撃力**0**！'
            a_was_fleeze = True
        if a_id in box.stun and a_strength:
            a_was_stun = True
            if random() <= 0.8 or a_id in box.nerf:
                box.stun[a_id] -= 1
                a_strength = 0
                irregular_text = f'\n{head_text}[`Stun`]攻撃力**0**！ (Stun×**{box.stun[a_id]}**)'
                if box.stun[a_id] <= 0:
                    del box.stun[a_id]
            else:
                a_strength -= int(a.STR()*0.2)
                irregular_text = f'\n{head_text}[`Stun`]攻撃力小幅減少！ (Stun×**{box.stun[a_id]}**)'
        if a_id in box.nerf and a_strength:
            box.nerf[a_id] -= 1
            a_was_nerf = True
            a_strength = int(a_strength/2)
            irregular_text = f'\n{head_text}[`Nerf`]攻撃力大幅減少！ (Nerf×**{box.nerf[a_id]}**)'
            if box.nerf[a_id] <= 0:
                del box.nerf[a_id]
        if (a_id in box.angry and a_strength) :
            a_was_angry = True
            critical_rate = 0.1
            irregular_text = f'\n{head_text}[`Angry`]急所率上昇！ (Angry×**{box.angry[a_id]}**)'
            box.angry[a_id] -= 1
            if box.angry[a_id] <= 0:
                del box.angry[a_id]
        if (a_id in box.berserk and a_strength) :
            a_was_berserk = True
            a_strength += a.STR()*2
            irregular_text = f'\n{head_text}[`Berserk`]攻撃力上昇、防御力**0**！ (Berserk×**{box.berserk[a_id]}**)'
            box.berserk[a_id] -= 1
            if box.berserk[a_id] <= 0:
                del box.berserk[a_id]
        if a_strength:
            if random() <= critical_rate:
                a_strength += a.STR()*4
                irregular_text += f'\n{head_text}急所に当たった！'
            elif random() <= min(((b.AGI()/a.AGI() - 1) if a.AGI()>0 else 0)*dodge_rate, 0.75):
                if b.ID() in box.stun:
                    if random() <= 0.5:
                        a_strength = 0
                        irregular_text += f'\n{head_text}{b.name} はギリギリ避けた！'
                else:
                    a_strength = 0
                    irregular_text += f'\n{head_text}{b.name} は華麗に避けた！'
            elif a_id in box.atk_switch:
                b_id = box.atk_switch[a_id]
                if b_id in box.players:
                    a_strength -= int(a.STR()/2)
                    if b_id == b.ID():
                        irregular_text += f"\n{head_text}{b.name} が攻撃を防いだ！ (Target**{b.name}**)"
                    else:
                        b = box.players[b_id]
                        irregular_text += f"\n{head_text}{b.name} は攻撃を見切った！ (Target**{b.name}**)"
                    del box.atk_switch[a_id]
        if b.ID() in box.fleez:
            box.fleez.remove(b.ID())
        battle_text += irregular_text
        a_strength = int(a_strength)
        b_dmg,b_now_def,b_now_hp = b.damaged(a_strength)
        battle_text += f'\n{head_text}**{b_dmg}**ダメージ (-**{a_strength-b_dmg}**)'
        release_by_buff = '\n'+head_text
        if a_was_stun and not a_id in box.stun:
            release_by_buff += 'Stun '
        if a_was_nerf and not a_id in box.nerf:
            release_by_buff += 'Nerf '
        if a_was_fleeze and not a_id in box.fleeze:
            release_by_buff += 'Fleeze '
        if a_was_sleep and not a_id in box.sleep:
            release_by_buff += 'Sleep '
        if a_was_angry and not a_id in box.angry:
            release_by_buff += 'Angry '
        if a_was_berserk and not a_id in box.berserk:
            release_by_buff += 'Berserk '
        if release_by_buff != '\n'+head_text:
            release_by_buff += 'が切れた！'
            battle_text += release_by_buff
        if buff in [1,2] and not a.ID() in box.stun:
            buff_dict = {1:"Stun",2:"Nerf"}
            battle_text += f"\n{head_text}{buff_dict[buff]} 付与"
            if buff == 1:
                box.stun[b.ID()] = 3
            if buff == 2:
                box.nerf[b.ID()] = 5
        battle_text += f"\n{b_mark} {b.name} の状態\n{create_defe_gauge(b.DEFE(),b_now_def)}\n{create_hp_gauge(b.max_hp,b_now_hp,b.ID())}"
        if b_is_mob and b.now_hp > 0 and b.type in ("UltraRare","WorldEnd"):
            if b.now_hp <= (b.max_hp*0.5):
                box.angry[b.ID()] = 5
                battle_text += f'\n{head_text}怒り狂っている…！(Angry×**5**)'
            if b.now_hp <= (b.max_hp*0.75):
                box.berserk[b.ID()] = 5
                battle_text += f'\n{head_text}大狂乱…！(Berserk×**5**)'
    return battle_text


# ⬜⬜⬜HPGauge作成⬜⬜⬜ #
def create_hp_gauge(max_hp,now_hp,id):
    hp_ratio = now_hp/max_hp
    num = 10*hp_ratio
    full_gauge_num = int(num)
    half_gauge_num = 0 if (num-full_gauge_num) < 0.5 else 1
    empty_gauge_num = 10 - full_gauge_num - half_gauge_num
    if (full_gauge_num+empty_gauge_num) <= 0 and not now_hp <= 0:
        half_gauge_num = 1
        empty_gauge_num -= 1
    if not half_gauge_num and (now_hp > 0 and now_hp < max_hp):
        full_gauge_num -= 1
        full_gauge = box.gauge_emoji["hp_full"]*full_gauge_num + "<:emoji_32:804676170355310612>"
    else:
        full_gauge = box.gauge_emoji["hp_full"]*full_gauge_num
    half_gauge = box.gauge_emoji["hp_half"]*half_gauge_num
    empty_gauge = box.gauge_emoji["hp_empty"]*empty_gauge_num
    if max_hp <= now_hp:
        end_gauge = box.gauge_emoji["hp_end_full"]
    else:
        end_gauge = box.gauge_emoji["hp_end_empty"]
    head_gauge = box.gauge_emoji["hp_head"]
    gauge = full_gauge + half_gauge + empty_gauge + end_gauge
    gauge_list = [ '<'+i for i in gauge.split('<')[1:] ]
    if not id in box.hp_box:
        box.hp_box[id] = [
            box.gauge_emoji["hp_full"],box.gauge_emoji["hp_full"],
            box.gauge_emoji["hp_full"],box.gauge_emoji["hp_full"],
            box.gauge_emoji["hp_full"],box.gauge_emoji["hp_full"],
            box.gauge_emoji["hp_full"],box.gauge_emoji["hp_full"],
            box.gauge_emoji["hp_full"],box.gauge_emoji["hp_full"],
            box.gauge_emoji["hp_end_full"]]
    for a,b,num in zip(gauge_list,box.hp_box[id],range(0,20)):
        if b in list(box.damaged_gauge_emoji.values()):
            b = box.gauge_emoji['hp_empty']
        if b != a and not b in (box.gauge_emoji['hp_empty'],box.gauge_emoji['hp_end_empty']):
            if (b,a) in ((box.gauge_emoji['hp_full'],box.gauge_emoji['hp_half']),(box.gauge_emoji['hp_full'],'<:emoji_32:804676170355310612>')):
                after_emoji = box.damaged_gauge_emoji['full_half']
            else:
                after_emoji = box.damaged_gauge_emoji[b]
            if num > 0 and gauge_list[num-1] == box.gauge_emoji['hp_full'] and a in ('<:emoji_37:804843399902920714>',):
                after_emoji = '<:emoji_39:805060168689516607>'
            gauge_list[num] = after_emoji
            
    corect_gauge = head_gauge + (','.join(gauge_list)).replace(',','')
    box.hp_box[id] = gauge_list
    return corect_gauge


# ⬜⬜⬜DefenceGauge作成⬜⬜⬜ #
def create_defe_gauge(max_defe,now_defe):
    hp_ratio = now_defe/max_defe
    num = 10*hp_ratio
    full_gauge_num = int(num)
    half_gauge_num = 0 if (num-full_gauge_num) < 0.5 else 1
    empty_gauge_num = 10 - full_gauge_num - half_gauge_num
    if (full_gauge_num+empty_gauge_num) <= 0 and not now_defe <= 0:
        half_gauge_num = 1
        empty_gauge_num -= 1
    full_gauge = box.gauge_emoji["defe_full"]*full_gauge_num
    half_gauge = box.gauge_emoji["defe_half"]*half_gauge_num
    empty_gauge = box.gauge_emoji["defe_empty"]*(empty_gauge_num)
    gauge = full_gauge + half_gauge + empty_gauge
    return gauge


# ⬜⬜⬜attack⬜⬜⬜ #
async def cbt_proc(user, ch):
    player = box.players[user.id]
    mob = box.mobs[ch.id]
    start_result = await battle_start(player,mob)
    if not start_result:
        return
    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        text1 = create_battle_text(player,mob)
        text2 = create_battle_text(mob,player)
    # 戦闘処理（Player後手） #
    else:
        text1 = create_battle_text(mob,player)
        text2 = create_battle_text(player,mob)
    if player.now_hp > 0:
        player.weapon().get_exp(2)
    battle_log = f">>> {text1}\n＊　＊　＊　＊\n{text2}"
    result_em,spawn_em,anti_magic_em = await battle_result(player, mob)
    await ch.send(content=battle_log,embed=result_em)
    if spawn_em:await ch.send(embed=spawn_em)
    if anti_magic_em:await ch.send(embed=anti_magic_em)


# ⬜⬜⬜戦闘から離脱⬜⬜⬜ #
async def reset(user, ch):
    player,mob = box.players[user.id],box.mobs[ch.id]
    if not user.id in box.players:
        print("box.playersに存在しないPlayer.idを取得")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from player_tb;")]:
            box.players[user.id] = player
            print(f"Playerデータ挿入(battle.py->cbt_proc)： {player.user}")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from mob_tb;")]:
            box.mobs[user.id] = mob
            print(f"Mobデータ挿入(battle.py->cbt_proc)： {mob.name}")
    if not player.battle_ch:
        player.now_hp = player.max_hp
        await ch.send(embed=discord.Embed(description=f"戦闘に参加していなかったのでHPを全回復しました。"))
        return
    now_ch = client.get_channel(player.battle_ch)
    if player.battle_ch != ch.id:
        await ch.send(embed=discord.Embed(description=f"<@{player.user.id}> は現在『{now_ch.mention}』で戦闘中です。"))
        return
    mob.battle_end()
    if player.ID() in box.power_charge:
        del box.power_charge[player.ID()]
    if mob.ID() in box.stun:
        del box.stun[mob.ID()]
    if mob.ID() in box.nerf:
        del box.nerf[mob.ID()]
    await ch.send(embed = mob.spawn())
    if mob.type in ("Elite","UltraRare","Catastrophe"):
        if not mob.ID() in box.anti_magic:
            box.anti_magic.append(mob.ID())
        anti_magic_em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動！")
        await ch.send(embed=anti_magic_em)
                    

# ⬜⬜⬜魔法一覧⬜⬜⬜ #
async def open_magic(user,ch):
    player,mob = box.players[user.id],box.mobs[ch.id]
    if player.magic_class() == "Wolf":
        await magic_wolf.open_magic(user,ch)
    if player.magic_class() == "Armadillo":
        await magic_armadillo.open_magic(user,ch)
    if player.magic_class() == "Orca":
        await magic_orca.open_magic(user,ch)

# ⬜⬜⬜魔法使用⬜⬜⬜ #
async def use_magic(user,ch,target):
    player,mob = box.players[user.id],box.mobs[ch.id]
    if ch.id in box.anti_magic:
        if player.magic_class() == "Orca":
            if not target in ['3','GinHex','GH']:
                em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動中 魔法が使えない！")
                await ch.send(embed=em)
                return
        else:
            em = discord.Embed(description=f"{mob.name}のアンチマジックエリアが発動中 魔法が使えない！")
            await ch.send(embed=em)
            return
    if player.magic_class() == "Wolf":
        await magic_wolf.use_magic(user,ch,target)
    if player.magic_class() == "Armadillo":
        await magic_armadillo.use_magic(user,ch,target)
    if player.magic_class() == "Orca":
        await magic_orca.use_magic(user,ch,target)
