from collections import namedtuple

# ※全要素をkey->idで管理するように!!
players = {}
mobs = {}
weapons = {}

# デバフ　バフ系
stun = {}
nerf = {}
power_charge = {}
magic_charge = {}
atk_switch = {}
anti_magic = []
exp_up_buff = []
fleez = []

#gui emoji
gui_emoji = {
    "left":"<:left:800980952461213706>",
    "close":"<:close:800980952414158908>",
    "right":"<:right:800980952426741770>",
}

# items_~ #
items_name = {
    1:"冒険者カード",
    2:"HP回復薬",3:"MP回復薬",
    4:"魂の焔",
    5:"砥石",6:"魔石",7:"魔晶",8:"魔硬貨",
    9:"HP全回復薬",10:"MP全回復薬",
    11:'キャラメル鉱石',12:'キャラメル鋼',
    13:'ブラッド鉱石',14:'ブラッド鋼',
    15:'ゴールド鉱石',16:'ゴールド鋼',
    17:'ダーク鉱石',18:'ダーク鋼',
    19:'ミスリル鉱石',20:'ミスリル鋼',
    21:'オリハルコン鉱石',22:'オリハルコン鋼',
    23:"鉄",24:"黒色酸化鉄",
    25:"コークス",26:"カーボンプレート",27:"ハンマー",
}

items_id = {v: k for k, v in items_name.items()}

items_emoji = {
    1:"<:card2:799771986523062322>",
    2:"<:hp_potion:786236538584694815>",
    3:"<:mp_potion:786236615575339029>",
    4:"<:soul_fire:786513145010454538>",
    5:"<:toishi2:799771986125520937>",
    6:"<:masyou2:799771986426593320>",
    7:"<:masuisyou:786516036673470504>",
    8:"<:magic_coin2:799771986476924998>",
    9:"<:hp_full_potion:788668620074385429>",
    10:"<:mp_full_potion:788668620314116106>",
    11:"<:caramel_ore:798207261595271200>",
    12:"<:caramel_ingot:798207112643608616>",
    13:"<:blood_ore:798207261964501002>",
    14:"<:blood_ingot:798207112630894592>",
    15:"<:gold_ore:798207261901586483>",
    16:"<:gold_ingot:798207112584232970>",
    17:"<:dark_ore:798207262068834364>",
    18:"<:dark_ingot:798207112601010236>",
    19:"<:mithril_ore:798207261922164776>",
    20:"<:mithril_ingot:798207112219328553>",
    21:"<:orihalcon_ore:798207262438064209>",
    22:"<:orihalcon_ingot:798207112441364511>",
    23:"<:iron_ingot:800197618234949663>",
    24:"<:black_iron_ingot:800198989676806164>",
    25:"<:carbon_powder:800197618286198813>",
    26:"<:carbon_plate:800197618327486584>",
    27:"<:hammer:800197618336530462>",
}
# 画像があるアイテムの {名前:画像URL} #
items_image = {
    "HP回復薬":"https://media.discordapp.net/attachments/719855399733428244/786984382673977374/hp_potion.gif",
    "MP回復薬":"https://media.discordapp.net/attachments/719855399733428244/786984396887556096/mp_potion.gif",
    "魔石":"https://media.discordapp.net/attachments/719855399733428244/757449362652790885/maseki.png",
    "魔硬貨":"https://media.discordapp.net/attachments/719855399733428244/786984393594896474/magic_coin.gif"
}


