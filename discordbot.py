import discord
import asyncio
import random
import os
import re
import ast
# import psutil
import traceback
from datetime import datetime, timedelta, timezone
JST = timezone(timedelta(hours=+9), 'JST')
TOKEN = os.environ['TOKEN']
client = discord.Client()

def randint(a,b):
    return random.randint(a,b)

class StatusCorr:
    max_dmg_corr = 10
    min_dmg_corr = 15

    def dmg_corr(self):
        return random.randint(self.max_dmg_corr, self.min_dmg_corr)


status_set = StatusCorr()

corr_path = "data/correction_value/dmg_corr.txt"
with open(corr_path,mode="r") as f:
    dmg_corr_nums = f.readlines()

status_set.max_dmg_corr = dmg_corr_nums[0]
status_set.min_dmg_corr = dmg_corr_nums[1]


@client.event
async def on_ready():
    NOW = datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S")
    # MEM = psutil.virtual_memory().percent
    LOG_CHANNELS = [i for i in client.get_all_channels() if i.name == "bit起動ログ"]
    desc = (f"\n+Bot\n{client.user}"
        + f"\n+BotID\n{client.user.id}"
        + f"\n+Prefix\n^^"
        # + f"\n+UseingMemory\n{MEM}%"
    )
    for ch in LOG_CHANNELS:
        try:
            embed = discord.Embed(
                title = "BitRPG起動ログ",
                description = f"```diff\n{desc}```")
            embed.timestamp = datetime.now(JST)
        except:
            print("Error")
    print(desc)

    path = f"data/playerdata/log/startup/{NOW}txt"
    with open(path,mode="w") as f:
        f.write(f"startup\n{datetime.now(JST)}")

