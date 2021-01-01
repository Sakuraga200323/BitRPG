import random
import discord
client = None
normal = {
'西表猫娘':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2015/07/136a7883e32cc95a7e38f6208e750f09.png',
'死ノ草':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2011/03/toubyo_1.png',
'バニーウィッチ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/10/2fcb790238f2dbd181836bc11436be85.png',
'白兎':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/10/d36583829d974b8d432b6fd0a7c0b828.png',
'黒兎':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/10/9c16d386f8183f2cedff86261577cb64.png',
'シャドウ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/12/93df8db1f2c031cd4ae314be6c768b6a.png',
'ファントム':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/12/811239edbe34099b17c4f233974cd92f.png',
'ネクロマンサー':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/01/a793f38be632f4b3bc001c69a3ae0ec8.png',
'グール':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/06/%E3%82%B0%E3%83%BC%E3%83%AB.png',
'ブッシュ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/12/8d30d6dce9fee3435990e649cceaf507.png',
'スライム':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/05/fc1677e1f8efb82042659c49edeb48a9.png',
'格闘家':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/03/6d21225503049c00ff05f03f343af506.png',
'拳闘士':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/02/67e38db69797db556fcdffe661c1d919.png',
'ミクロラプトル・グイ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/07/ef4df1e60bb57ce43926148883335e35.png',
'アマビエ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/03/b23125c46c37fecb018cfa25121d4094.png',
'寿':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/11/cf426c2f7fa97af5034449c1ba215f3d.png',
'カシュデヤン':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/12/0bba5b1b0cfa668c3740958a2409a0b9.png',
'ブラッドレター':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/07/67ddd0f3ff7897f3ab8ef3794f3cc419.png',
'巫女':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2018/07/a75449c0147f290aca40d41f83086acd.png',
'マンイーター':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/05/f9c816958e6690e7101db7fe74e2ccdd.png',
'マンイーター':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/05/ddf3ee8b035b17536aff1cddf930c63f.png',
'モノリス':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/06/4dba7cfcaa3ba06799f8eab9bfb7674c.png',
'けりゅべりょしゅ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/09/6825f9ab92d3dc92903b8d9cad0b01e3.png',
'スライム':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/05/be3b72818def225b308358cad1bc7de1.png',
'ヤバイエイ':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2011/04/Cthylla_2.png',
'ヤバイイカ':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2011/04/Cthylla_1.png',
'ハーピィ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/05/5898684b5efafe8e5d6e7dbb4f412f06.png',
'女戦士':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2018/06/6a20182725ab8a3fdeceb14b452bb44f.png',
'女戦士':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2018/06/9101751550bbbbae4878a004e2022460.png',
'スプリガン':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2016/08/a705c64f123ea0621f687f2d77fca782.png',
'ドワーフ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/08/90a640ca37cff2b8acd41fd0b78e92df.png',
'大地の精霊':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/07/410bea672cb680e671eec8f6c76e1c09.png',
'森の精霊':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/06/f8424ad1e7fb5a361a299709efdae9d7.png',
'火の精霊':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/06/3a76d6930d86df706d47cdfcd3b03596.png',
'雷の精霊':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/06/4b5d5fb3c4569234ddb2657438a74271.png',
'ガーゴイル':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/06/63e8fef26f6dc883380f7ca1876b127f.png',
'天使':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2011/07/angel_11.png',
'黒塚':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2011/04/kurotsuka_1.png',
'ドラゴノイド':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2011/03/dragonoid_r.png',
'騎士':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2010/12/armor_b.png',
'ミートホープ':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2010/12/kotori.png'
}