shop_weapons = {
    'サバイバルナイフ':('<:w4:798469938380800011>',10000,2),
    '１０式シャベル':('<:w1:798469938595495967>',10000,2),
    'パイプ':('<:w2:798469938536644628>',10000,2),
    'ブロンズソード':('<:w3:798469938511216650>',10000,2),
    'バスターアックス':('<:w5:798469938175934505>',15000,2),
    '刀':('<:w17:798469941753806869>',15000,2),
    'グラム':('<:w6:798469938137792515>',15000,2),
    'セラミックソード':('<:w7:798469938180128779>',15000,2),
    '二刀一対':('<:w9:798469938401509396>',15000,2),
    'ストームブリンガー':('<:w16:798469938682658846>',15000,2),
    'ワイドブレード':('<:w35:798469938666405888>',15000,2),
    'セラミックスピア':('<:w18:798469938317885441>',15000,2),
    'ワンハンドアックス':('<:w26:798469938477400105>',15000,2),
    '十手':('<:w10:798469938389188658>',15000,2),
    'カラドボルグ':('<:w11:798469938418286602>',20000,2),
    'シーパンサー':('<:w12:798469938514886708>',20000,2),
    'フラガラック':('<:w13:798469938532712468>',20000,2),
    'ジャイアントカッター':('<:w14:798469938574393345>',20000,2),
    'スカイブレード':('<:w24:798469938464423953>',25000,2),
    'スカイアックス':('<:w28:798469938498371584>',25000,2),
    'バーンナックル':('<:w21:798469938310021132>',30000,3),
    'レーヴァンティン':('<:w23:798469938426675210>',30000,3),
    'ティルヴィング':('<:w25:798469938469011486>',30000,3),
    'デュランダル':('<:w20:798469938302025729>',30000,3),
    'ツーハンドデッドアックス':('<:w27:798469938481594388>',35000,3),
    'ネックカッター':('<:w29:798469938498502656>',35000,3),
    'ソウルイーター':('<:w30:798469938535858176>',35000,3),
    '黒桜':('<:w22:798469938418286692>',35000,3),
    '小狐丸':('<:w8:798469938208702465>',35000,3),
    'エンダーソード':('<:w31:798469938535989298>',40000,3),
    'スターライトグラム':('<:w19:798469938234523689>',45000,3),
    'カゲミツG4':('<:w32:798469938552897556>',45000,3),
    'ミスリルパイプ':('<:w36:798469938054299719>',45000,3),
    'リーフカッター':('<:w33:798469938565349396>',50000,4),
    'ロンギヌスの槍':('<:w34:798469938603884564>',50000,4),
    'ロストソング':('<:w37:798471199729778748>',50000,4),
    '永久のコイン':('<:w39:799848024640716822>',50000,4)
}
player_weapons = [
    ('サバイバルナイフ', '<:w4:798469938380800011>', 100000), 
    ('１０式シャベル', '<:w1:798469938595495967>', 100000),
    ('パイプ', '<:w2:798469938536644628>', 100000),
    ('ブロンズソード', '<:w3:798469938511216650>', 100000), 
    ('バスターアックス', '<:w5:798469938175934505>', 150000), 
    ('刀', '<:w17:798469941753806869>', 150000), 
    ('グラム', '<:w6:798469938137792515>', 150000), 
    ('セラミックソード', '<:w7:798469938180128779>', 150000), 
    ('二刀一対', '<:w9:798469938401509396>', 150000),
    ('ストームブリンガー', '<:w16:798469938682658846>', 150000), 
    ('ワイドブレード', '<:w35:798469938666405888>', 150000),
    ('セラミックスピア', '<:w18:798469938317885441>', 150000), 
    ('ワンハンドアックス', '<:w26:798469938477400105>', 150000),
    ('十手', '<:w10:798469938389188658>', 150000),
    ('カラドボルグ', '<:w11:798469938418286602>', 200000), 
    ('シーパンサー', '<:w12:798469938514886708>', 200000),
    ('フラガラック', '<:w13:798469938532712468>', 200000),
    ('ジャイアントカッター', '<:w14:798469938574393345>', 200000), 
    ('スカイブレード', '<:w24:798469938464423953>', 250000),
    ('スカイアックス', '<:w28:798469938498371584>', 250000), 
    ('バーンナックル', '<:w21:798469938310021132>', 300000), 
    ('レーヴァンティン', '<:w23:798469938426675210>', 300000),
    ('ティルヴィング', '<:w25:798469938469011486>', 300000), 
    ('デュランダル', '<:w20:798469938302025729>', 300000), 
    ('ツーハンドデッドアックス', '<:w27:798469938481594388>', 350000),
    ('ネックカッター', '<:w29:798469938498502656>', 350000),
    ('ソウルイーター', '<:w30:798469938535858176>', 350000), 
    ('黒桜', '<:w22:798469938418286692>', 350000), 
    ('小狐丸', '<:w8:798469938208702465>', 350000),
    ('エンダーソード', '<:w31:798469938535989298>', 400000), 
    ('スターライトグラム', '<:w19:798469938234523689>', 450000), 
    ('カゲミツG4', '<:w32:798469938552897556>', 450000),
    ('ミスリルパイプ', '<:w36:798469938054299719>', 450000),
    ('リーフカッター', '<:w33:798469938565349396>', 500000), 
    ('ロンギヌスの槍', '<:w34:798469938603884564>', 500000), 
    ('ロストソング', '<:w37:798471199729778748>', 500000),
    ('永久のコイン', '<:w39:799848024640716822>', 500000)
]
Weapon = namedtuple("Weapon", [
    "name",
    "emoji",
    "id",
    "recipe",
    "create_cost",
    "rate_of_rankup",
    ])
Recipe = namedtuple("Rcipe",[
    "soul_fire" ,
    "carmel_ingot" ,"blood_ingot" ,
    "gold_ingot" ,"dark_ingot" ,
    "mithril_ingot" ,"orihalcon_ingot" ,
    "iron_ingot" ,
    "black_iron_ingot" ,
    "carbon_plate" ,
])
Rank = namedtuple("Rank",["S","A","B","C"])
value100000 = Recipe(1000,  50,  50,  25,  25,   0,   0,  100,   0,   0)
value150000 = Recipe(1000, 100, 100,  50,  50,   5,   5,  150,   0,   0)
value200000 = Recipe(1000, 150, 150,  75,  75,  15,  15,  200,   0,   0)
value250000 = Recipe(1000, 200, 200, 100, 100,  30,  30,  250,   0,   0)
value300000 = Recipe(1000, 300, 300, 125, 125,  45,  45,  300,   0,   0)
value350000 = Recipe(1000, 350, 350, 150, 150,  65,  65,  350,   0,   0)
value400000 = Recipe(1000, 400, 400, 275, 275, 110, 110,  400,  50,  50)
value450000 = Recipe(1000, 450, 450, 300, 300, 150, 150,  450, 100, 100)
value500000 = Recipe(1000, 500, 500, 325, 325, 200, 200,  500, 150, 150)
recipe_dict = {
    100000:value100000,150000:value150000,
    200000:value200000,250000:value250000,
    300000:value300000,350000:value350000,
    400000:value400000,450000:value450000,
    500000:value500000,
}
rank_dict = {
    100000:0.25,150000:0.3,
    200000:0.45,250000:0.5,
    300000:0.65,350000:0.7,
    400000:0.85,450000:0.9,
    500000:0.95
}
num = 0
PLAYERmade_weapons = {}
for data in player_weapons:
    num =+ 1
    PLAYERmade_weapons[num] = Weapon(data[0],data[1],num,recipe_dict[data[2]],)
