import sqlite3
import csv
import pprint

conn = sqlite3.connect('denver_boulder.db')
c = conn.cursor()

# c.execute('CREATE TABLE nodes (id integer primary key, lat real, lon real, user text, uid integer, version text, changeset integer, timestamp text)')
# c.execute('CREATE TABLE node_tags (id integer references nodes, key text, value text, type text)')
#
# c.execute('CREATE TABLE ways (id integer primary key, user text, uid integer, version text, changeset integer, timestamp text)')
# c.execute('CREATE TABLE way_nodes (id integer references ways, node_id integer, position integer)')
# c.execute('CREATE TABLE way_tags (id integer references ways, key text, value text, type text)')

# with open('nodes.csv','rb') as f:
#     dr = csv.DictReader(f) # comma is default delimiter
#     to_db = [(i['id'].decode("utf-8"), i['lat'].decode("utf-8"),i['lon'].decode("utf-8"), i['user'].decode("utf-8"),
#               i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"),
#               i['timestamp'].decode("utf-8")) for i in dr]
# c.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)

# with open('nodes_tags.csv','rb') as f:
#     dr = csv.DictReader(f) # comma is default delimiter
#     to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"),i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]
# c.executemany("INSERT INTO node_tags(id, key, value, type) VALUES (?, ?, ?, ?);", to_db)

# with open('ways.csv','rb') as f:
#     dr = csv.DictReader(f) # comma is default delimiter
#     to_db = [(i['id'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"),
#               i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) for i in dr]
# c.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)

# with open('ways_nodes.csv','rb') as f:
#     dr = csv.DictReader(f) # comma is default delimiter
#     to_db = [(i['id'].decode("utf-8"), i['node_id'].decode("utf-8"),i['position'].decode("utf-8")) for i in dr]
# c.executemany("INSERT INTO way_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db)
#
#
# with open('ways_tags.csv','rb') as f:
#     dr = csv.DictReader(f) # comma is default delimiter
#     to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"),i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]
# c.executemany("INSERT INTO way_tags(id, key, value, type) VALUES (?, ?, ?, ?);", to_db)

# conn.commit()


QUERY = 'SELECT COUNT(*) FROM (SELECT key, value FROM node_tags UNION ALL SELECT key, value FROM way_tags WHERE \
        key = "addr:postcode" AND value = "80304") '

c.execute(QUERY)
result =c.fetchall()
pprint.pprint(result)

conn.close()