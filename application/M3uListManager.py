"""M3U List Manager CLI
Usage:
    M3uListManager [options] (--m3u-file filename | --update-db script)

Options:
-h --help               show this
--m3u-file <filename>   save to file
--update-db <script>    update db using script provided
--debug                 show debug information
--quiet                 display errors only

"""
import logging
import runpy
from concurrent.futures.thread import ThreadPoolExecutor
from logging.handlers import TimedRotatingFileHandler

from docopt import docopt

from io_operations.M3uTransformer import M3uTransformer
from services import service, tmdb

console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(message)s')
console_handler.setFormatter(formatter)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    handlers=[TimedRotatingFileHandler(filename='M3U_FIXER.log', encoding='utf-8'),
                              console_handler], level=logging.DEBUG)

channel_id_dic = {
    "A&E": ['A&E', 'A&E FHD', 'A&E HD', 'A&E HD [Alter]', 'A&E [Alter]'],
    "AMC": ['AMC', 'AMC FHD', 'AMC HD', 'AMC HD [Alter]', 'AMC [Alter]'],
    "Animal Planet": ['ANIMAL  PLANET FHD', 'ANIMAL PLANET', 'ANIMAL PLANET HD', 'ANIMAL PLANET HD [Alter]',
                      'ANIMAL PLANET [Alter]'],
    "Arte 1": ['ARTE 1', 'ARTE 1 FHD', 'ARTE 1 HD', 'ARTE 1 [Alter]'],
    "AXN": ['AXN FHD', 'AXN HD', 'AXN HD [Alter]', 'AXN SD', 'AXN [Alter]'],
    "Baby Tv": ['BABY TV', 'BABY TV [Alter]'],
    "Band": ['BAND HD [Alter]', 'BAND SP', 'BAND SP FHD', 'BAND SP HD', 'BAND SP [Alter]'],
    "Band News": ['BAND NEWS', 'BAND NEWS FHD', 'BAND NEWS HD', 'BAND NEWS [Alter]'],
    "Band Sports": ['BAND SPORTS', 'BAND SPORTS FHD', 'BAND SPORTS HD', 'BAND SPORTS [Alter]',
                    'Band Sports HD [Alter]'],
    "BIS": ['BIS', 'BIS FHD', 'BIS HD', 'BIS [Alter]', 'Bis HD [Alter]'],
    "Boomerang": ['BOOMERANG', 'BOOMERANG  FHD', 'BOOMERANG HD', 'BOOMERANG [Alter]', 'Boomerang HD [Alter]'],
    "Canal Brasil": ['CANAL BRASIL', 'CANAL BRASIL FHD', 'CANAL BRASIL HD', 'CANAL BRASIL [Alter]'],
    "Canção Nova": ['CANÇÃO NOVA', 'CANÇÃO NOVA [Alter]'],
    "Cartoon Network": ['CARTOON NETWORK', 'CARTOON NETWORK FHD', 'CARTOON NETWORK HD', 'CARTOON NETWORK [Alter]',
                        'Cartoon Network HD [Alter]'],
    "Cinemax": ['CINEMAX', 'CINEMAX FHD', 'CINEMAX HD', 'CINEMAX [Alter]', 'Cinemax HD [Alter]'],
    "Combate": ['COMBATE', 'COMBATE FHD', 'COMBATE HD', 'Combate HD [Alter]', 'Combate [Alter]'],
    "Comedy Central": ['COMEDY CENTRAL', 'COMEDY CENTRAL FHD', 'COMEDY CENTRAL HD', 'Comedy Central HD [Alter]',
                       'Comedy Central [Alter]'],
    "Cultura": ['TV CULTURA FHD', 'TV CULTURA HD', 'TV CULTURA SD', 'TV Cultura [Alter]'],
    "DAZN1": ['DAZN 1 FHD', 'DAZN 1 HD', 'DAZN 1 SD'],
    "DAZN2": ['DAZN 2 FHD', 'DAZN 2 HD', 'DAZN 2 SD'],
    "DAZN3": ['DAZN 3 FHD', 'DAZN 3 HD', 'DAZN 3 SD'],
    "Discovery Channel": ['DISCOVERY CHANNEL', 'DISCOVERY CHANNEL FHD', 'DISCOVERY CHANNEL HD',
                          'Discovery Channel HD [Alter]', 'Discovery Channel [Alter]'],
    "Discovery Civilization": ['DISCOVERY CIVILIZATION', 'DISCOVERY CIVILIZATION FHD', 'DISCOVERY CIVILIZATION HD',
                               'Discovery Civilization HD [Alter]'],
    "Discovery Home & Health": ['DISCOVERY HOME & HEALTH', 'DISCOVERY HOME & HEALTH FHD',
                                'DISCOVERY HOME & HEALTH HD', 'Discovery H&H [Alter]',
                                'Discovery Home & Helth HD [Alter]'],
    "Discovery Kids": ['DISCOVERY KIDS', 'DISCOVERY KIDS FHD', 'DISCOVERY KIDS HD', 'DISCOVERY KIDS [Alter]',
                       'Discovery Kids HD [Alter]'],
    "Discovery Science": ['DISCOVERY SCIENCE', 'DISCOVERY SCIENCE FHD', 'DISCOVERY SCIENCE HD',
                          'Discovery Science HD [Alter]'],
    "Discovery Theater": ['DISCOVERY THEATER', 'DISCOVERY THEATER FHD', 'DISCOVERY THEATER HD',
                          'Discovery Theater HD [Alter]'],
    "Discovery Turbo": ['DISCOVERY TURBO', 'DISCOVERY TURBO FHD', 'DISCOVERY TURBO HD', 'Discovery Turbo HD [Alter]',
                        'Discovery Turbo [Alter]'],
    "Discovery world": ['DISCOVERY WORLD', 'DISCOVERY WORLD  HD', 'DISCOVERY WORLD FHD',
                        'Discovery World HD [Alter]'],
    "Disney Channel": ['DISNEY CHANNEL', 'DISNEY CHANNEL FHD', 'DISNEY CHANNEL HD', 'Disney Channel HD [Alter]',
                       'Disney [Alter]'],
    "Disney JR": ['DISNEY JR FHD', 'DISNEY JR HD', 'DISNEY JR SD', 'Disney JR [Alter]'],
    "Disney XD": ['DISNEY XD SD', 'Disney XD [Alter]'],
    "E!": ['E! FHD', 'E! HD', 'E! HD [Alter]', 'E! SD', 'E! [Alter]'],
    "EI2": ['EI PLUS 2 HD', 'EI PLUS 2 SD'],
    "EI3": ['EI PLUS 3 HD', 'EI PLUS 3 SD'],
    "EI": ['EI PLUS HD*', 'EI PLUS SD*'],
    "ESPN": ['ESPN   [Alter]', 'ESPN FHD', 'ESPN HD', 'ESPN HD [Alter]', 'ESPN SD', 'ESPN [Alter]'],
    "ESPN 2": ['ESPN 2 FHD', 'ESPN 2 HD', 'ESPN 2 HD [Alter]', 'ESPN 2 SD'],
    "ESPN Brasil": ['ESPN BRASIL FHD', 'ESPN BRASIL HD', 'ESPN BRASIL HD [Alter]', 'ESPN BRASIL SD',
                    'Espn Brasil [Alter]'],
    "ESPN Extra": ['ESPN EXTRA HD', 'ESPN EXTRA SD', 'ESPN Extra FHD', 'ESPN Extra HD [Alter]', 'ESPN Plus HD [Alter]'],
    "Film&Arts": ['FILM & ARTS SD'],
    "FISH TV": ['FISH TV FHD', 'FISH TV HD', 'FISH TV SD', 'Fish TV HD [Alter]', 'Fish TV [Alter]'],
    "Food Network": ['FOOD NETWORK FHD', 'FOOD NETWORK HD', 'FOOD NETWORK SD', 'Food Network HD [Alter]',
                     'Food Network [Alter]'],
    "FOX": ['FOX FHD', 'FOX HD', 'FOX SD', 'Fox 1 HD [Alter]', 'Fox HD [Alter]', 'Fox [Alter]'],
    "Fox Life": ['FOX LIFE FHD', 'FOX LIFE HD', 'FOX LIFE SD', 'Fox Life HD [Alter]', 'Fox Life [Alter]'],
    "Fox Sports": ['FOX SPORTS FHD', 'FOX SPORTS HD', 'FOX SPORTS HD [Alter]', 'FOX SPORTS SD', 'FOX SPORTS [Alter]'],
    "FOX Sports 2": ['FOX SPORTS 2 FHD', 'FOX SPORTS 2 HD', 'FOX SPORTS 2 SD', 'Fox Sports 2 HD [Alter]',
                     'Fox Sports 2 [Alter]'],
    "Futura": ['FUTURA FHD', 'FUTURA HD', 'FUTURA SD'],
    "FX": ['FX FHD', 'FX HD', 'FX HD [Alter]', 'FX SD', 'FX [Alter]'],
    "GloboRpc": ['GLOBO RPC CURITIBA FHD', 'GLOBO RPC CURITIBA HD', 'GLOBO RPC CURITIBA SD', 'RPC Curitiba [Alter]',
                 'GLOBO RPC FOZ DO IGUACU HD'],
    "GloboNews": ['GLOBO NEWS', 'GLOBO NEWS FHD', 'GLOBO NEWS HD', 'GLOBO NEWS HD [Alter]', 'GLOBO NEWS [Alter]'],
    "Gloob": ['GLOOB FHD', 'GLOOB HD', 'GLOOB SD', 'Gloob HD [Alter]', 'Gloob [Alter]'],
    "Gloobinho": ['GLOOBINHO FHD', 'GLOOBINHO HD', 'GLOOBINHO SD'],
    "Mais Globosat": ['MAIS GLOBOSAT FHD', 'MAIS GLOBOSAT HD', 'MAIS GLOBOSAT SD'],
    "GNT": ['GNT', 'GNT FHD', 'GNT HD', 'GNT HD [Alter]', 'GNT [Alter]'],
    "HBO 2": ['HBO 2 FHD', 'HBO 2 HD', 'HBO 2 HD [Alter]', 'HBO 2 SD', 'HBO 2 [Alter]'],
    "HBO Family": ['HBO FAMILY FHD', 'HBO FAMILY HD', 'HBO FAMILY SD', 'HBO Family HD [Alter]', 'HBO Family [Alter]'],
    "HBO": ['HBO FHD', 'HBO HD', 'HBO HD [Alter]', 'HBO SD', 'HBO [Alter]'],
    "HBO Plus": ['HBO PLUS SD', 'HBO Plus [Alter]', 'HBO PLUS FHD', 'HBO PLUS HD', 'HBO Plus HD [Alter]'],
    "HBO Signature": ['HBO SIGNATURE FHD', 'HBO SIGNATURE HD', 'HBO SIGNATURE SD', 'HBO SIGNATURE [Alter]',
                      'HBO Signature HD [Alter]'],
    "History 2": ['H2 FHD', 'H2 HD', 'H2 SD', 'History 2 HD [Alter]', 'History 2 [Alter]'],
    "InvestigacaoDiscovery": ['INVESTIGATION DISCOVERY FHD', 'INVESTIGAÇÃO DISCOVERY', 'INVESTIGAÇÃO DISCOVERY HD',
                              'INVESTIGAÇÃO DISCOVERY HD [Alter]', 'INVESTIGAÇÃO DISCOVERY [Alter]'],
    "Lifetime": ['LIFETIME', 'LIFETIME FHD', 'LIFETIME HD', 'Life Time HD [Alter]', 'Life Time [Alter]'],
    "Max": ['MAX FHD', 'MAX HD', 'MAX SD', 'MAX UP FHD', 'MAX UP HD', 'MAX UP SD', 'Max HD [Alter]', 'Max [Alter]'],
    "Max Prime": ['MAX PRIME FHD', 'MAX PRIME HD', 'MAX PRIME SD', 'Max Prime HD [Alter]', 'Max Prime [Alter]'],
    "Megapix": ['MEGAPIX FHD', 'MEGAPIX HD', 'MEGAPIX SD', 'Megapix HD [Alter]', 'Megapix [Alter]'],
    "MTV": ['MTV', 'MTV FHD', 'MTV HD', 'MTV HD [Alter]', 'MTV [Alter]'],
    "MTV Live": ['MTV LIVE FHD', 'MTV LIVE HD', 'MTV LIVE SD'],
    "Multishow": ['MULTISHOW', 'MULTISHOW FHD', 'MULTISHOW HD', 'Multishow HD [Alter]', 'Multishow [Alter]'],
    "Music Box Brazil": ['MUSIC BOX BRASIL FHD', 'MUSIC BOX BRASIL HD', 'MUSIC BOX BRASIL SD',
                         'Music Box Brasil [Alter]'],
    "Max UP": ['Max UP HD [Alter]', 'Max UP [Alter]'],
    "NatGeo": ['NAT GEO FHD', 'NAT GEO HD', 'NAT GEO SD', 'NatGeo HD [Alter]', 'NatGeo [Alter]'],
    "NatGeo Kids": ['NAT GEO KIDS FHD', 'NAT GEO KIDS HD', 'NAT GEO KIDS SD', 'NatGeo Kids HD [Alter]',
                    'NatGeo Kids [Alter]'],
    "NatGeo Wild": ['NAT GEO WILD FHD', 'NAT GEO WILD HD', 'NAT GEO WILD SD', 'NatGeo Wild HD [Alter]',
                    'NatGeo Wild [Alter]'],
    "NBR": ['NBR', 'NBR [Alter]'],
    "NHK World Premium": ['NHK [Alter]'],
    "Nick Jr": ['NICK JR FHD', 'NICK JR HD', 'NICK JR SD', 'Nick JR HD [Alter]', 'Nick JR [Alter]'],
    "Nickelodeon": ['NICKELODEN SD', 'NICKELODEON FHD', 'NICKELODEON HD', 'Nickelodeon HD [Alter]',
                    'Nickelodeon [Alter]'],
    "Off": ['OFF FHD', 'OFF HD', 'OFF HD [Alter]', 'OFF SD', 'OFF [Alter]'],
    "Paramount": ['PARAMOUNT CHANNEL  [Alter]', 'PARAMOUNT CHANNEL FHD', 'PARAMOUNT CHANNEL HD',
                  'PARAMOUNT CHANNEL HD [Alter]', 'PARAMOUNT CHANNEL SD'],
    "Playboy": ['PLAYBOY', 'PLAYBOY FHD', 'PLAYBOY HD', 'PLAYBOY HD [Alter]', 'PLAYBOY [Alter]'],
    "Play TV": ['Play Tv [Alter]'],
    "Prime Box Brazil": ['PRIME BOX BRASIL FHD', 'PRIME BOX BRASIL HD', 'PRIME BOX BRASIL SD',
                         'Prime Box Brasil [Alter]'],
    "Premiere Clubes": ['PREMIERE CLUBES FHD', 'Premiere Clubes HD', 'Premiere Clubes HD [Alter]', 'Premiere Clubes SD',
                        'Premiere Clubes [Alter]'],
    "Premiere 2": ['PREMIERE 2 FHD', 'PREMIERE 2 HD', 'PREMIERE 2 SD', 'Premiere 2 HD [Alter]', 'Premiere 2 [Alter]'],
    "Premiere 3": ['PREMIERE 3 FHD', 'PREMIERE 3 HD', 'PREMIERE 3 SD', 'Premiere 3 HD [Alter]', 'Premiere 3 [Alter]'],
    "Premiere 4": ['PREMIERE 4 FHD', 'PREMIERE 4 HD', 'PREMIERE 4 SD', 'Premiere 4 HD [Alter]', 'Premiere 4 [Alter]'],
    "Premiere 5": ['PREMIERE 5 FHD', 'PREMIERE 5 HD', 'PREMIERE 5 SD', 'Premiere 5 HD [Alter]', 'Premiere 5 [Alter]'],
    "Premiere 6": ['PREMIERE 6 FHD', 'PREMIERE 6 HD', 'PREMIERE 6 SD', 'Premiere 6 HD [Alter]', 'Premiere 6 [Alter]'],
    "Premiere 7": ['PREMIERE 7 FHD', 'PREMIERE 7 HD', 'PREMIERE 7 SD', 'Premiere 7 HD [Alter]', 'Premiere 7 [Alter]'],
    "Premiere 8": ['Premiere 8 [Alter]'],
    "TV Ra Tim Bum": ['TV RA TIM BUM FHD', 'TV RA TIM BUM HD', 'TV RA TIM BUM SD', 'TV RA TIM BUM [Alter]'],
    "Record": ['RECORD HD Alternativo', 'RECORD HD [Alter]', 'RECORD [Alter]'],
    "Record News": ['RECORD NEWS', 'RECORD NEWS FHD', 'RECORD NEWS HD', 'RECORD NEWS [Alter]', 'RIT'],
    "Rede TV": ['REDE TV', 'REDE TV FHD', 'REDE TV HD', 'REDE TV HD [Alter]', 'REDE TV [Alter]'],
    "Rede Vida": ['REDE VIDA', 'REDE VIDA FHD', 'REDE VIDA HD', 'REDE VIDA [Alter]'],
    "SBT": ['SBT', 'SBT FHD', 'SBT HD', 'SBT HD [Alter]', 'SBT SP INTERIOR', 'SBT [Alter]'],
    "Sextreme": ['SEXTREME', 'SEXTREME [Alter]'],
    "Sexy Hot": ['SEXY HOT', 'SEXY HOT [Alter]'],
    "SIC International": ['SIC Internacional [Alter]'],
    "Smithsonian": ['SMITHSONIAN CHANNEL FHD', 'SMITHSONIAN CHANNEL HD', 'SMITHSONIAN CHANNEL SD'],
    "Space": ['SPACE FHD', 'SPACE HD', 'SPACE SD', 'Space HD [Alter]', 'Space [Alter]'],
    "SporTV": ['SPORTV FHD', 'SPORTV HD', 'SPORTV SD', 'Sportv HD [Alter]', 'Sportv [Alter]'],
    "SporTV 2": ['SPORTV 2 FHD', 'SPORTV 2 HD', 'SPORTV 2 SD', 'Sportv 2 HD [Alter]', 'Sportv 2 [Alter]'],
    "SporTV 3": ['SPORTV 3 FHD', 'SPORTV 3 HD', 'SPORTV 3 SD', 'Sportv 3 HD [Alter]', 'Sportv 3 [Alter]'],
    "Studio Universal": ['STUDIO UNIVERSAL FHD', 'STUDIO UNIVERSAL HD', 'STUDIO UNIVERSAL SD',
                         'Studio Universal HD [Alter]', 'Studio Universal [Alter]'],
    "Syfy": ['SYFY FHD', 'SYFY HD', 'SYFY SD', 'Syfy HD [Alter]', 'Syfy [Alter]'],
    "Sony": ['CANAL SONY', 'CANAL SONY FHD', 'CANAL SONY HD', 'Canal Sony HD [Alter]', 'Sony [Alter]'],
    "TBS": ['TBS FHD', 'TBS HD', 'TBS HD [Alter]', 'TBS SD', 'TBS [Alter]'],
    "TCM": ['TCM SD', 'TCM [Alter]'],
    "Telecine Action": ['TELECINE ACTION', 'TELECINE ACTION [Alter]', 'TELECINE ACTION FHD', 'TELECINE ACTION HD',
                        'TELECINE ACTION HD [Alter]'],
    "Telecine Cult": ['TELECINE CULT', 'TELECINE CULT FHD', 'TELECINE CULT HD', 'TELECINE CULT HD [Alter]',
                      'TELECINE CULT [Alter]'],
    "Telecine Fun": ['TELECINE FUN', 'TELECINE FUN [Alter]', 'TELECINE FUN FHD', 'TELECINE FUN HD',
                     'TELECINE FUN HD [Alter]'],
    "Telecine Pipoca": ['TELECINE PIPOCA', 'TELECINE PIPOCA [Alter]', 'TELECINE PIPOCA FHD', 'TELECINE PIPOCA HD',
                        'TELECINE PIPOCA HD [Alter]'],
    "Telecine Premium": ['TELECINE PREMIUM', 'TELECINE PREMIUM FHD', 'TELECINE PREMIUM HD',
                         'TELECINE PREMIUM HD [Alter]', 'TELECINE PREMIUM [Alter]'],
    "Telecine Touch": ['TELECINE TOUCH', 'TELECINE TOUCH [Alter]', 'TELECINE TOUCH FHD', 'TELECINE TOUCH HD',
                       'TELECINE TOUCH HD [Alter]'],
    "History": ['HISTORY SD', 'History [Alter]', 'HISTORY FHD', 'HISTORY HD', 'History HD [Alter]'],
    "TLC": ['TLC FHD', 'TLC HD', 'TLC HD [Alter]', 'TLC SD', 'TLC [Alter]'],
    "TNT": ['TNT SD', 'TNT [Alter]', 'TNT FHD', 'TNT HD', 'TNT HD [Alter]'],
    "TNT SERIES": ['TNT SERIES FHD', 'TNT SERIES HD', 'TNT SERIES SD', 'TNT Series HD [Alter]', 'TNT Series [Alter]'],
    "Tooncast": ['TOONCAST SD'],
    "Tru TV": ['TRUTV FHD', 'TruTV HD', 'TruTV SD'],
    "TV Aparecida": ['TV APARECIDA', 'TV APARECIDA [Alter]'],
    "Universal": ['UNIVERSAL CHANNEL FHD', 'UNIVERSAL CHANNEL HD', 'UNIVERSAL CHANNEL SD',
                  'Universal Channel HD [Alter]', 'Universal Channel [Alter]'],
    "Venus": ['VENUS', 'VENUS [Alter]'],
    "VH1": ['VH1 FHD', 'VH1 HD', 'VH1 HD [Alter]', 'VH1 SD'],
    "VH1 Megahits": ['VH1 MEGA HITS SD', 'VH1 Mega Hits [Alter]'],
    "Viva": ['VIVA FHD', 'VIVA HD', 'VIVA SD', 'VIVA [Alter]', 'Viva HD [Alter]'],
    "Warner": ['WARNER CHANNEL HD', 'WARNER CHANNEL SD', 'WARNER FHD', 'Warner Channel [Alter]', 'Warner HD [Alter]'],
    "Woohoo": ['WOOHOO FHD', 'WOOHOO HD', 'WOOHOO SD', 'Woohoo HD [Alter]', 'Woohoo [Alter]']
}


def main(iptv_filename):
    logging.info("Starting EPG and movie data process.")
    all_m3u = M3uTransformer(iptv_filename).transform()

    with ThreadPoolExecutor(thread_name_prefix='save_thread') as executor:
        movies_future = executor.submit(service.save_movies, all_m3u, tmdb)
        channel_future = executor.submit(service.save_channels, all_m3u, channel_id_dic)
        series_future = executor.submit(service.save_series, all_m3u, tmdb)
        # executor.submit(self.update_m3u_entity, self.adultos, repository.adult_movies())

        logging.debug("Future result for movie thread - {}".format(movies_future.result()))
        logging.debug("Future result for channels thread - {}".format(channel_future.result()))
        logging.debug("Future result for series thread - {}".format(series_future.result()))

    logging.info("EPG and show data process finished.")


if __name__ == '__main__':
    arguments = docopt(__doc__, version='M3U List Manager 1.0')
    console_handler.setLevel(logging.INFO)
    if arguments['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    elif arguments['--quiet']:
        logging.basicConfig(level=logging.ERROR)

    if arguments['--update-db']:
        runpy.run_path(arguments['--update-db'])
    else:
        main(arguments['--m3u-file'])