elite = {
'侵略-聖母マリア':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/06/e181b8bc72c5ae7d98541fc9b10370b9.png',
'ダークグール':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/06/%E3%82%B0%E3%83%BC%E3%83%AB_2.png',
'ヴァルキリー':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/12/497ee39d4e650c5d5e4033c677c7926a.png',
'レインボースライム':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/05/c211c0e4782fdef1fb6a9014ce9e31af.png',
'オークライダー':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/10/f24cb922ca3de847ddb2a8a5ba5ccd4e.png',
'龍格闘家-龍姫':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/03/a77c93f5b8cb49ca86b756b02a7342ff.png',
'水神-アマビエ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/03/b23125c46c37fecb018cfa25121d4094.png',
'ラミエル':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/06/8e13afa0e6256e72d755c60d0afe4bb4.png',
'ラミエル':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/06/8e704e898fd57a2f6ce0e0aa86de9c3b.png',
'武装-ケルベロス':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/09/b7c16922da9de6556c2a80d7316687ab.png',
'三女神ノ一柱':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/12/9962b8759ce0db9f2288dce709d6d62e.png',
'三女神ノ一柱':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/12/2b6756d998233192a490ab0bf87f391a.png',
'三女神ノ一柱':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/12/bcd1c21445c0f66532a6909a28a7417b.png',
'クトゥルフ実娘-クティーラ':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2011/04/Cthylla_3L.png',
'エグリゴリ・トゥリエル':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/06/%E3%83%88%E3%82%A5%E3%83%AA%E3%82%A8%E3%83%AB.png',
'堕天使-バレンタイン':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2012/01/valentine_s.png',
'覚醒-ドラゴノイド':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2011/03/dragonoid_ultimet_r.png',
}

catastrophe = {
'三女神':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2020/12/2da57be77b70a9eaca606109dfc41822.png',
'覚醒龍格闘家-龍姫':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2011/10/ryuho_ki_L_efect.png',
'超覚醒-ドラゴノイド':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2011/03/dragonoid_infinity_r.png',
'デュラハン':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2010/12/armor_d.png',
'氷の女王-シヴァ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2012/03/shiva_l.png',
}

worldend = {
'プレイシュヴァ':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2011/02/breasvha.png',
'真理':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2010/12/abronxless_2.png',
}

rare = {
'アルビノ-ミクロラプトル・グイ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/07/05b540a17ec3687a5a2725cb5ce7b85b.png',
'人化-寿':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/11/72a9e322afc325ee2132393ed1d1b25c.png',
'アルビノ-ブラッドレター':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/07/56bcb287530e2be50552c25dd1f5bd85.png',
'スターウィザード':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/01/ea470cf0eb57c3fd397c76dd8033db03.png',
'ゴールド-モノリス':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2017/06/e591677f3dcebe6d5f001844a7ccb877.png',
'モロナイ':'http://darts-x.sakura.ne.jp/m/wp-content/uploads/2018/06/574126928be7084ff3cf07433a1f2b17.png',
'サキュバス':'http://darts-x.sakura.ne.jp/m//wp-content/uploads/2011/03/Succubus_1.png',
}

ultrarare = {
    "古月":"https://media.discordapp.net/attachments/719489738939301938/750412647203209266/download20200903025142.png?width=585&height=585",
}



def select(lv):
    chance = random.random()
    if chance <= 0.005:
        type = "UltraRare"
        name = random.choice(list(ultrarare.keys()))
        img = ultrarare[name]
    elif chance <= 0.05:
        type = "Rare"
        name = random.choice(list(rare.keys()))
        img = rare[name]
    elif lv % 1000 == 0:
        type = "WorldEnd"
        name = random.choice(list(worldend.keys()))
        img = worldend[name]
    elif lv % 100 == 0:
        type = "Catastrophe"
        name = random.choice(list(catastrophe.keys()))
        img = catastrophe[name]
    elif lv % 10 == 0:
        type = "Elite"
        name = random.choice(list(elite.keys()))
        img = elite[name]
    else:
        type = "Normal"
        name = random.choice(list(normal.keys()))
        img = normal[name]
    return {"type":type, "name":name, "img_url":img}


