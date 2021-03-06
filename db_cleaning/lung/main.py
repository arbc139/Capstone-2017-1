#!/usr/bin/python

from urllib.parse import quote
import difflib
import math
import pymysql
import re
import sys
import time

get_current_millis = lambda: int(round(time.time() * 1000))
def get_elapsed_seconds(current_time, elapsed_millis):
  return (current_time - elapsed_millis) / 1000.0

if len(sys.argv) < 2:
  raise RuntimeError('Need to set column name')

COLUMN_NAME = sys.argv[1]

START_S_ID = None
if len(sys.argv) > 2:
  START_S_ID = sys.argv[2]

db = pymysql.connect(host='localhost', user='root', password='', db='mesh', charset='utf8')

elapsed_millis = get_current_millis()
# Get '${symbol}' type genes in DB.
all_genes = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  query = 'SELECT * FROM LUNG_GENES WHERE %s REGEXP "\'.*\'" ORDER BY S_ID' % (COLUMN_NAME) if START_S_ID is None \
    else 'SELECT * FROM LUNG_GENES WHERE %s REGEXP "\'.*\'" AND S_ID > %s ORDER BY S_ID' % (COLUMN_NAME, START_S_ID)
  cursor.execute(query)
  all_genes = cursor.fetchall()
print('Find type genes time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

# Find with checking family
values = []
for gene in all_genes:
  if not re.match('\'.*\'', gene[COLUMN_NAME]):
    continue

  print('UPDATE LUNG_GENES SET %s=%s WHERE S_ID=%s' % (
    COLUMN_NAME, gene[COLUMN_NAME][1:-1], gene['S_ID']))
  values.append([gene[COLUMN_NAME][1:-1], gene['S_ID']])

elapsed_millis = get_current_millis()
# Send a query to update LUNG_GENES.
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  cursor.executemany(
    'UPDATE LUNG_GENES SET %s' % (COLUMN_NAME) + '=%s WHERE S_ID=%s',
    values
  )
db.commit()
print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
