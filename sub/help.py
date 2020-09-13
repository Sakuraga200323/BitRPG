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
    

def inverse_lookup(d, x):
    for k,v in d.items():
        if x == v:
            return k

async def help(client, ch, user):
    sended_em = await send_em(
        ch=ch,
        title="BitRPG Help Bord",
        description="BitRPGに存在するコマンドや用語の解説をみることができます。以下から選び、同チャンネルに送信してください。\n`help, status, attack, result, item, point, rank, str, def, agi, stp, exp, player, mob, money`\nまた、`all`と送信すると、全ての解説を一気に表示することが出来ます。"
    )
    target_list = ["help","status","attack","reset","item","point","rank","str","def","agi", "exp", "player", "mob", "stp", "money"]
    def check(m):
        if m.author.id != user.id:
            return 0
        if m.channel.id != ch.id:
            return 0
        return 1
    try:
        remsg = await client.wait_for("message", timeout=20, check=check)
    except asyncio.TimeoutError:
        await ch.send("20秒経過、受付を終了します。")
        sended_em[1].set_footer(text="処理終了済み")
        await sended_em[0].edit(embed=sended_em[1])
    else:
        target = remsg.content
        if not target in target_list:
            rate_result = {}
            for i in target_list:
                rate = difflib.SequenceMatcher(None, target, i).ratio()
                rate_result[i] = rate
            yosou = inverse_lookup(rate_result, max(list(rate_result.values())))
            yosou_msg = ""
            if max(list(rate_result.values())) >= 0.5:
                yosou_msg = "\n※独断と勝手な偏見で予想しましたが、もしかして探しているのは`{yosou}`ではないですか？"
            await ch.send(f"`{target}`はHelpに登録されていません。コマンドの場合は省略形で入れている可能性があります。原形で探してみてください。{yosou_msg}")
            return
        
         
        