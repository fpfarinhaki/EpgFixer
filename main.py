# coding=utf-8
from M3uFixer import M3uFixer
import sys
import logging

channel_id_dic = {
    "A&E": ['A&E', 'A&E FHD', 'A&E HD', 'A&E HD [Alter]', 'A&E [Alter]'],
    "AMC": ['AMC', 'AMC FHD', 'AMC HD', 'AMC HD [Alter]', 'AMC [Alter]'],
    "AnimalPlanet": ['ANIMAL  PLANET FHD', 'ANIMAL PLANET', 'ANIMAL PLANET HD', 'ANIMAL PLANET HD [Alter]',
                     'ANIMAL PLANET [Alter]'],
    "Arte1": ['ARTE 1', 'ARTE 1 FHD', 'ARTE 1 HD', 'ARTE 1 [Alter]'],
    "AXN": ['AXN FHD', 'AXN HD', 'AXN HD [Alter]', 'AXN SD', 'AXN [Alter]'],
    "BabyTv": ['BABY TV', 'BABY TV [Alter]'],
    "Band": ['BAND HD [Alter]', 'BAND SP', 'BAND SP FHD', 'BAND SP HD', 'BAND SP [Alter]'],
    "BandNews": ['BAND NEWS', 'BAND NEWS FHD', 'BAND NEWS HD', 'BAND NEWS [Alter]'],
    "BandSports": ['BAND SPORTS', 'BAND SPORTS FHD', 'BAND SPORTS HD', 'BAND SPORTS [Alter]', 'Band Sports HD [Alter]'],
    "BIS": ['BIS', 'BIS FHD', 'BIS HD', 'BIS [Alter]', 'Bis HD [Alter]'],
    "Boomerang": ['BOOMERANG', 'BOOMERANG  FHD', 'BOOMERANG HD', 'BOOMERANG [Alter]', 'Boomerang HD [Alter]'],
    "CanalBrasil": ['CANAL BRASIL', 'CANAL BRASIL FHD', 'CANAL BRASIL HD', 'CANAL BRASIL [Alter]'],
    "CançãoNova": ['CANÇÃO NOVA', 'CANÇÃO NOVA [Alter]'],
    "CartoonNetwork": ['CARTOON NETWORK', 'CARTOON NETWORK FHD', 'CARTOON NETWORK HD', 'CARTOON NETWORK [Alter]',
                       'Cartoon Network HD [Alter]'],
    "Cinemax": ['CINEMAX', 'CINEMAX FHD', 'CINEMAX HD', 'CINEMAX [Alter]', 'Cinemax HD [Alter]'],
    "Combate": ['COMBATE', 'COMBATE FHD', 'COMBATE HD', 'Combate HD [Alter]', 'Combate [Alter]'],
    "ComedyCentral": ['COMEDY CENTRAL', 'COMEDY CENTRAL FHD', 'COMEDY CENTRAL HD', 'Comedy Central HD [Alter]',
                      'Comedy Central [Alter]'],
    "Cultura": ['TV CULTURA FHD', 'TV CULTURA HD', 'TV CULTURA SD', 'TV Cultura [Alter]'],
    "DAZN1": ['DAZN 1 FHD', 'DAZN 1 HD', 'DAZN 1 SD'],
    "DAZN2": ['DAZN 2 FHD', 'DAZN 2 HD', 'DAZN 2 SD'],
    "DAZN3": ['DAZN 3 FHD', 'DAZN 3 HD', 'DAZN 3 SD'],
    "Discovery": ['DISCOVERY CHANNEL', 'DISCOVERY CHANNEL FHD', 'DISCOVERY CHANNEL HD',
                  'Discovery Channel HD [Alter]', 'Discovery Channel [Alter]'],
    "DiscoveryCivilization": ['DISCOVERY CIVILIZATION', 'DISCOVERY CIVILIZATION FHD', 'DISCOVERY CIVILIZATION HD',
                              'Discovery Civilization HD [Alter]'],
    "DiscoveryHomeHealth": ['DISCOVERY HOME & HEALTH', 'DISCOVERY HOME & HEALTH FHD',
                            'DISCOVERY HOME & HEALTH HD', 'Discovery H&H [Alter]',
                            'Discovery Home & Helth HD [Alter]'],
    "DiscoveryKids": ['DISCOVERY KIDS', 'DISCOVERY KIDS FHD', 'DISCOVERY KIDS HD', 'DISCOVERY KIDS [Alter]',
                      'Discovery Kids HD [Alter]'],
    "DiscoveryScience": ['DISCOVERY SCIENCE', 'DISCOVERY SCIENCE FHD', 'DISCOVERY SCIENCE HD',
                         'Discovery Science HD [Alter]'],
    "DiscoveryTheater": ['DISCOVERY THEATER', 'DISCOVERY THEATER FHD', 'DISCOVERY THEATER HD',
                         'Discovery Theater HD [Alter]'],
    "DiscoveryTurbo": ['DISCOVERY TURBO', 'DISCOVERY TURBO FHD', 'DISCOVERY TURBO HD', 'Discovery Turbo HD [Alter]',
                       'Discovery Turbo [Alter]'],
    "DiscoveryWorld": ['DISCOVERY WORLD', 'DISCOVERY WORLD  HD', 'DISCOVERY WORLD FHD',
                       'Discovery World HD [Alter]'],
    "Disney": ['DISNEY CHANNEL', 'DISNEY CHANNEL FHD', 'DISNEY CHANNEL HD', 'Disney Channel HD [Alter]',
               'Disney [Alter]'],
    "DisneyJr": ['DISNEY JR FHD', 'DISNEY JR HD', 'DISNEY JR SD', 'Disney JR [Alter]'],
    "DisneyXD": ['DISNEY XD SD', 'Disney XD [Alter]'],
    "E!": ['E! FHD', 'E! HD', 'E! HD [Alter]', 'E! SD', 'E! [Alter]'],
    "EI2": ['EI PLUS 2 HD', 'EI PLUS 2 SD'],
    "EI3": ['EI PLUS 3 HD', 'EI PLUS 3 SD'],
    "EI": ['EI PLUS HD*', 'EI PLUS SD*'],
    "ESPN": ['ESPN   [Alter]', 'ESPN FHD', 'ESPN HD', 'ESPN HD [Alter]', 'ESPN SD', 'ESPN [Alter]'],
    "ESPN2": ['ESPN 2 FHD', 'ESPN 2 HD', 'ESPN 2 HD [Alter]', 'ESPN 2 SD'],
    "ESPNBrasil": ['ESPN BRASIL FHD', 'ESPN BRASIL HD', 'ESPN BRASIL HD [Alter]', 'ESPN BRASIL SD',
                   'Espn Brasil [Alter]'],
    "ESPN+": ['ESPN EXTRA HD', 'ESPN EXTRA SD', 'ESPN Extra FHD', 'ESPN Extra HD [Alter]', 'ESPN Plus HD [Alter]'],
    "FilmArts": ['FILM & ARTS SD'],
    "FishTV": ['FISH TV FHD', 'FISH TV HD', 'FISH TV SD', 'Fish TV HD [Alter]', 'Fish TV [Alter]'],
    "FoodNetwork": ['FOOD NETWORK FHD', 'FOOD NETWORK HD', 'FOOD NETWORK SD', 'Food Network HD [Alter]',
                    'Food Network [Alter]'],
    "FOX": ['FOX FHD', 'FOX HD', 'FOX SD', 'Fox 1 HD [Alter]', 'Fox HD [Alter]', 'Fox [Alter]'],
    "FOXLife": ['FOX LIFE FHD', 'FOX LIFE HD', 'FOX LIFE SD', 'Fox Life HD [Alter]', 'Fox Life [Alter]'],
    "FOXSports": ['FOX SPORTS FHD', 'FOX SPORTS HD', 'FOX SPORTS HD [Alter]', 'FOX SPORTS SD', 'FOX SPORTS [Alter]'],
    "FOXSports2": ['FOX SPORTS 2 FHD', 'FOX SPORTS 2 HD', 'FOX SPORTS 2 SD', 'Fox Sports 2 HD [Alter]',
                   'Fox Sports 2 [Alter]'],
    "Futura": ['FUTURA FHD', 'FUTURA HD', 'FUTURA SD'],
    "FX": ['FX FHD', 'FX HD', 'FX HD [Alter]', 'FX SD', 'FX [Alter]'],
    "GloboRpc": ['GLOBO RPC CURITIBA FHD', 'GLOBO RPC CURITIBA HD', 'GLOBO RPC CURITIBA SD', 'RPC Curitiba [Alter]',
                 'GLOBO RPC FOZ DO IGUACU HD'],
    "GloboNews": ['GLOBO NEWS', 'GLOBO NEWS FHD', 'GLOBO NEWS HD', 'GLOBO NEWS HD [Alter]', 'GLOBO NEWS [Alter]'],
    "Gloob": ['GLOOB FHD', 'GLOOB HD', 'GLOOB SD', 'Gloob HD [Alter]', 'Gloob [Alter]'],
    "Gloobinho": ['GLOOBINHO FHD', 'GLOOBINHO HD', 'GLOOBINHO SD'],
    "Globosat": ['MAIS GLOBOSAT FHD', 'MAIS GLOBOSAT HD', 'MAIS GLOBOSAT SD'],
    "GNT": ['GNT', 'GNT FHD', 'GNT HD', 'GNT HD [Alter]', 'GNT [Alter]'],
    "HBO2": ['HBO 2 FHD', 'HBO 2 HD', 'HBO 2 HD [Alter]', 'HBO 2 SD', 'HBO 2 [Alter]'],
    "HBOFamily": ['HBO FAMILY FHD', 'HBO FAMILY HD', 'HBO FAMILY SD', 'HBO Family HD [Alter]', 'HBO Family [Alter]'],
    "HBO": ['HBO FHD', 'HBO HD', 'HBO HD [Alter]', 'HBO SD', 'HBO [Alter]'],
    "HBOPlus": ['HBO PLUS SD', 'HBO Plus [Alter]', 'HBO PLUS FHD', 'HBO PLUS HD', 'HBO Plus HD [Alter]'],
    "HBOSignature": ['HBO SIGNATURE FHD', 'HBO SIGNATURE HD', 'HBO SIGNATURE SD', 'HBO SIGNATURE [Alter]',
                     'HBO Signature HD [Alter]'],
    "HistoryChannel": ['HISTORY SD', 'History [Alter]', 'HISTORY FHD', 'HISTORY HD', 'History HD [Alter]'],
    "H2": ['H2 FHD', 'H2 HD', 'H2 SD', 'History 2 HD [Alter]', 'History 2 [Alter]'],
    "DiscoveryInvestigation": ['INVESTIGATION DISCOVERY FHD', 'INVESTIGAÇÃO DISCOVERY', 'INVESTIGAÇÃO DISCOVERY HD',
                               'INVESTIGAÇÃO DISCOVERY HD [Alter]', 'INVESTIGAÇÃO DISCOVERY [Alter]'],
    "Lifetime": ['LIFETIME', 'LIFETIME FHD', 'LIFETIME HD', 'Life Time HD [Alter]', 'Life Time [Alter]'],
    "MAX": ['MAX FHD', 'MAX HD', 'MAX SD', 'MAX UP FHD', 'MAX UP HD', 'MAX UP SD', 'Max HD [Alter]', 'Max [Alter]'],
    "Maxprime": ['MAX PRIME FHD', 'MAX PRIME HD', 'MAX PRIME SD', 'Max Prime HD [Alter]', 'Max Prime [Alter]'],
    "Megapix": ['MEGAPIX FHD', 'MEGAPIX HD', 'MEGAPIX SD', 'Megapix HD [Alter]', 'Megapix [Alter]'],
    "MTV": ['MTV', 'MTV FHD', 'MTV HD', 'MTV HD [Alter]', 'MTV [Alter]'],
    "MTV Live": ['MTV LIVE FHD', 'MTV LIVE HD', 'MTV LIVE SD'],
    "Multishow": ['MULTISHOW', 'MULTISHOW FHD', 'MULTISHOW HD', 'Multishow HD [Alter]', 'Multishow [Alter]'],
    "MusicBox": ['MUSIC BOX BRASIL FHD', 'MUSIC BOX BRASIL HD', 'MUSIC BOX BRASIL SD', 'Music Box Brasil [Alter]'],
    "MaxUp": ['Max UP HD [Alter]', 'Max UP [Alter]'],
    "NationalGeographic": ['NAT GEO FHD', 'NAT GEO HD', 'NAT GEO SD', 'NatGeo HD [Alter]', 'NatGeo [Alter]'],
    "NatGeoKids": ['NAT GEO KIDS FHD', 'NAT GEO KIDS HD', 'NAT GEO KIDS SD', 'NatGeo Kids HD [Alter]',
                   'NatGeo Kids [Alter]'],
    "NatGeoWild": ['NAT GEO WILD FHD', 'NAT GEO WILD HD', 'NAT GEO WILD SD', 'NatGeo Wild HD [Alter]',
                   'NatGeo Wild [Alter]'],
    "NBR": ['NBR', 'NBR [Alter]'],
    "NHK": ['NHK [Alter]'],
    "NickJr": ['NICK JR FHD', 'NICK JR HD', 'NICK JR SD', 'Nick JR HD [Alter]', 'Nick JR [Alter]'],
    "Nickelodeon": ['NICKELODEN SD', 'NICKELODEON FHD', 'NICKELODEON HD', 'Nickelodeon HD [Alter]',
                    'Nickelodeon [Alter]'],
    "Off": ['OFF FHD', 'OFF HD', 'OFF HD [Alter]', 'OFF SD', 'OFF [Alter]'],
    "Paramount": ['PARAMOUNT CHANNEL  [Alter]', 'PARAMOUNT CHANNEL FHD', 'PARAMOUNT CHANNEL HD',
                  'PARAMOUNT CHANNEL HD [Alter]', 'PARAMOUNT CHANNEL SD'],
    "Playboy": ['PLAYBOY', 'PLAYBOY FHD', 'PLAYBOY HD', 'PLAYBOY HD [Alter]', 'PLAYBOY [Alter]'],
    "PlayTV": ['Play Tv [Alter]'],
    "PrimeBoxBr": ['PRIME BOX BRASIL FHD', 'PRIME BOX BRASIL HD', 'PRIME BOX BRASIL SD',
                   'Prime Box Brasil [Alter]'],
    "PremiereClubes": ['PREMIERE CLUBES FHD', 'Premiere Clubes HD', 'Premiere Clubes HD [Alter]', 'Premiere Clubes SD',
                       'Premiere Clubes [Alter]'],
    "Premiere2": ['PREMIERE 2 FHD', 'PREMIERE 2 HD', 'PREMIERE 2 SD', 'Premiere 2 HD [Alter]', 'Premiere 2 [Alter]'],
    "Premiere3": ['PREMIERE 3 FHD', 'PREMIERE 3 HD', 'PREMIERE 3 SD', 'Premiere 3 HD [Alter]', 'Premiere 3 [Alter]'],
    "Premiere4": ['PREMIERE 4 FHD', 'PREMIERE 4 HD', 'PREMIERE 4 SD', 'Premiere 4 HD [Alter]', 'Premiere 4 [Alter]'],
    "Premiere5": ['PREMIERE 5 FHD', 'PREMIERE 5 HD', 'PREMIERE 5 SD', 'Premiere 5 HD [Alter]', 'Premiere 5 [Alter]'],
    "Premiere6": ['PREMIERE 6 FHD', 'PREMIERE 6 HD', 'PREMIERE 6 SD', 'Premiere 6 HD [Alter]', 'Premiere 6 [Alter]'],
    "Premiere7": ['PREMIERE 7 FHD', 'PREMIERE 7 HD', 'PREMIERE 7 SD', 'Premiere 7 HD [Alter]', 'Premiere 7 [Alter]'],
    "Premiere8": ['Premiere 8 [Alter]'],
    "RATIMBUM": ['TV RA TIM BUM FHD', 'TV RA TIM BUM HD', 'TV RA TIM BUM SD', 'TV RA TIM BUM [Alter]'],
    "Record": ['RECORD HD Alternativo', 'RECORD HD [Alter]', 'RECORD [Alter]'],
    "RecordNews": ['RECORD NEWS', 'RECORD NEWS FHD', 'RECORD NEWS HD', 'RECORD NEWS [Alter]', 'RIT'],
    "RedeTV!": ['REDE TV', 'REDE TV FHD', 'REDE TV HD', 'REDE TV HD [Alter]', 'REDE TV [Alter]'],
    "RedeVida": ['REDE VIDA', 'REDE VIDA FHD', 'REDE VIDA HD', 'REDE VIDA [Alter]'],
    "SBT": ['SBT', 'SBT FHD', 'SBT HD', 'SBT HD [Alter]', 'SBT SP INTERIOR', 'SBT [Alter]'],
    "SextremeBr": ['SEXTREME', 'SEXTREME [Alter]'],
    "SexyHot": ['SEXY HOT', 'SEXY HOT [Alter]'],
    "SIC": ['SIC Internacional [Alter]'],
    "Smithsonian": ['SMITHSONIAN CHANNEL FHD', 'SMITHSONIAN CHANNEL HD', 'SMITHSONIAN CHANNEL SD'],
    "Space": ['SPACE FHD', 'SPACE HD', 'SPACE SD', 'Space HD [Alter]', 'Space [Alter]'],
    "SporTV": ['SPORTV FHD', 'SPORTV HD', 'SPORTV SD', 'Sportv HD [Alter]', 'Sportv [Alter]'],
    "SporTV2": ['SPORTV 2 FHD', 'SPORTV 2 HD', 'SPORTV 2 SD', 'Sportv 2 HD [Alter]', 'Sportv 2 [Alter]'],
    "SporTV3": ['SPORTV 3 FHD', 'SPORTV 3 HD', 'SPORTV 3 SD', 'Sportv 3 HD [Alter]', 'Sportv 3 [Alter]'],
    "UniversalStudio": ['STUDIO UNIVERSAL FHD', 'STUDIO UNIVERSAL HD', 'STUDIO UNIVERSAL SD',
                        'Studio Universal HD [Alter]', 'Studio Universal [Alter]'],
    "SyFy": ['SYFY FHD', 'SYFY HD', 'SYFY SD', 'Syfy HD [Alter]', 'Syfy [Alter]'],
    "Sony": ['CANAL SONY', 'CANAL SONY FHD', 'CANAL SONY HD', 'Canal Sony HD [Alter]', 'Sony [Alter]'],
    "TBS": ['TBS FHD', 'TBS HD', 'TBS HD [Alter]', 'TBS SD', 'TBS [Alter]'],
    "TCM": ['TCM SD', 'TCM [Alter]'],
    "TelecineAction": ['TELECINE ACTION', 'TELECINE ACTION [Alter]', 'TELECINE ACTION FHD', 'TELECINE ACTION HD',
                       'TELECINE ACTION HD [Alter]'],
    "TelecineCult": ['TELECINE CULT', 'TELECINE CULT FHD', 'TELECINE CULT HD', 'TELECINE CULT HD [Alter]',
                     'TELECINE CULT [Alter]'],
    "TelecineFun": ['TELECINE FUN', 'TELECINE FUN [Alter]', 'TELECINE FUN FHD', 'TELECINE FUN HD',
                    'TELECINE FUN HD [Alter]'],
    "TelecinePipoca": ['TELECINE PIPOCA', 'TELECINE PIPOCA [Alter]', 'TELECINE PIPOCA FHD', 'TELECINE PIPOCA HD',
                       'TELECINE PIPOCA HD [Alter]'],
    "TelecinePremium": ['TELECINE PREMIUM', 'TELECINE PREMIUM FHD', 'TELECINE PREMIUM HD',
                        'TELECINE PREMIUM HD [Alter]', 'TELECINE PREMIUM [Alter]'],
    "TelecineTouch": ['TELECINE TOUCH', 'TELECINE TOUCH [Alter]', 'TELECINE TOUCH FHD', 'TELECINE TOUCH HD',
                      'TELECINE TOUCH HD [Alter]'],
    "TLC": ['TLC FHD', 'TLC HD', 'TLC HD [Alter]', 'TLC SD', 'TLC [Alter]'],
    "TNT": ['TNT SD', 'TNT [Alter]', 'TNT FHD', 'TNT HD', 'TNT HD [Alter]'],
    "TNTSeries": ['TNT SERIES FHD', 'TNT SERIES HD', 'TNT SERIES SD', 'TNT Series HD [Alter]', 'TNT Series [Alter]'],
    "Tooncast": ['TOONCAST SD'],
    "TruTV": ['TRUTV FHD', 'TruTV HD', 'TruTV SD'],
    "TV Aparecida": ['TV APARECIDA', 'TV APARECIDA [Alter]'],
    "Universal": ['UNIVERSAL CHANNEL FHD', 'UNIVERSAL CHANNEL HD', 'UNIVERSAL CHANNEL SD',
                  'Universal Channel HD [Alter]', 'Universal Channel [Alter]'],
    "Venus": ['VENUS', 'VENUS [Alter]'],
    "VH1": ['VH1 FHD', 'VH1 HD', 'VH1 HD [Alter]', 'VH1 SD'],
    "VH1 MegaHits": ['VH1 MEGA HITS SD', 'VH1 Mega Hits [Alter]'],
    "Viva": ['VIVA FHD', 'VIVA HD', 'VIVA SD', 'VIVA [Alter]', 'Viva HD [Alter]'],
    "Warner": ['WARNER CHANNEL HD', 'WARNER CHANNEL SD', 'WARNER FHD', 'Warner Channel [Alter]', 'Warner HD [Alter]'],
    "WooHoo": ['WOOHOO FHD', 'WOOHOO HD', 'WOOHOO SD', 'Woohoo HD [Alter]', 'Woohoo [Alter]']
}


def main(iptv_filename, enable_vod_update):
    print("Reading m3u file")
    fixer = M3uFixer(iptv_filename, channel_id_dic, enable_vod_update)
    fixer.fixLines()
    # with open("playlist.m3u", 'r', encoding='utf8') as playlist:
    #     print(playlist.read())

main(sys.argv[0], sys.argv[1])