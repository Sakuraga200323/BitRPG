import random

normal = {
    1:("Skeleton","https://media.discordapp.net/attachments/719489738939301938/719490176627507230/hone.png"),
    2:("Roguenite","https://cdn.discordapp.com/attachments/719489738939301938/719490298845069322/heisi.png"),
    3:("Golem","https://media.discordapp.net/attachments/719489738939301938/719490326066102292/iwao.png"),
    4:("LizardGoblin","https://media.discordapp.net/attachments/719489738939301938/719490348933709874/guremrin.png"),
    5:("Skeleton","https://media.discordapp.net/attachments/719489738939301938/719490411198152775/hone2.png"),
    6:("Orc","https://media.discordapp.net/attachments/719489738939301938/719490421964668958/gobb.png"),
    7:("Sludge","https://media.discordapp.net/attachments/719489738939301938/719493729550860339/slimred.png"),
    8:("GoblinSoldier","https://media.discordapp.net/attachments/719489738939301938/719493795850485760/red.png"),
    9:("Mummy","https://media.discordapp.net/attachments/719489738939301938/719494134330556457/mummy.png"),
    10:("Valkyrie","https://media.discordapp.net/attachments/719489738939301938/719494265759072286/tougisya.png"),
    11:("Lorg","http://folce.zatunen.com/m85.png"),
    12:("Manticore","http://folce.zatunen.com/m78.png"),
    13:("Succubus","http://folce.zatunen.com/m67.png"),
    14:("Theaf","http://folce.zatunen.com/m17.png"),
    15:("Bicorn","http://folce.zatunen.com/m13.png"),
    16:("Kerberos","http://folce.zatunen.com/illust/m15.png"),
    17:("Phelios","http://folce.zatunen.com/m11.png"),
    18:("GiantBat","https://blog-imgs-38-origin.fc2.com/e/u/r/eurs/m158a.png")
}

elite = {
    2:("RogueniteElite","http://folce.zatunen.com/m19.png"),
    3:("ValkyrieElite","http://folce.zatunen.com/m52.png"),
    4:("LizardGoblinElite","http://folce.zatunen.com/m37.png"),
    5:("DarkKnight","http://folce.zatunen.com/m36.png"),
    6:("Odin","http://folce.zatunen.com/m62.png"),
    7:("Estate","https://blog-imgs-29-origin.fc2.com/e/u/r/eurs/m317b.png"),
    8:("Imvelna","https://blog-imgs-29-origin.fc2.com/e/u/r/eurs/m316b.png"),
    
}

catastrophe = {
    1:("Catastrophe","https://blog-imgs-29-origin.fc2.com/e/u/r/eurs/m284b.png")
}
  
worldend = {
    1:("Texa","https://media.discordapp.net/attachments/719489738939301938/719686581174140969/5e804b95f8d7cffb7090ad95733a3d09.gif"),
    2:("時空の狭間","https://media.discordapp.net/attachments/719489738939301938/719686743280058408/fdf1cd7d2454971cedd30509e02a4648.gif?width=479&height=671"),
    3:("プレデター","https://blog-imgs-29-origin.fc2.com/e/u/r/eurs/m226a.png"),
    
}

rare = {
    1:("Ajna","http://darts-x.sakura.ne.jp/m/wp-content/uploads/2019/10/c43fb4ea3281e1ae87e168d3bb430d18.png"),
    2:("ValWolf","http://darts-x.sakura.ne.jp/m/wp-content/uploads/2014/08/50afb13d8d0bcf721b6683e70e0d841b.png")
}

ultrarare = {
    1:("古月","https://media.discordapp.net/attachments/719489738939301938/750412647203209266/download20200903025142.png?width=585&height=585"),
    2:("🎁MerryChristmas！！🎁","https://media.discordapp.net/attachments/719489738939301938/791694439055097866/New_Piskel_9.png?width=867&height=614")
}



def select(lv):
    if random.random() <= 0.001:
        type = "UltraRare"
        result = random.choice(list(ultrarare.values()))
    elif random.random() <= 0.01:
        type = "Rare"
        result = random.choice(list(rare.values()))
    elif lv % 1000 == 0:
        type = "WorldEnd"
        result = random.choice(list(worldend.values()))
    elif lv % 10 == 0:
        type = "Elite"
        result = random.choice(list(elite.values()))
    else:
        type = "Normal"
        result = random.choice(list(normal.values()))
    return {"type":type, "name":result[0], "img_url":result[1]}
