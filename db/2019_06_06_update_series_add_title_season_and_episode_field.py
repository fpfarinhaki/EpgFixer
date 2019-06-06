from repository import repository

print("Adding field data_id with default value NO_DATA")
docs = repository.series().all()
for doc in docs:
    doc['title'] = ''
    doc['season'] = '1'
    doc['episode'] = '1'
repository.series().write_back(docs)
