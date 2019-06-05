# This Python file uses the following encoding: utf-8
from helpers import m3uCollectors
from helpers.m3uCollectors import *

channel = M3uEntity(
    '#EXTINF:-1 tvg-id="Animal  Planet FHD" tvg-name="ANIMAL  PLANET FHD" tvg-logo="http://i.imgur.com/J1oK0xW.png" group-title="Canais: Documentários",ANIMAL  PLANET FHD',
    'http://srv.mtvs.me:8880/sdrehBge0F/Z2Gda3tzQb/28782')
movie = M3uEntity(
    '#EXTINF:-1 tvg-id="" tvg-name="O Culto" tvg-logo="http://painel.iptvmove.com:80/images/uVHPBTLb6Sj1Eso9HzyBAOMRheM_small.jpg" group-title="Filme: Terror",O Culto',
    'http://srv.mtvs.me:8880/movie/sdrehBge0F/Z2Gda3tzQb/16198.mp4')
serie = M3uEntity(
    '#EXTINF:-1 tvg-id="" tvg-name="O Conto da Aia (The Handmaid\'s Tale) S02 E12" tvg-logo="http://painel.iptvmove.com:8880/images/szTXwJyWKVKgmWLvhtdQsSeadRZ_small.jpg" group-title="Série: O Conto da Aia (The Handmaid\'s Tale)",O Conto da Aia (The Handmaid\'s Tale) S02 E12',
    'http://srv.mtvs.me:8880/series/sdrehBge0F/Z2Gda3tzQb/26573.mp4')
filme_adulto = M3uEntity(
    '#EXTINF:-1 tvg-id="" tvg-name="A Casa das Brasileirinhas - A Nova Fernandinha Fernandez" tvg-logo="https://www.chocolatefx.ca/wp-content/uploads/2017/11/Adults-Only-Chocolate.jpg" group-title="Filme: Adultos",A Casa das Brasileirinhas - A Nova Fernandinha Fernandez',
    'http://srv.mtvs.me:8880/movie/sdrehBge0F/Z2Gda3tzQb/14965.mp4')
canal_adulto = M3uEntity(
    '#EXTINF:-1 tvg-id="Sexy Hot" tvg-name="SEXY HOT" tvg-logo="http://i.imgur.com/jv8XhSR.png" group-title="Canais: Adultos",SEXY HOT',
    'http://srv.mtvs.me:8880/sdrehBge0F/Z2Gda3tzQb/28405'
)
canal_24_horas = M3uEntity(
    '#EXTINF:-1 tvg-id="" tvg-name="POWER COUPLE BRASIL HD" tvg-logo="https://upload.wikimedia.org/wikipedia/pt/thumb/b/bf/Power_Couple_Brasil.jpg/260px-Power_Couple_Brasil.jpg" group-title="Canais: 24 Hrs",POWER COUPLE BRASIL HD',
    'http://srv.mtvs.me:8880/sdrehBge0F/Z2Gda3tzQb/30946'
)
radio = M3uEntity(
    '#EXTINF:-1 tvg-id="" tvg-name="Radio Mania Melody" tvg-logo="http://iconbug.com/data/c0/347/2ca8069df1ccf87f23afe60b26faae1e.png" group-title="Rádios",Radio Mania Melody',
    'http://srv.mtvs.me:8880/sdrehBge0F/Z2Gda3tzQb/29119'
)
channel_id_dic = {
    "A&E": ['A&E', 'A&E FHD', 'A&E HD', 'A&E HD [Alter]', 'A&E [Alter]'],
    "Animal Planet": ['ANIMAL  PLANET FHD', 'ANIMAL PLANET', 'ANIMAL PLANET HD', 'ANIMAL PLANET HD [Alter]',
                      'ANIMAL PLANET [Alter]']
}
test_data = [channel, movie, serie, filme_adulto, canal_adulto, canal_24_horas, radio]

print(m3uCollectors.collect(test_data, M3uMovieCollector()))
print(m3uCollectors.collect(test_data, M3uChannelCollector(channel_id_dic)))
print(m3uCollectors.collect(test_data, M3uAdultCollector()))
print(m3uCollectors.collect(test_data, M3uRadioCollector()))
