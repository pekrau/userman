" Userman: Load all CouchDB database design documents. "

import os


def load_designs(db, root='designs'):
    for design in os.listdir(root):
        views = dict()
        path = os.path.join(root, design)
        if not os.path.isdir(path): continue
        path = os.path.join(root, design, 'views')
        for filename in os.listdir(path):
            name, ext = os.path.splitext(filename)
            if ext != '.js': continue
            with open(os.path.join(path, filename)) as codefile:
                code = codefile.read()
            if name.startswith('map_'):
                name = name[len('map_'):]
                key = 'map'
            elif name.startswith('reduce_'):
                name = name[len('reduce_'):]
                key = 'reduce'
            else:
                key = 'map'
            views.setdefault(name, dict())[key] = code
        doc = dict(_id="_design/%s" % design, views=views)
        try:
            doc['_rev'] = db.revisions(doc['_id']).next().rev
        except StopIteration:
            pass
        db.save(doc)


if __name__ == '__main__':
    import sys
    from userman import utils
    try:
        utils.load_settings(filepath=sys.argv[1])
    except IndexError:
        utils.load_settings()
    db = utils.get_db()
    load_designs(db)
