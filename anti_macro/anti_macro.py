import cv2
from anti_macro import paste
import io
import tempfile
import requests
from matplotlib import pyplot as plt


import discord
client = None

async def get_img(c):
    global client
    client = c
    channel = client.get_channel(761521730035646464)
    channel2 = client.get_channel(761522350248165486)
    temp = await channel.history().flatten()
    imgs_front = [ i.attachments[0].url for i in temp]
    temp = await channel2.history.flatten()
    imgs_back = dict(
        zip(
            [ i.attachments[0].url for i in temp],[ i.content for i in temp]))
    front_url = random.choice(imgs_front)
    back_url = random.choice(imgs_front)
    num =  imgs_front[back_url]
    # 画像をリクエストする
    def get_from_url(url):
        res = requests.get(url)
        img = None
        # Tempfileを作成して即読み込む
        with tempfile.NamedTemporaryFile(dir='./') as fp:
            fp.write(res.content)
            fp.file.seek(0)
            img = cv2.imread(fp.name)
        return img
    img = padte.paste(
        get_from_url(front_url),# 前景
        get_from_url(back_url),# 背景
        False, False # 縁フラグ、回転・移動フラグ
    )
    return img, num
