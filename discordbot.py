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
import sub.box
import sub.item

JST = timezone(timedelta(hours=+9), 'JST')

dsn = os.environ.get('DATABASE_URL')

class Postgres:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        psycopg2.extras.register_hstore(self.cur)

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


standard_set = "name,sex,id,lv,max_hp,now_hp,max_mp,now_mp,str,def,agi,stp,str_stp, def_stp, agi_stp,all_exp,now_exp,money,cbt_ch_id"
    
token = os.environ.get('TOKEN')
client = discord.Client()

admin_list = [
    715192735128092713,
    710207828303937626,
    548058577848238080,
]

clr_lv4 = [
    548058577848238080,
    561836530398789641
]

clr_lv5 = [
    715192735128092713,
    710207828303937626
]


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=f"起動中…"))
    pg = Postres(dsn)
    for ch_data in pg.fetchdict("select id from mob_tb;")[0]["id"]:
        if not client.get_channel(ch_data):
            pg.execute(f"delete from mob_tb where id = {ch_data}")
    NOW = datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S")
    MEM = psutil.virtual_memory().percent

    LOG_CHANNELS = [i for i in client.get_all_channels() if i.name == "bitrpg起動ログ"]
    desc = (
        f"\n+Prefix\n^^"
        + f"\n+UsingMemory\n{MEM}%"
       　+ f"\n+Server\n{len(client.guilds)}")

    print(f"【報告】起動完了。\n使用メモリー{MEM}%")

    loop.start()

    await client.change_presence(activity=discord.Game(name=f"^^help║Server：C║Mem：{MEM} %"))
    for ch in LOG_CHANNELS:
        try:
            embed = discord.Embed(
                title = "BitRPG起動ログ",
                description = f"```diff\n{desc}```")
            embed.timestamp = datetime.now(JST)
            await ch.send(embed = embed)
        except:
            print("Error")

@tasks.loop(seconds=10)
async def loop():
    MEM = psutil.virtual_memory().percent
    await client.change_presence(activity=discord.Game(name=f"開発作業中║Server：{len(client.guilds)}║Mem：{MEM} %"))


@client.event
async def on_guild_join(guild):
    log_ch = client.get_channel(752551728553132102)
    embed = discord.Embed(
        title="BitRPG導入ログ",
        description=f"{guild.name}({guild.id})が導入\n現在の導入数：{len(client.guilds)}"
    )
    embed.timestamp=datetime.now(JST)
    await log_ch.send(embed=embed)


@client.event
async def on_guild_remove(guild):
    log_ch = client.get_channel(752551728553132102)
    embed = discord.Embed(
        title="BitRPG撤去ログ",
        description=f"{guild.name}({guild.id})が撤去\n現在の導入数：{len(client.guilds)}"
    )
    embed.timestamp=datetime.now(JST)
    await log_ch.send(embed=embed)

