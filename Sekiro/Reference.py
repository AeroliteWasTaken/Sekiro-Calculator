EnemyName = {
    'Tutorial Genichiro': 71000000,
    'Lady Butterfly': 50900000,
    'Gyoubu': 50800000,
    'Genichiro Ashina': 71001000,
    'Guardian Ape': 51000000,
    'Headless Ape': 51000100,
    'Brown Ape': 51000010,
    'Corrupted Monk': 50001000,
    'Emma': 74000010,
    'Isshin Ashina': 54300000,
    'Great Shinobi Owl': 50600000,
    'True Monk': 50000000,
    'Divine Dragon': 52000000,
    'Owl (Father)': 50601010,
    'Demon of Hatred': 70200000,
    'Genichiro Way of Tomoe (Silvergrass Field)': 71101000,
    'Isshin the Sword Saint': 54000000,
    'Inner Genichiro': 1,
    'Inner Father': 2,
    'Inner Isshin': 3,
    'Shigenori Yamauchi': 10201000,
    'Naomori Kawarada': 10200000,
    'Chained Ogre': 50202000,
    'Tenzen Yamauchi': 10200010,
    'Headless - Ako': 13500000,
    'Shinobi Hunter Enshin': 10500001,
    'Juzou': 10700000,
    'Blazing Bull': 13700000,
    'Armoured Warrior': 11300000,
    'Long Arm Centipede Sen-Un': 10400000,
    'Lone Shadow Longswordsman': 14704000,
    'General Kuranosuke Matsumoto': 10202000,
    'Seven Ashina Spears - Shikibu Toshikatsu Yamauchi': 10210000,
    'Headless - Ungo': 13400000,
    'Lone Shadow Masanaga the Spear-bearer': 14701006,
    'Ashina Elite - Jinsuke Saze': 14000200,
    'Shichimen Warrior (Dungeon)': 10800000,
    'Headless - Gokan': 13501000,
    'Snake Eyes Shirafuji': 11910000,
    'Headless - Gachiin': 13502000,
    'Tokujiro ': 10703000,
    'Mist Noble': 13001000,
    "O'Rin of the Water": 70000000,
    'Snake Eyes Shirahagi': 11911000,
    'Chained Ogre (Castle)': 50200010,
    'Lone Shadow Vilehand': 14701005,
    'Long-arm Centipede Giraffe': 10401000,
    'Shichimen Warrior (Ashina Depths)': 10802000,
    'Shigekichi of the Red Guard': 10701000,
    'Chained Ogre (Outskirts)': 50205000,
    'Sakura Bull of the Palace': 13800000,
    'Lone Shadow Masanaga the Spear-bearer (Hirata 2)': 14703002,
    'Juzou (Hirata 2)': 10704000,
    'Seven Ashina Spears - Shume Masaji Oniwa': 10211000,
    'Ashina Elite - Ujinari Mizuo': 14004200,
    'Okami Leader Shizu': 13100310,
    'Shichimen Warrior (Fountainhead)': 10801000,
    'Headless - Yashariku': 13401000,
    'Headless - Yashariku Phantom': 13401001
}

InnerEnemy = {
    1: 71001000,
    2: 50601010,
    3: 54000000}

ItemLot_Time_Offset = {
    False:
        {1: 1,
        2: 11,
        3: 21,
        4: 31},
    True:
        {1: 11,
         2: 21,
         3: 31,
         4: 41}
}

ReflectionOverride = {
0: { # default
    (False, False): [7950, 7954], # default 
    (True, False): [7952, 7992], # cl
    (False, True): [7953, 7993], # db 
    (True, True): [7951, 7955]}, # cldb 

1: { # inner geni
    (False, False): [7962, 7966], # default 
    (True, False): [7964, 7968], # cl 
    (False, True): [7965, 7969], # db 
    (True, True): [7963, 7967]}, # cldb 

2: { # inner father
    (False, False): [7950, 7954], # default 
    (True, False): [7952, 7956], # cl 
    (False, True): [7953, 7957], # db 
    (True, True): [7951, 7955]}, # cldb 

3: { # inner isshin
    (False, False): [7950, 7954], # default 
    (True, False): [7952, 7956], # cl 
    (False, True): [7953, 7957], # db 
    (True, True): [7951, 7955]}, # cldb 

51000000: { # guardian ape
    (False, False): [7930, 7934], # default 
    (True, False): [7932, 7936], # cl 
    (False, True): [7933, 7937], # db 
    (True, True): [7931, 7935]}, # cldb 

74000010: { #emma
    (False, False): [7986, 7990], # default 
    (True, False): [7988, 7992], # cl
    (False, True): [7989, 7993], # db
    (True, True): [7987, 7991]}, # cldb

54300000: { #IA
    (False, False): [7986, 7990], # default 
    (True, False): [7988, 7992], # cl
    (False, True): [7989, 7993], # db 
    (True, True): [7987, 7991]}, # cldb

71101000: { #Geni WOT (Final Boss)
    (False, False): [7986, 7990], # default 
    (True, False): [7988, 7992], # cl
    (False, True): [7989, 7993], # db
    (True, True): [7987, 7991]}, # cldb

}

MortalJourneyOverride = {
0: { # default
    (False, False): [7950, 7958], # default
    (True, False): [7952, 7958], # cl
    (False, True): [7986, 7959], # db 
    (True, True): [7951, 7959]}, # cldb

1: { # inner geni
    (False, False): [7962, 7970], # default 
    (True, False): [7964, 7972], # cl 
    (False, True): [7965, 7973], # db 
    (True, True): [7963, 7971]}, # cldb 

2: { # inner father
    (False, False): [7950, 7958], # default 
    (True, False): [7952, 7960], # cl 
    (False, True): [7953, 7961], # db 
    (True, True): [7951, 7959]}, # cldb 

3: { # inner isshin
    (False, False): [7950, 7958], # default 
    (True, False): [7952, 7960], # cl 
    (False, True): [7953, 7961], # db 
    (True, True): [7951, 7959]}, # cldb 

51000000: { # guardian ape
    (False, False): [7930, 7938], # default 
    (True, False): [7932, 7940], # cl 
    (False, True): [7933, 7941], # db 
    (True, True): [7931, 7939]}, # cldb 

74000010: { #emma
    (False, False): [7986, 7994], # default 
    (True, False): [7988, 7996], # cl
    (False, True): [7989, 7997], # db
    (True, True): [7987, 7995]}, # cldb

54300000: { #IA
    (False, False): [7986, 7994], # default 
    (True, False): [7988, 7996], # cl
    (False, True): [7989, 7997], # db 
    (True, True): [7987, 7995]}, # cldb

71101000: { #Geni WOT (Final Boss)
    (False, False): [7986, 7994], # default 
    (True, False): [7988, 7996], # cl
    (False, True): [7989, 7997], # db
    (True, True): [7987, 7995]}, # cldb
}
