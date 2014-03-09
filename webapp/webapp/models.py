from rtree import index
from pymongo import MongoClient

# Load the r-tree index
p = index.Property()
p.dimension = 3
idx = index.Index('3d_index', properties=p)

# Setup connection to Mongo
client = MongoClient()
db = client.local

# Collections
col = db.echonest_data
queries = db.queries
