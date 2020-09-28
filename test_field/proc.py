def dmg_calc(STR,DEF):
    value = random.randint(80,120)
    dmg = ((value*STR) - (DEF*50))/100
    if dmg <= 0:
        dmg = 0
    return dmg



async def battle(user, ch):

    mob = player = None
    if ch.id in mob:
        mob = mob[ch.id]
    if user.id in player:
        player = player[user.id]

    if player.battle_chid and not player.battle_chid == ch.id:
        temp = client.get_channel(player.battle_chid)
        await ch.send(f"【警告】{player.name} は既に{'データ破損' if not temp else temp.mention if temp}で戦闘中です。")
        return
    player.battle_chid(ch.id)
    if mob.battle == [] or not user.id in mob.battle:
        mom.battle.append(user.id)
    if not player.is_alive:
        await ch.send(f"【警告】{player.name} は既に死亡しています。")
        return

    dmg_pm = dmg_ploc(player.STR, mob.DEF)
    dmg_mp = dmg_ploc(mob.DEF, player.STR)

    battle_log1 = battle_log2 = ""

    if player.id in buff.doping:
        buff.doping[player.id][0] -= 1
        dmg_pm = int(dmg_pm*1.1)

    player_win = False
    player_first = False if player.AGI < mob.AGI else True if player.AGI >= mob.AGI
    m, n = random.random(), random.random()
    player_ctl = 1 if m < 0.85 else 3 if m >= 0.95 else 2 if m >= 0.90 else 1.5 if m >= 0.95
    mob_ctl = 1 if n < 0.85 else 3 if n >= 0.95 else 2 if n >= 0.90 else 1.5 if n >= 0.95
    dmg_pm *= player_ctl
    dmg_mp *= mob_ctl
    dmg_pm = int(dmg_pm)
    dmg_mp = int(dmg_mp)

    if player_first:
        if mob.now_hp <= dmg_pm:
            player_win = True
        mob.cut_hp(dmg_mp)

    
