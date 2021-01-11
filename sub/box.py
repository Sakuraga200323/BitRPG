# ※全要素をkey->idで管理するように!!
players = {}
mobs = {}
cmd_user = []
cbt_user = {}
cbt_ch = {}
cmd_ch = []

# デバフ　バフ系
stun = {}
nerf = {}
power_charge = {}
magic_charge = {}
atk_switch = {}
anti_magic = []
exp_up_buff = []
fleez = []

# items_~ #
items_name = {
    1:"冒険者カード",
    2:"HP回復薬",3:"MP回復薬",
    4:"魂の焔",
    5:"砥石",6:"魔石",7:"魔晶",8:"魔硬貨",
    9:"HP全回復薬",10:"MP全回復薬",
}

items_id = {
    "冒険者カード":1,
    "HP回復薬":2,"MP回復薬":3,
    "魂の焔":4,
    "砥石":5,"魔石":6,"魔晶":7,"魔硬貨":8,
    "HP全回復薬":9,"MP全回復薬":10,
}

items_emoji = {
    1:"<:card:786514637289947176>",
    2:"<:hp_potion:786236538584694815>",
    3:"<:mp_potion:786236615575339029>",
    4:"<:soul_fire:786513145010454538>",
    5:"<:toishi:786513144691556364>",
    6:"<:maseki:785641515561123921>",
    7:"<:masuisyou:786516036673470504>",
    8:"<:magic_coin:786513121236746260>",
    9:"<:hp_full_potion:788668620074385429>",
    10:"<:mp_full_potion:788668620314116106>",
}

items_emoji_a = {
    1:"<:card:786514637289947176>",
    2:"<a:hp_potion_a:786982694479200336>",
    3:"<a:mp_potion_a:786982694839124021>",
    4:"<:soul_fire:786513145010454538>",
    5:"<a:toishi_a:786974865777229864>",
    6:"<:maseki:785641515561123921>",
    7:"<a:masuisyou_a:786982694948306974>",
    8:"<a:magic_coin_a:786966211594289153>",
    9:"<:hp_full_potion:788668620074385429>",
    10:"<:mp_full_potion:788668620314116106>",
}

# 画像があるアイテムの {名前:画像URL} #
items_image = {
    "HP回復薬":"https://media.discordapp.net/attachments/719855399733428244/786984382673977374/hp_potion.gif",
    "MP回復薬":"https://media.discordapp.net/attachments/719855399733428244/786984396887556096/mp_potion.gif",
    "魔石":"https://media.discordapp.net/attachments/719855399733428244/757449362652790885/maseki.png",
    "魔硬貨":"https://media.discordapp.net/attachments/719855399733428244/786984393594896474/magic_coin.gif"
}
