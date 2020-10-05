import cv2
from anti_macro import paste
import io
import tempfile
import requests
from matplotlib import pyplot as plt
import random


import discord
client = None

async def get_img(c):
    global client
    client = c
    num = random.randint(0,9)
    img_front = cv2.imread(f"anti_macro/num_img/front/front{random.randint(1,10)}.png",-1)
    img_num = cv2.imread(f"anti_macro/num_img/num/{num}.png",-1)
    print(img_front, img_num)
    # 画像をリクエストする
    img = paste.paste(
        img_front,# 前景
        img_num,# 背景
        False, True # 縁フラグ、回転・移動フラグ
    )
    return img, num
