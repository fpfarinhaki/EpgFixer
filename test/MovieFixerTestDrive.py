import sys

from MovieFixer import MovieFixer

sys.argv.append("Bohemian Rhapsody: Performance Completa no Live Aid 2019")
sys.argv.append("Bohemian Rhapsody: Recreating Live Aid")
print(sys.argv)
print("Fixing movies with no data found")
fixer = MovieFixer()
fixer.assign_data_to_movie_manually(sys.argv[1], sys.argv[2])
print("Finished fixing movies")


