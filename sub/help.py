import difflib
import asyncio
from datetime import datetime,timezone,timedelta
import discord
JST = timezone(timedelta(hours=+9), 'JST')

async def send_em(ch, title, description, timestamp=False):
    embed=discord.Embed(title=title,description=description)
    if timestamp == True:
        embed.timestamp = datetime.now(JST)
    return await ch.send(embed=embed), embed
    


async def help(client, ch, user):
    embed = discord.Embed(
        title="BitRPBHelpURL",
        description=("各URLから公式ヘルプページにジャンプ出来ます。青字でないところはページが未完成です。"
            +"[BitRPG内の用語](https://github.com/Sakuraga200323/BitRPG/blob/master/help_page/1)BitRPG%E5%86%85%E3%81%AE%E7%94%A8%E8%AA%9E.md)"
            +"[各コマンドの使い方](https://github.com/Sakuraga200323/BitRPG/blob/master/help_page/2)%E5%90%84%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89%E3%81%AE%E4%BD%BF%E3%81%84%E6%96%B9.md)"
            +"戦闘システム"
            +"[アイテム](https://github.com/Sakuraga200323/BitRPG/blob/master/help_page/4)%E3%82%A2%E3%82%A4%E3%83%86%E3%83%A0.md)"
            +"魔法領域"
            +"未登録(要望があれば増えます)"
    )
    await ch.send(embed=embed)
