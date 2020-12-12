import math
import ast
import asyncio
from datetime import datetime, timedelta, timezone
import discord
from discord.ext import tasks
import glob
import os
import psutil
import psycopg2
import psycopg2.extras
import random
import re
import traceback
from sub import box, calc, avatar, status


JST = timezone(timedelta(hours=+9), 'JST')
dsn = os.environ.get('DATABASE_URL')


token = os.environ.get('TOKEN')

admin_list = [
    715192735128092713,
    710207828303937626,
    548058577848238080,
]


item_emoji = {
    1:"<:card:786514637289947176>",
    2:"<:hp_potion:786236538584694815>",
    3:"<:mp_potion:786236615575339029>",
    4:"<:soul_fire:786513145010454538>",
    5:"<:toishi:786513144691556364>",
    6:"<:maseki:785641515561123921>",
    7:"<:masuisyou:786516036673470504>",
    8:"<:magic_coin:786513121236746260>",
}

item_emoji_a = {
    1:"<:card:786514637289947176>",
    2:"<a:hp_potion_a:786982694479200336>",
    3:"<a:mp_potion_a:786982694839124021>",
    4:"<:soul_fire:786513145010454538>",
    5:"<a:toishi_a:786974865777229864>",
    6:"<:maseki:785641515561123921>",
    7:"<a:masuisyou_a:786982694948306974>",
    8:"<a:magic_coin_a:786966211594289153>"
}

getmagic_list = [
    "001|Heal",
    "002|FireBall",
    "003|StrRein",
    "004|DefRein",
    "005|AgiRein",
    "006|LifeConversion"
]

pg = None

