#!/bin/python
import MySQLdb
import argparse
import os
from .config import HOST, USER, PASSWD, DB, SUGARDIR

parser = argparse.ArgumentParser(description='Test documents of SugarCRM')
parser.add_argument('--remove', type=bool, default=False,
    help='delete documents')
args = parser.parse_args()


db = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB)
cur = db.cursor()

cur.execute("SELECT id,filename FROM document_revisions")
rows = cur.fetchall()
to_delete = []
for row in rows:
    if os.path.isfile(os.path.join(SUGARDIR, row[0])):
        print "File %s (%s) exists" % (row[0], row[1])
    else:
        print "File %s (%s) doesn't exist!!" % (row[0], row[1])
        to_delete.append(row[0])
cur.close()
if args.remove:
    print "Removing unexistent files..."
    ids = ""
    for revision_id in to_delete:
        ids += "'%s'," % revision_id
    ids = ids[0:-1]
    sql = " delete from document_revisions where id in (%s)" % ids
    cur.execute(sql)
    sql = " delete from documents d where not exists (select id from"
    " document_revisions where document_id = d.id) "
    cur.execute(sql)