@client.event
async def on_message(message):

    m_ctt = message.content
    m_em = message.embeds
    m_id = message.id
    m_ch = message.channel
    m_guild = message.guild
    m_author = message.author

    path = f"data/playerdata/{m_author.id}_data.txt"
    flag_path = f"data/playerdata/{m_author.id}_flag.txt"
    path2 = f"data/channeldata/{m_ch.id}_data.txt"
    flag_path2 = f"data/channeldata/{m_ch.id}_flag.txt"


    if m_ctt.startswith("^^reset"):
        if os.path.exists(path):

            with open(path, mode="r") as f:
                P_list = f.readlines()

        elif not os.path.exists(path):

            with open(path, mode="w") as file:
                file.write("1\n100\n100\n10\n10\n10\n0\n0\n0\n0\n0")
                P_list = [1, 100, 100, 10, 10, 10, 0]

        with open(path, mode="w") as f:
            P_list[2] = P_list[1]
            f.writelines([ str(i) for i in P_list])


        if os.path.exists(path2):

            with open(path, mode="r") as f:
                M_list = f.readlines()

        elif not os.path.exists(path2):

            with open(path2, mode="w") as file:
                file.write("1\n100\n100\n10\n10\n10\n0\n0\n0\n0\n0")
                P_list = [1, 100, 100, 10, 10, 10, 0]

        with open(path2, mode="w") as f:
            M_list[2] = M_list[1]
            f.writelines([str(i) for i in M_list])



    if m_ctt.startswith("^^attack"):
        print("〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓〓")
        msg = ""
        embed = None

        dmg_corr = randint(4,6)

        print("-> PlayerData")

        if os.path.exists(path):
            print(f"found player:{m_author}║{m_author.id}")

            with open(path, mode="r") as f:
                P = f.readlines()
                p_list = [int(i.strip()) for i in P]

        elif not os.path.exists(path):

            print(f"didn't find player:{m_author}║{m_author.id}")
            with open(path, mode="w") as file:
                file.write("1\n100\n100\n10\n10\n10\n0\n0\n0\n0\n0")
                p_list = [1, 100, 100, 10, 10, 10, 0]

        print(f"PlayerData\n {p_list}")
        print("\n")


        print("-> ChannelData")

        if not os.path.exists(path2):
            print(f"didn't find channel:{m_ch.name}║{m_ch.id}")

            with open(path2, mode="w") as file:
                file.write("1\n100\n100\n10\n10\n10")
                m_list = [1, 100, 100, 10, 10, 10]

        elif os.path.exists(path2):
            print(f"found channel:{m_ch.name}║{m_ch.id}")

            with open(path2, mode="r") as file:
                M = file.readlines()
                m_list = [ int(i.strip()) for i in M ]


        print(f"ChannelData\n {m_list}")
        print("\n")

        be_moblv = m_list[0]

        # プレイヤーのHPが0だったらreturn
        if p_list[2] <= 0:
            await message.channel.send(f"{m_author.name}はもう死んでるよ")
            return

        p_atk1 = p_list[3] * (randint(8,11) / 10)
        p_atk2 = p_list[3] * (randint(8,11) / 10)
        print(f"PlayerAtk:{p_atk1}, {p_atk2}")

        p_def1 = p_list[4] * (randint(8,11) / 10)
        p_def2 = p_list[4] * (randint(8,11) / 10)
        print(f"PlayerDef:{p_def1}, {p_def2}")

        m_atk1 = m_list[3] * (randint(8,11) / 10)
        m_atk2 = m_list[3] * (randint(8,11) / 10)
        print(f"MobAtk:{m_atk1}, {m_atk2}")

        m_def1 = m_list[4] * (randint(8,11) / 10)
        m_def2 = m_list[4] * (randint(8,11) / 10)
        print(f"MobDef:{m_def1}, {m_def2}")

        A = randint(10,15)
        B = randint(10,15)
        dmg1 = int((p_atk1*p_list[0] / m_def1)*A) # プレイヤーが与えるダメージ
        dmg2 = int((m_atk2*m_list[0] / p_def2)*B) # モンスターが与えるダメージ

        # ダメージ量が0未満になったときに強制的に0に
        if dmg1 < 0:
            dmg1 = 0

        if dmg2 < 0:
            dmg2 = 0

        print(f"dmg1:{dmg1}\ncorr:×{A}")
        print(f"dmg2:{dmg2}\ncorr:×{B}")
        print("\n")

        # プレイヤーが先手を取る時
        if p_list[5] >= m_list[5]:
            print(f"p(AGI):{p_list[5]}\nm(AGI):{m_list[5]}")
            m_list[2] -= dmg1
            print(f"m(HP):{m_list[2]}/{m_list[1]}")
            msg = msg + ("```diff\n"
                + f"+ {m_author.name}の攻撃！\n"
                + f"+ Lv{m_list[0]}の敵に{dmg1}のダメージ！\n"
                + f" 敵[{m_list[2]}/{m_list[1]}]"
                + "```")

            # モンスターのHPが残っている時
            if m_list[2] > 0:
                p_list[2] -= dmg2
                msg = msg + ("```diff\n"
                    + f"- Lv{m_list[0]}の敵の攻撃！\n"
                    + f"- {m_author.name}に{dmg2}のダメージ！\n"
                    + f" {m_author.name}[{p_list[2]}/{p_list[1]}]"
                    + "```")

                # モンスターの後手でプレイヤーのHPが0以下に成った時
                if p_list[2] <= 0:
                    msg = msg + (f"```ini\n[{m_author.name}はやられてしまった]```")

            # モンスターのHPが残っていない時
            elif m_list[2] <= 0:
                desc = (
                    f"Lv{m_list[0]}の敵を倒した。\n"
                    +f"{m_author.mention}は{m_list[0]}のExpを獲得した。")
                m_list[0] += 1
                m_list[2] = int(100 * (1 + ((m_list[0] -1)/10)))
                p_list[6] += m_list[0]
                be_lv = p_list[0]
                while p_list[6] >= p_list[0]:
                    p_list[6] -= p_list[0]
                    p_list[0] += 1
                p_list[3] = int(10 * (1 + ((p_list[0] -1)/10)))
                p_list[4] = int(10 * (1 + ((p_list[0] -1)/10)))
                p_list[5] = int(10 * (1 + ((p_list[0] -1)/10)))
                p_list[1] = int(100 * (1 + ((p_list[0] -1)/10)))
                p_list[2] = p_list[1]
                if p_list[0] > be_lv:
                    desc = desc + (f"\n{m_author.mention}はレベルアップ`{be_lv}->{p_list[0]}`")

                embed = discord.Embed(
                    title = "Result",
                    description = desc,
                )

        # モンスターが先手を取る時
        elif p_list[5] < m_list[5]:
            print(f"p(AGI):{p_list[5]}\nm(AGI):{m_list[5]}")
            p_list[2] -= dmg2
            print(f"p(HP):{p_list[2]}/{p_list[1]}")
            msg = msg + ("```diff\n"
                + f"- Lv{m_list[0]}の敵の攻撃！\n"
                + f"- {m_author.name}に{dmg2}のダメージ！\n"
                + f" {m_author.name}[{p_list[2]}/{p_list[1]}]"
                + "```")

            # プレイヤーのHPが残っている時
            if p_list[2] > 0:
                m_list[2] -= dmg1
                msg = msg + ("```diff\n"
                    + f"+ {m_author.name}の攻撃！\n"
                    + f"+ Lv{m_list[0]}の敵に{dmg1}のダメージ！\n"
                    + f" 敵[{m_list[2]}/{m_list[1]}]"
                    + "```")

                # プレイヤーの後手でモンスターのHPが0以下に成った時
                if m_list[2] <= 0:
                    desc = (
                        f"Lv{m_list[0]}の敵を倒した。\n"
                        +f"{m_author.mention}は{m_list[0]}のExpを獲得した。")
                    m_list[0] += 1
                    m_list[2] = int(100 * (1 + ((m_list[0] -1)/10)))
                    p_list[6] += m_list[0]
                    be_lv = p_list[0]
                    while p_list[6] >= p_list[0]:
                        p_list[6] -= p_list[0]
                        p_list[0] += 1
                    p_list[3] = int(10 * (1 + ((p_list[0] -1)/10)))
                    p_list[4] = int(10 * (1 + ((p_list[0] -1)/10)))
                    p_list[5] = int(10 * (1 + ((p_list[0] -1)/10)))
                    p_list[1] = int(100 * (1 + ((p_list[0] -1)/10)))
                    p_list[2] = p_list[1]
                    if p_list[0] > be_lv:
                        desc = desc + (f"{m_author.mention}はレベルアップ`{be_lv}->{p_list[0]}`")

                    embed = discord.Embed(
                        title = "Result",
                        description = desc,
                    )
            # プレイヤーのHPが残ってない時
            elif p_list[2] <= 0:
                msg = msg + (f"```ini\n[{m_author.name}はやられてしまった]```")

        await message.channel.send(content = msg, embed = embed)

        m_list[3] = int(10 * (1 + ((m_list[0] -1)/10)))
        m_list[4] = int(10 * (1 + ((m_list[0] -1)/10)))
        m_list[5] = int(10 * (1 + ((m_list[0] -1)/10)))
        m_list[1] = int(100 * (1 + ((m_list[0] -1)/10)))


        if be_moblv < m_list[0]:
            img_path = "/Users/furuno/Desktop/DiscordBots/BitRPGbot/data/imgurl.txt"
            with open(img_path,mode="r") as f:
                url = random.choice(f.readlines())
            embed = discord.Embed(
                title = f"敵が出現！",
                description = f"Lv.{m_list[0]}｜HP.{m_list[2]}/{m_list[1]}",
                color = discord.Color.blue())
            embed.set_image(url = url)
            await m_ch.send(embed = embed)


        with open(path, mode="w") as f:
            L_P = [str(i) + "\n" for i in p_list]
            print(L_P)
            f.writelines(L_P)

        with open(path2, mode="w") as f:
            L_M = [str(i) + "\n" for i in m_list]
            print(L_M)
            f.writelines(L_M)

        with open(path, mode="r") as f:
            p = f.readlines()
            print([int(i) for i in p])

        with open(path2, mode="r") as f:
            m = f.readlines()
            print([int(i) for i in m])


client.run(TOKEN)
