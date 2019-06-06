from tinydb import where
from tinydb.operations import add

from repository import repository

print("Adding field data_id with default value NO_DATA ")
repository.series().update(add('data_id', 'NO_DATA'), where('doc_id') > 0)
