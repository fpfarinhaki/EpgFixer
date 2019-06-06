from tinydb import where
from tinydb.operations import set

from repository import repository

repository.series().update(set('data_id', 'NO_DATA'), where('doc_id') > 0)