def get_zukan(type):
    embeds = {}
    if type == 'Normal':
        for name,url in zip(list(normal.keys()),list(normal.values())):
            em = discord.Embed(title='Monster Dictionary',description=f'{name}')
            em.set_image(url=url)
            em.set_footer(text=f'Page.{list(normal.keys()).index(name)+1}/{len(normal)}')
            embeds[name] = em
    if type == 'Elite':
        for name,url in zip(list(elite.keys()),list(elite.values())):
            em = discord.Embed(title='Monster Dictionary',description=f'{name}')
            em.set_image(url=url)
            em.set_footer(text=f'Page.{list(elite.keys()).index(name)+1}/{len(elite)}')
            embeds[name] = em
    if type == 'Catastrophe':
        for name,url in zip(list(catastrophe.keys()),list(catastrophe.values())):
            em = discord.Embed(title='Monster Dictionary',description=f'{name}')
            em.set_image(url=url)
            em.set_footer(text=f'Page.{list(catastrophe.keys()).index(name)+1}/{len(catastrophe)}')
            embeds[name] = em
    if type == 'WorldEnd':
        for name,url in zip(list(worldend.keys()),list(worldend.values())):
            em = discord.Embed(title='Monster Dictionary',description=f'{name}')
            em.set_image(url=url)
            em.set_footer(text=f'Page.{list(worldend.keys()).index(name)+1}/{len(worldend)}')
            embeds[name] = em
    if type == 'Rare':
        for name,url in zip(list(rare.keys()),list(rare.values())):
            em = discord.Embed(title='Monster Dictionary',description=f'{name}')
            em.set_image(url=url)
            em.set_footer(text=f'Page.{list(rare.keys()).index(name)+1}/{len(rare)}')
            embeds[name] = em
    if type == 'UltraRare':
        for name,url in zip(list(ultrarare.keys()),list(ultrarare.values())):
            em = discord.Embed(title='Monster Dictionary',description=f'{name}')
            em.set_image(url=url)
            em.set_footer(text=f'Page.{list(ultrarare.keys()).index(name)+1}/{len(ultrarare)}')
            embeds[name] = em
    return embeds

async def open_zukan(user,ch):
    zukan_em = discord.Embed(
        title="Ranking",
        description=("`表示する図鑑の番号を半角英数字で送信してください。`"
            + "\n`1.`Normal Monster"
            + "\n`2.`Elite Monster"
            + "\n`3.`Catastrophe Monster"
            + "\n`4.`WorldEnd Monster"
            + "\n`5.`Rare Monster"
            + "\n`6.`UltraRare Monster"
    ))
    zukan_em_msg = await ch.send(embed=zukan_em)
    def check(m):
        if not user.id == m.author.id:
            return 0
        return 1
    def check2(m):
        if not user.id == m.author.id:
            return 0
        if not m.content in ("y","Y","n","N"):
            return 0
        return 1
    try:
        msg = await client.wait_for("message", timeout=20, check=check)
    except asyncio.TimeoutError:
        em = discord.Embed(description=f"指定がないので処理終了しました")
        await ch.send(embed=em)
    else:
        respons = int(msg.content)
        if not respons in range(0,7):
            return
        zukan_flag = True
        await msg.delete()
        if respons == 1:
            embeds_dict = get_zukan('Normal')
        if respons == 2:
            embeds_dict = get_zukan('Elite')
        if respons == 3:
            embeds_dict = get_zukan('Catastrophe')
        if respons == 4:
            embeds_dict = get_zukan('WorldEnd')
        if respons == 5:
            embeds_dict = get_zukan('Rare')
        if respons == 6:
            embeds_dict = get_zukan('UltraRare')
        embeds = list(embeds_dict.values())
        await zukan_em_msg.edit(embed=embeds[0])
        em = discord.Embed(description=f"番号を送信するとページが切り替わります 0と送信すると処理が停止してメッセージが残ります")
        em_msg = await ch.send(embed=em)
        while zukan_flag:
            try:
                msg2 = await client.wait_for("message", timeout=20, check=check)
            except asyncio.TimeoutError:
                await zukan_em_msg.delete()
                em = discord.Embed(description=f"指定がないのでメッセージを消去しました")
                await em_msg.edit(embed=em)
                zukan_flag = False
            else:
                page_num = int(msg2.content)
                if 0 < page_num <= len(embeds):
                    await zukan_em_msg.edit(embed=embeds[page_num-1])
                if page_num == 0:
                    ranking_flag = False
                    await em_msg.delete()
                await msg2.delete()
                    