async def cbt_proc(client, user, ch):
    if not user.id in box.players:
        print("box.playersに存在しないPlayer.idを取得")
        if not user.id in [i["id"] for i in pg.fetchdict(f"select id from player_tb;")]:
            box.players[user.id] = avatar.Player(client, user.id)
            print(f"Playerデータ挿入(battle.py->cbt_proc)： {box.players[user.id].user}")
    player,mob = box.players[user.id],box.mobs[ch.id]
    if not player.battle_start(ch.id):
        channel = client.get_channel(player.battle_ch)
        if channel:
            await ch.send(f"<@{user.id}> は現在『<@{channel.id}>』で戦闘中です。")
            return
        await ch.send(f"<@{user.id}> が認識できないチャンネルで戦闘中。データの上書きを行ないます。")
        player.battle_end()
        if player.battle_start(ch.id):
            await ch.send(f"上書き完了")
        else:
            await ch.send(f"上書き失敗、戦闘に参加できていません。")
            return

    if player.now_hp <= 0:
        await ch.send(f"<@{user.id}> は既に死亡しています。")
        return
    mob.player_join(user.id)

    # モンスターとの戦闘で使うダメージ、運の計算およびログの設定 #
    dmg1,dmg2 = calc.dmg(player.STR(), mob.defe()),calc.dmg(mob.str(), player.DEFE())
    dmg2 = int(dmg2*1.45) if mob.name=="古月" else dmg2
    log1_1 = log2_1 = ""

    # HPゲージの作成
    def hp_gauge(now, max):
        return  "-"*20 if now<=0 else (int((now/max)*20)*"/")+((20-int((now/max)*20))*" ")

    a,b = random.random(),random.random()
    t,x = ("極",5) if a>=0.95 else ("超",2) if a>=0.9 else ("強",1.5) if a>=0.85 else ("",1)
    t2,x2 = ("極",5) if b>=0.95 else ("超",2) if b>=0.9 else ("強",1.5) if b>=0.85 else ("",1)
    t += "ダメージ！"
    t2 += "ダメージ！"

    # 戦闘処理（Player先手） #
    if player.AGI() >= mob.agi():
        log1_1 += f'+ {player.user}の攻撃->'
        dmg1 = round(x * dmg1)
        log1_1 += f"{str(dmg1)}の{t}" if dmg1!=0 else "しかし当たらなかった…"
        log1_1 += f'\n{mob.name} のHP[{mob.cut_hp(dmg1)}/{mob.max_hp}]\n[{hp_gauge(mob.now_hp, mob.max_hp)}]
        log2_1 += f'{mob.name}を倒した！！' if mob.now_hp<=0 else f'- {mob.name}の攻撃->'
        if not mob.now_hp <= 0:
            dmg2 = round(x2 * dmg2)
            log2_1 += f"{str(dmg2)}の{t2}" if dmg2!=0 else "しかし当たらなかった…"
            log2_1 += f'\n{user} のHP[{player.cut_hp(dmg2)}/{player.max_hp}]\n[{hp_gauge(player.now_hp, player.max_hp)}]'

    # 戦闘処理（Player後手） #
    else:
        log1_1 += f'- {mob.name}の攻撃->'
        dmg2 = round(x * dmg2)
        log1_1 += f"{str(dmg2)}の{t}" if dmg1!=0 else "しかし当たらなかった…"
        log1_1 += f'\n{user}のHP[{player.cut_hp(dmg2)}/{player.max_hp}]\n[{hp_gauge(player.now_hp, player.max_hp)}]
        log2_1 += f'{user}はやられてしまった！！' if player.now_hp<=0 else f'- {user}の攻撃->'
        if not player.now_hp<=0
            dmg1 = round(x2 * dmg1)
            if not player.now_hp <= 0:
            log2_1 += f"{str(dmg1)}の{t2}" if dmg1!=0 else "しかし当たらなかった…"
            log2_1 += f'\n{mob.name}のHP[{mob.cut_hp(dmg1)}/{mob.max_hp}]\n[{hp_gauge(mob.now_hp, mob.max_hp)}]'

    battle_log = f"```diff\n{log1_1}``````diff\n{log2_1}```"


    # バフのターンとかの確認 #
    #buff_text = ""
    #if user.id in buff.doping:  # ドーピング薬
    #    buff.doping[user.id][0] -= 1
    #    if buff.doping[user.id][0] <= 0:
    #        p_data["now_hp"] -= buff.doping[user.id][1]
    #        buff_text += f"- {p_data['name']} はドーピング薬の反動を受けた！{buff.doping[user.id][1]}のダメージ!\n"
    #        buff_text += f"{p_data['name']} のHP[{p_data['now_hp']}/{p_data['max_hp']}]"
    #        buff_log = f"```diff\n{buff_text}```"
    #        battle_log += buff_log
    #         del buff.doping[user.id]


    embed = em = item_em = spawn_embed = None

    if mob.now_hp <= 0:
        desc = ""
        now = datetime.now(JST).strftime("%H:%M")
        if  now in ['23:18']:
            get_exp *= 16
            await ch.send("????『幸運を。死したものより祝福を。』")
        exp, money = mob.exp()
        money = int(money/len(mob.battle_players))
        print("戦闘参加しているPlayer: ",mob.battle_players)
        for p_id in mob.battle_players:
            p = box.players[p_id]
            up_exp, up_lv = p.get_exp(exp)
            p.kill_count(1)
            p.money(money)
            desc += f"<@{p_id}> 経験値+{exp} "
            desc += f"お金+{money} "
            if up_lv > 0: desc += f"\nLvUP {p.lv()-up_lv} -> {p.lv()}"
            desc += "\nドロップアイテム： "
            def get_item_sub(c=client, u=user, item_id, item_num):
                status.get_item(c, u, item_id, item_num)
                desc += f"{item_emoji_a[item_id]}×{item_num} "
            if random.random() <= 0.05:
                # HPポーション
                item_id,item_num = 2,random.randint(3, 6)
                get_item_sub(item_id, item_num)
            if random.random() <= 0.05:
                # MPポーション
                item_id,item_num = 3,random.randint(3, 6)
                get_item_sub(item_id, item_num)
            if True:
                # 魂の焔
                item_id,item_num = 4,1
                get_item_sub(item_id, item_num)
            if random.random() <= 0.5 and mob.name in ("Golem",):
                # 砥石
                item_id,item_num = 5,random.randint(1, 2)
                get_item_sub(item_id, item_num)
            if random.random() <= 0.03:
                # 魔石
                item_id,item_num = 6,random.randint(3, 6)
                get_item_sub(item_id, item_num)
        if random.random() <= 0.01:
            player.now_stp(mob.lv())
            em = discord.Embed(description=f"<@{user.id}> は{mob.lv()}のSTPを獲得した！")
        embed = discord.Embed(title="Result",description=desc,color=discord.Color.green())
        mob.lv(1)
        spawn_embed = mob.battle_end()
    
    await ch.send(content=battle_log,embed = embed)
    if em: await ch.send(embed=em)
    if item_em: await ch.send(embed=item_em)
    if spawn_embed: await ch.send(embed=spawn_embed)

        
# 戦闘から離脱 #
async def reset(client, user, ch):
    if not user or not ch:
        await ch.send("プレイヤーもしくはチャンネルが見つかりません。")
        rerturn
    if not user.id in box.players:
        box.players[user.id] = avatar.Player(client, user.id)
        print(f"Playerデータ挿入： {box.players[user.id].user}")
        return
    player,mob = box.players[user.id],box.mobs[ch.id]
    if not player.battle_ch:
        player.now_hp = player.max_hp
        await ch.send(f"HPを全回復しました。")
        return
    now_ch = client.get_channel(player.battle_ch)
    if player.battle_ch != ch.id:
        await ch.send(f"<@{player.user.id}> は『<@{now_ch.id}>』で戦闘中です。")
        return
    mob.battle_end()
    await ch.send(embed = mob.spawn())
                    
