" Userman: Dump the database into a JSON file."

import json
import tarfile
from cStringIO import StringIO

from userman import utils
from userman import constants


def dump(db, filename):
    """Dump contents of the database to a tar file, optionally compressed.
    Return the number of items, and the number of attachment files dumped."""
    count_items = 0
    count_files = 0
    if filename.endswith('.gz'):
        mode = 'w:gz'
    elif filename.endswith('.bz2'):
        mode = 'w:bz2'
    else:
        mode = 'w'
    outfile = tarfile.open(filename, mode=mode)
    for key in db:
        if not constants.IUID_RX.match(key): continue
        doc = db[key]
        del doc['_rev']
        info = tarfile.TarInfo(doc['_id'])
        data = json.dumps(doc)
        info.size = len(data)
        outfile.addfile(info, StringIO(data))
        count_items += 1
        for attname in doc.get('_attachments', dict()):
            info = tarfile.TarInfo("{0}_att/{1}".format(doc['_id'], attname))
            attfile = db.get_attachment(doc, attname)
            data = attfile.read()
            attfile.close()
            info.size = len(data)
            outfile.addfile(info, StringIO(data))
            count_files += 1
    outfile.close()
    return count_items, count_files

def undump(db, filename):
    """Reverse of dump; load all items from a tar file.
    Items are just added to the database, ignoring existing items."""
    count_items = 0
    count_files = 0
    attachments = dict()
    infile = tarfile.open(filename, mode='r')
    for item in infile:
        itemfile = infile.extractfile(item)
        itemdata = itemfile.read()
        itemfile.close()
        if item.name in attachments:
            # This relies on an attachment being after its item in the tarfile.
            db.put_attachment(doc, itemdata, **attachments.pop(item.name))
            count_files += 1
        else:
            doc = json.loads(itemdata)
            # If the user document already exists, do not load again.
            if doc[constants.DB_DOCTYPE] == constants.USER:
                rows = db.view('user/email', key=doc['email'])
                if len(list(rows)) != 0: continue
            atts = doc.pop('_attachments', dict())
            db.save(doc)
            count_items += 1
            for attname, attinfo in atts.items():
                key = "{0}_att/{1}".format(doc['_id'], attname)
                attachments[key] = dict(filename=attname,
                                        content_type=attinfo['content_type'])
    infile.close()
    return count_items, count_files


if __name__ == '__main__':
    import sys
    try:
        utils.load_settings(filepath=sys.argv[1])
    except IndexError:
        utils.load_settings()
    db = utils.get_db()
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = 'dump.tar.gz'
    count_items, count_files = dump(db, filename)
    print 'dumped', count_items, 'items and', count_files, 'files to', filename
