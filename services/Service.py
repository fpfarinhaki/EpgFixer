import logging

from tinydb import Query

from io_operations import M3uWriter
from services import ShowDataService
from tinydb import operations


class Service(object):

    def __init__(self, file_writer: M3uWriter, mdb_service: ShowDataService):
        self.file_writer = file_writer
        self.mdb_service = mdb_service

    def save(self, m3u_list):
        pass

    def update_m3u_entity(self, m3u_entity_list, db):
        logging.debug("Updating {} with {} M3U Entities".format(db, len(m3u_entity_list)))
        to_insert = []
        for m3uEntity in m3u_entity_list:
            if not (db.contains(Query().tvg_name == m3uEntity.tvg_name)):
                logging.debug("Inserting new M3U entity {} - insert".format(m3uEntity))
                to_insert.append(vars(m3uEntity))
            else:
                db.update(operations.set("link", m3uEntity.link), Query().tvg_name == m3uEntity.tvg_name)
        db.insert_multiple(to_insert)
