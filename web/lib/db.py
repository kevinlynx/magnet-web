# kevinlynx@gmail.com
# 03.10.2016
from contextlib import closing
import MySQLdb

'''
to keep a long connection to mysql looks like some bugs there which many cause 'MySQL down exception',
to simply solve this is to create a short connection.
'''
class ShortConn(object):
    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql, *args):
        rows = []
        with closing(self.conn.cursor(MySQLdb.cursors.DictCursor)) as cur:
            cur.execute(sql, *args)
            rows = cur.fetchall() 
        self.conn.close()
        return rows

class DBConn(object):
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.conn = MySQLdb.connect(host, user, pwd, db, charset='utf8')

    def execute_short(self, sql, *args):
        conn = ShortConn(MySQLdb.connect(self.host, self.user, self.pwd, self.db, charset='utf8'))
        return conn.execute(sql, *args)

    def update(self, sql, *args):
        conn = MySQLdb.connect(self.host, self.user, self.pwd, self.db, charset='utf8')
        with closing(conn.cursor()) as cur:
            cur.execute(sql, *args)
            conn.commit()
        conn.close()

    '''
    when the crawler inserted new records, this client (if still running) can't select these
    latest inserted records on the same connection! i googled around, even changed another 
    library, still not figured it out. But, to create a new connection can solve this problem.
    '''
    def _reset(self):
        self.conn.close()
        self.conn = MySQLdb.connect(self.host, self.user, self.pwd, self.db, charset='utf8')

    def __del__(self):
        self.conn.close()

