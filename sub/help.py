import difflib
import asyncio
from datetime import datetime,timezone,timedelta
import discord
JST = timezone(timedelta(hours=+9), 'JST')
client = None

async def send_em(ch, title, description, timestamp=False):
    embed=discord.Embed(title=title,description=description)
    if timestamp == True:
        embed.timestamp = datetime.now(JST)
    return await ch.send(embed=embed), embed


cmd_em_list = []
cmd_info = (
    ('^^attack','Mobに攻撃 PlayerとMobのAgility(AGI)を比較して先手を決める\n`^^atk`と省略可'),
    ('^^magic','''`^^magic`┃現在の魔法一覧表示
`^^magic 魔法名`┃指定魔法使用
`^^magic 魔法番号`┃指定魔法使用
魔法名や魔法番号は^^magicで確認
全て`^^m`と省略可'''),
    ('^^reset','戦闘に参加しているPlayerを全員強制的に離脱 Mobは強制的に変わるので注意\n`^^re`と省略可'),
    ('^^item','''`^^item`┃所持Item確認
`^^inventory`┃所持Item確認
`^^item アイテム名`┃指定Item使用
全て`^^i`と省略可'''),
    ('^^shop','Mobが落とすお金(Cell)を消費してItemの購入・合成を行う'),
    ('^^pouch','''Itemのショートカットを作成(Max３個)
`^^item`ではItem名で指定が必須だが Pouchなら３個まで番号指定が可能
`^^pouch`┃設定済みItemを確認
`^^pouch 番号`┃指定番号(1~3)にセットされたItemを使用
`^^pouch 番号 アイテム名`┃指定番号にItemをセット
全て`^^p`と省略可'''),
    ('^^status','PlayerのStatus表示\n`^^st`と省略可'),
    ('^^rank','ランキング表示'),
    ('^^point','''StatusPointの振り分け
`^^point 強化対象 強化量`┃指定Statusを強化 強化対象はstr def agi のみ StatusPoint(STP)を消費'''),
    ('^^training','初心者向け Mobと戦わずにクイズでExpを獲得\n`^^tr`と省略可'),
)


async def help(user,ch):
    global cmd_info
    text = '`0 .┃Helpページの処理を終了`\n'
    cmd_info = sorted(cmd_info, key = lambda x:x[0])
    for i in cmd_info:
        em = discord.Embed(title=i[0],description=i[1])
        cmd_em_list.append(em) 
    for i,j in zip(cmd_info,range(1,len(cmd_em_list)+1)):
        text += f'`{j:<2}.┃{i[0]}`\n'
    help_em = discord.Embed(
        title='Command Help',
        description=('対応する番号を送信してください\n'+text))
    await ch.send(embed=help_em)
    def check(m):
        if m.author.id != user.id:return 0
        if m.channel.id != ch.id:return 0
        return 1
    help_flag = True
    while help_flag == True:
        try:
            respons = await client.wait_for('message',timeout=20,check=check)
            respons_num = int(respons.content)
        except asyncio.TimeoutError:
            em = discord.Embed(description='時間切れです')
            await ch.send(embed=em)
            help_flag = False
        else:
            if respons_num in range(1,len(cmd_em_list)+1):
                await ch.send(embed=cmd_em_list[respons_num-1])
            if respons_num == 0:
                em = discord.Embed(description='処理を終了しました')
                await ch.send(embed=em)
                help_flag = False
            
