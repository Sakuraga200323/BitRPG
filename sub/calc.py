import random

def randint(a,b):
    return random.randint(a,b)

def dmg(STR,DEF):
    value = random.randint(80,120)
    dmg = ((value*STR) - (DEF*50))/100
    if dmg <= 0:
        dmg = 1
    return dmg
