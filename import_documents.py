#!/bin/python
import MySQLdb
import argparse
import magic
import os
import uuid
from .config import HOST, USER, PASSWD, DB, SUGARDIR


parser = argparse.ArgumentParser(description='Import documents to SugarCRM')
parser.add_argument('directory', metavar='dir', type=str,
    help='directory to import documents')
parser.add_argument('--existing', dest='existing', action='store_true',
    help='Skip existing documents')
parser.set_defaults(existing=False)
args = parser.parse_args()

db = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB)
cur = db.cursor()

mime = magic.open(magic.MAGIC_MIME)
mime.load()

for root, dirs, files in os.walk(args.directory):
    for file in files:
        file_id = uuid.uuid4()
        revision_id = uuid.uuid4()
        ext = file.split('.')[-1]
        try:
            mime_type = mime.file(os.path.join(args.directory, file))
            mime_type = mime_type.split(";")[0]
            if len(mime_type) == 0:
                mime_type = 'text/plain'
        except:
            mime_type = 'text/plain'

        try:
            if args.existing:
                cur.execute("SELECT id from documents where document_name = '%s'"
                        % (file))
                row = cur.fetchone()
                if row:
                        continue
            cur.execute("INSERT INTO documents "
                "(id,document_name,status_id,document_revision_id,active_date,"
                "created_by) "
                " VALUES ('%s','%s','Active','%s',NOW(),'1') "
                % (file_id, file, revision_id))
            cur.execute("INSERT INTO document_revisions (id,document_id,"
                "revision,change_log,filename,file_ext,file_mime_type, "
                "doc_type,created_by) VALUES ('%s','%s',1,'Documento Creado',"
                "'%s','%s','%s','Sugar','1') "
                % (revision_id, file_id, file, ext, mime_type))
            relation_id = uuid.uuid4()
            #Move file to upload/%(revision_id)s
            os.rename(os.path.join(root, file), os.path.join(SUGARDIR,
                    str(revision_id)))
        except:
            pass

cur.close()
