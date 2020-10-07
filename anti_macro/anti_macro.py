import cv2
import io
import tempfile
import requests
import numpy as np
from matplotlib import pyplot as plt
import random


import discord
client = None





def rotate(img, angle, scale):
    """
    画像を回転（反転）させる
    [in]  img:   回転させる画像
    [in]  angle: 回転させる角度
    [in]  scale: 拡大率
    [out] 回転させた画像
    """

    size = img.shape[:2]
    mat = cv2.getRotationMatrix2D((size[0] // 2, size[1] // 2), angle, scale)
    return cv2.warpAffine(img, mat, size, flags=cv2.INTER_CUBIC)


def rotateR(img, level=[-10, 10], scale=1.2):
    """
    ランダムに画像を回転させる
    [in]  img:   回転させる画像
    [in]  level: 回転させる角度の範囲
    [out] 回転させた画像
    [out] 回転させた角度
    """

    angle = np.random.randint(level[0], level[1])
    return rotate(img, angle, scale), angle


def paste(fg, bg, mask_flg=True, random_flg=True):
    """
    背景に前景を重ね合せる
    [in]  fg:         重ね合せる背景
    [in]  bg:         重ね合せる前景
    [in]  mask_flg:   マスク処理を大きめにするフラグ
    [in]  random_flg: 前景をランダムに配置するフラグ
    [out] 重ね合せた画像
    """

    # Load two images
    img1 = bg.copy()
    if random_flg:# ランダム回転
        img2, _ = rotateR(fg, [-90, 90], 1.0)
    else:
        img2 = fg.copy()

    # I want to put logo on top-left corner, So I create a ROI
    w1, h1 = img1.shape[:2]
    w2, h2 = img2.shape[:2]
    if random_flg:# ランダム移動
        x = np.random.randint(0, w1 - w2 + 1)
        y = np.random.randint(0, w1 - w2 + 1)
    else:
        x = 0
        y = 0

    roi = img1[x:x + w2, y:y + h2]

    # Now create a mask of logo and create its inverse mask also
    print(type(img2))
    mask = img2[:, :, 3]
    ret, mask_inv = cv2.threshold(
        cv2.bitwise_not(mask),
        200, 255, cv2.THRESH_BINARY
    )

    if mask_flg:# 縁を膨張・収縮で作成（膨張大きめ）
        kernel1 = np.ones((5, 5), np.uint8)
        kernel2 = np.ones((3, 3), np.uint8)
        mask_inv = cv2.dilate(mask_inv, kernel1, iterations=1)
        mask_inv = cv2.erode(mask_inv, kernel2, iterations=1)

    # Now black-out the area of logo in ROI
    img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

    # Take only region of logo from logo image.
    img2_fg = cv2.bitwise_and(img2, img2, mask=mask)

    # Put logo in ROI and modify the main image
    dst = cv2.add(img1_bg, img2_fg)
    img1[x:x + w2, y:y + h2] = dst
    print("img1", img1)
    return img1

async def get_img(c):
    global client
    client = c
    num = random.randint(0,9)
    img_front0 = cv2.imread(f"anti_macro/num_img/枠.png",-1)
    img_front1 = cv2.imread(f"anti_macro/num_img/front/front{random.randint(1,10)}.png",-1)
    img_num = cv2.imread(f"anti_macro/num_img/num/{num}.png",-1)
    print(type(img_front), type(img_num))
    # 画像をリクエストする
    img = paste(
        img_front1,# 前景
        img_num,# 背景
        False, True # 縁フラグ、回転・移動フラグ
    )
    result_img = paste(
        img_front0,# 前景
        img,# 背景
        False, False # 縁フラグ、回転・移動フラグ
    )
    return result_img, num
