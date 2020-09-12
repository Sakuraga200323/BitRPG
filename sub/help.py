import difflib
import asyncio
from datetime import datetime,timezone,timedelta
import discord
JST = timezone(timedelta(hours=+9), 'JST')

async def send_em(ch, title, description, timestamp=False):
    embed=discord.Embed(title=title,description=description)
    if timestamp == True:
        embed.timestamp = datetime.now(JST)
    returnawait ch.send(embed=embed)
    

def inverse_lookup(d, x):
    for k,v in d.items():
        if x == v:
            return k

async def help(client, ch, user):
    sended_em = await send_em(
        ch=ch,
        title="BitRPG Help Bord",
        description="BitRPGに存在するコマンドや用語の解説をみることができます。以下から選び、同チャンネルに送信してください。また、`all`と送信すると、全ての解説を一気に表示することが出来ます。\n`help, status, attack, result, item, point, rank, str, def, agi, stp, exp, player, mob, money`"
    )
    target_list = ["help","status","attack","reset","item","point","rank","str","def","agi", "exp", "player", "mob", "stp", "money"]
    def check(msg):
        if msg.author.id != user.id:
            return
        if msg.channel.id != ch.id:
            return
    try:
        remsg = await client.wait_for("message", timeout=20, check=check)
    except asyncio.TimeoutError:
        await ch.send("20秒経過、受付を終了します。")
        sended_em.set_author(text="処理終了済み")
    else:
        target = remsg.content
        if not target in target_list:
            rate_result = {}
            for i in target_list:
                rate = difflib.SequenceMatcher(None, target, i).ratio()
                rate_result[i] = rate
            print(rate_result)
            yosou = inverse_lookup(rate_result, list(rate_result.values()))
            await ch.send(f"{target}はHelpに登録されていません。コマンドの場合は省略形で入れている可能性があります。原形で探してみてください。\n`help, status, attack, result, item, point, rank, str, def, agi, stp, exp, player, mob, money`\n※独断と勝手な偏見で予想しましたが、もしかして探しているのは`{yosou}`ではないですか？")
            return
        
         
        
