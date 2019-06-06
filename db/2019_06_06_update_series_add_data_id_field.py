from repository import repository

print("Adding field data_id with default value NO_DATA")
docs = repository.series().all()
for doc in docs:
    doc['data_id'] = 'NO_DATA'
repository.series().write_back(docs)
