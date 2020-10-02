import cv2
import numpy as np
from anti_macro import rotate

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
        img2, _ = rotate.rotateR(fg, [-90, 90], 1.0)
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
    return img1