@client.event
async def on_message(message):
    global cur, conn

    m_ctt = message.content
    m_em = message.embeds
    m_id = message.id
    m_ch = message.channel
    m_guild = message.guild
    m_author = message.author

    message_lock = asyncio.Lock()
    async with message_lock:
        if m_ctt.startswith("^^"):
            import sub.box
            if m_ch.id in sub.box.cmd_ch:
                await m_ch.send("【警告】処理が終了するまで待機してください。")
                return
            sub.box.cmd_ch.append(m_ch.id)
            pg = Postgres(dsn)
            id_list = [ i[0] for i in pg.fetch("select id from mob_tb;")]
            id = m_ch.id
            if not id_list or (not id in id_list):
                import sub.N_Mob
                mob_name = random.choice(list(sub.N_Mob.set.keys()))
                url = sub.N_Mob.set[mob_name]
                pg.execute(f"insert into mob_tb (name,id,lv,max_hp,now_hp,str,def,agi,img_url) values ('{mob_name}',{m_ch.id},1,10,10,10,10,10,'{url}');")
            id_list = [ i[0] for i in pg.fetch("select id from player_tb;")]
            id = m_author.id
            if not id_list or (not id in id_list):
                player_num = len(id_list)
                flag = False
                while flag == False:
                    name_flag = False
                    sex_flag = False
                    def check(m):
                        if not m.author.id == id:
                            return 0
                        return 1
                    while name_flag == False:
                        await m_ch.send(
                            f"{m_author.mention}さんの冒険者登録を開始。"
                            +"\n登録名を1分以内に送信してください。`next`と送信するか、1分経過すると、定型名で登録されます。\n"
                            +"`あとから設定し直すことが可能です。\n20文字以内。`"
                        )
                        try:
                            msg = await client.wait_for("message", timeout=60, check=check)
                        except asyncio.TimeoutError:
                            name = "Player" + str(player_num + 1)
                            await m_ch.send(f"1分経過。『{name}』で登録します。")
                            name_flag = True
                        else:
                            name = msg.content
                            if name == "next":
                                name = "Player" + str(player_num + 1)
                            else:
                                name_list = [ i[0] for i in pg.fetch("select name from player_tb;")]
                                if name_list and name in name_list:
                                    await m_ch.send(f"【警告】『{name}』は既に使用されています。")
                                    continue
                                if len(list(name)) > 20:
                                    await m_ch.send(f"【警告】『{name}』は20文字を{ len(list(name)) - 20}文字超過しています。20文字以内にしてください。")
                                    continue 
                                await m_ch.send(f"『{name}』で宜しいですか？\nyes -> y\nno -> n")
                                try:
                                    msg = await client.wait_for("message", timeout=10, check=check)
                                except asyncio.TimeoutError:
                                    name_flag = True
                                else:
                                    if not msg.content in ("y","Y","n","N"):
                                        await m_ch.send("【警告】y、nで答えてください。")
                                        continue
                                    if msg.content in ("y","Y"):
                                        await m_ch.send(f"『{name}』で登録します。")
                                        name_flag = True
                                    elif msg.content in ("n","N"):
                                        await m_ch.send(f"名前を登録し直します。")
                                        continue

                    while sex_flag == False:
                        await m_ch.send("\n該当する性別の番号を20秒以内に送信してください。\n男性 -> 0\n女性 -> 1\n無記入 -> 2\n`半角全角は問いません。`")
                        try:
                            msg2 = await client.wait_for("message", timeout=20, check=check)
                        except asyncio.TimeoutError:
                            sex = "無記入"
                        else:
                            sex = msg2.content
                            if not sex in ("0", "1", "１", "０", "2","２"):
                                await m_ch.send("0、1、2いずれかの番号を送信してください。")
                                continue
                            if sex in ("0", "０"):
                                sex = "男性"
                            if sex in ("1", "１"):
                                sex = "女性"
                            if sex in ("2", "２"):
                                sex = "無記入"
                        await m_ch.send(f"『{sex}』で宜しいですか？\nyes -> y\nno -> n")
                        try:
                            msg = await client.wait_for("message", timeout=10, check=check)
                        except asyncio.TimeoutError:
                            await m_ch.send(f"10秒経過。『{sex}』で登録します。")
                            sex_flag = True
                        else:
                            if not msg.content in ("y","Y","n","N"):
                                await m_ch.send("【警告】y、nで答えてください。")
                            if msg.content in ("y","Y"):
                                await m_ch.send(f"『{name}』で登録します。")
                                sex_flag = True
                            elif msg.content in ("n","N"):
                                await m_ch.send(f"性別を登録し直します。")
                                continue
                    embed = discord.Embed(color = discord.Color.green())
                    embed.add_field(name = "Name", value = name)
                    embed.add_field(name = "Sex", value = sex)
                    flag = True
                    await m_ch.send(embed=embed)
                    n = name
                    s = sex
                    jsonb_items = "'冒険者カード', 1, 'HP回復薬', 10, 'MP回復薬', 10, 'ドーピング薬', 1, '魔石', 1"
                    cmd = (
                        f"INSERT INTO player_tb VALUES ("
                        + f"'{n}', '{s}', {id}, 1, 10 ,10, 1, 1, 10, 10, 10, 0, 0, 0, 0, 0, 0, 0, NULL, jsonb_build_object({jsonb_items}, 0)"
                        +");"
                    )
                    print(cmd)
                    try:
                        pg.execute(cmd)
                    except Exception as e:
                        await m_ch.send('type:' + str(type(e))
                        + '\nargs:' + str(e.args)
                        + '\ne自身:' + str(e))
                    else:
                        embed = discord.Embed(
                            description=f"{name}は`冒険者カード×1`を獲得した。",
                            color=discord.Color.green())
                        embed.set_thumbnail(url="https://media.discordapp.net/attachments/719855399733428244/740870252945997925/3ff89628eced0385.gif")
                        await m_ch.send(content = "冒険者登録が完了しました。" , embed=embed) 

                    P_list = [ i for i in pg.fetch(f"select {standard_set} from player_tb where id = {m_author.id}")[0] ]
                    embed = discord.Embed(title = "Plyer Status Board")
                    embed.add_field(name = f"Player", value = f"{P_list[0]}({m_author.mention})", inline = False)
                    embed.add_field(name = f"Sex", value = f"{P_list[1]}", inline = False)
                    embed.add_field(name = f"Lv (Level)", value = f"*{P_list[3]}*")
                    embed.add_field(name = f"HP (HitPoint)", value = f"*{P_list[5]} / {P_list[4]}*")
                    embed.add_field(name = f"MP (MagicPoint)", value = f"*{P_list[7]} / {P_list[6]}*")
                    embed.add_field(name = f"STR (Strength)", value = f"*{P_list[8]}*\n`(+{P_list[12]})`")
                    embed.add_field(name = f"DEF (Defense)", value = f"*{P_list[9]}*\n`(+{P_list[13]})`")
                    embed.add_field(name = f"AGI (Agility)", value = f"*{P_list[10]}*\n`(+{P_list[14]})`")
                    embed.add_field(name = f"EXP (ExperiencePoint)", value = f"*{P_list[15]}*\n`[次のレベルまで後{P_list[3] - P_list[16]}]`")
                    embed.add_field(name = f"STP (StatusPoint)", value = f"*{P_list[11]}*\n`[+1point -> +1]`")
                    await m_ch.send(embed = embed)
                    embed = discord.Embed(title="ステータスの見方",description="基本的な使用方法を説明します")
                    embed.add_field(name = f"Player", value = f"貴方の名前", inline = False)
                    embed.add_field(name = f"Sex", value = f"貴方の性別", inline = False)
                    embed.add_field(name = f"Lv", value = f"*現在のLv*")
                    embed.add_field(name = f"HP", value = f"*現在のHP / 最高HP*")
                    embed.add_field(name = f"MP", value = f"*現在のMP / 最高MP*")
                    embed.add_field(name = f"STR", value = f"*攻撃力。強化による補正済みの値です。*\n`[強化量]`")
                    embed.add_field(name = f"DEF", value = f"*防御力。同様*\n`[強化量]`")
                    embed.add_field(name = f"AGI", value = f"*素早さ。同様*\n`[強化量]`")
                    embed.add_field(name = f"EXP", value = f"*獲得した総EXP*\n`[次のレベルまでの残り必要EXP]`")
                    embed.add_field(name = f"STP", value = f"*使用可能なPoint\n10LvUP毎に50獲得可能\n`[+1STP -> +1]`*\n")
                    await m_ch.send(embed=embed)

            else:

                # ステータスの表示 #
                if m_ctt in ("^^st","^^status"):
                    # ステータスの表示 #
                    result = pg.fetch(f"select {standard_set} from player_tb where id = {m_author.id};")
                    P_list = [ i for i in result[0] ]
                    embed = discord.Embed(title = "Plyer Status Board")
                    embed.add_field(name = f"Player", value = f"{P_list[0]}({m_author.mention})", inline = False)
                    embed.add_field(name = f"Sex", value = f"{P_list[1]}", inline = False)
                    embed.add_field(name = f"Lv (Level)", value = f"*{P_list[3]}*")
                    embed.add_field(name = f"HP (HitPoint)", value = f"*{P_list[5]} / {P_list[4]}*")
                    embed.add_field(name = f"MP (MagicPoint)", value = f"*{P_list[7]} / {P_list[6]}*")
                    embed.add_field(name = f"STR (Strength)", value = f"*{P_list[8]}*\n`(+{P_list[12]})`")
                    embed.add_field(name = f"DEF (Defense)", value = f"*{P_list[9]}*\n`(+{P_list[13]})`")
                    embed.add_field(name = f"AGI (Agility)", value = f"*{P_list[10]}*\n`(+{P_list[14]})`")
                    embed.add_field(name = f"EXP (ExperiencePoint)", value = f"*{P_list[15]}*\n`[次のレベルまで後{P_list[3] - P_list[16]}]`")
                    embed.add_field(name = f"STP (StatusPoint)", value = f"*{P_list[11]}*\n`[+1point -> +1]`")
                    embed.set_thumbnail(url=m_author.avatar_url)
                    await m_ch.send(embed = embed)


                # 戦闘 #
                if m_ctt.startswith("^^attack") or m_ctt.startswith("^^atk"):
                    temp = m_ctt
                    pattern = r"(\^\^atk|\^\^attack|\^\^atk (.+)|\^\^attack (.+))$"
                    result = re.search(pattern, temp)
                    if result:
                        import sub.battle
                        sub.battle.cbt_proc(m_author,m_ch)


                # 戦闘から離脱 #
                if m_ctt.startswith("^^re"):
                    temp = m_ctt.split("^^")[1]
                    pattern = r"(re|reset|reset (.+)|re (.+))$"
                    result = re.search(pattern, temp)
                    if result:
                        import sub.battle
                        sub.battle.reset(m_author, m_ch)


                # STPの振り分け #
                if m_ctt.startswith("^^point"):
                    pattern = r"^\^\^point (str|STR|def|DEF|agi|AGI) (\d{1,})$"
                    result = re.search(pattern, m_ctt)
                    if result:
                        import sub.stp
                        sub.stp.divid(m_author, m_ch, result)


                # チャンネルレベルランキングの表示 #
                if m_ctt == "^^rank m":
                    import sub.rank
                    rank = sub.rank.RankClass(client)
                    rank.channel(m_author,m_ch)


                if m_ctt.startswith("^^item"):
                    if m_ctt == "^^item":
                        sub.item.open(client, m_ch, m_author)
                    if m_ctt.startswith("^^item "):
                        sub.item.use(client, m_ch, m_author, m_ctt.split("^^item ")[1])
                
            if  m_ch.id in sub.box.cmd_ch:
                sub.box.cmd_ch.remove(m_ch.id)



    if m_ctt.startswith("SystemCall"):
        m_ctt = m_ctt.split("SystemCall")[1].strip("\n")
        await m_ch.send("** 【警告】プロトコル[SystemCall]の実行にはLv4以上のクリアランスが必要です。\nクリアランスLv4未満のユーザーの不正接続を確認次第、即座に対象のデータを終了します。**")
        if not m_author.id in clr_lv4 and not m_author.id in clr_lv5 :
            await m_ch.send("**貴方のクリアランスはLv4未満です。プロトコル[SystemCall]の実行にはLv4以上のクリアランスが必要です。**")
            return
        else:
            if m_author.id in clr_lv4:
                c_lv = 4
            elif m_author.id in clr_lv5:
                c_lv = 5
            await m_ch.send(f"**Lv{c_lv}クリアランスを認証。プロトコル[SystemCall]を実行します。**")
        if m_ctt.startswith("^^psql "):
            cmd = m_ctt.split("^^psql ")[1]
            pg = Postgres(dsn)
            await m_ch.send(f"`::DATABASE=> {cmd}`")
            if "select" in cmd:
                result = pg.fetch(cmd)
                await m_ch.send(result)
            else:
                pg.execute(cmd)
        if m_ctt.startswith("reverse"):
            sub.box.cmd_ch.remove(m_ch.id)


        await m_ch.send("**すべての処理完了。プロトコル[SystemCall]を終了します。**")

def get_ch(id):
    ch = client.get_channel(id)
    return ch

        
'''
update テーブル名 set 列名 = 値, 列名 = 値, ...
where 列名 = 値;
select 列名 from テーブル名
where 列名 = 値;
'''


client.run(token)
