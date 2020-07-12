def dmg_calc(STR, DEF):
    value = random.randint(80,120)
    dmg = (( value * STR ) - ( DEF * 50 )) / 100
    if dmg <= 0:
        dmg = 1
    return dmg
