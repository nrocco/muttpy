import sqlite3
import os
import logging
import ldap

from muttpy import __version__, DEFAULT_CONFIG
from ldapper.clients import LdapClient



log = logging.getLogger(__name__)

PROG = 'mutt-aliases'
DESC = '''Query an external LDAP directory and optionally cache the
results locally. As an alternative to provide command line options
you can create a file `%s` and place your default settings in a
section with the name %s.''' % (DEFAULT_CONFIG, PROG)



class AliasCache(object):
    QUERY = """SELECT * FROM alias WHERE name LIKE '%{q}%' OR nick LIKE '%{q}%' or email LIKE '%{q}%' ORDER BY nick ASC"""
    QUERY_GROUP = """SELECT * FROM groups WHERE name LIKE '%{}%'"""
    EXIST = """SELECT * FROM alias WHERE name = '{name}' AND nick = '{nick}' AND email = '{email}' ORDER BY nick ASC"""
    INSERT = """INSERT INTO alias VALUES ('{nick}', '{name}', '{email}')"""
    SCHEMA = """CREATE TABLE IF NOT EXISTS alias (nick TEXT, name TEXT, email TEXT)"""
    SCHEMA2 = """CREATE TABLE IF NOT EXISTS groups (name TEXT, emails TEXT)"""

    def __init__(self, db, *args, **kwargs):
        self.db = db
        if not os.path.isfile(self.db):
            new = True
        else:
            new = False

        self.conn = sqlite3.connect(self.db)

        if new:
            self.create_cache_db(self.db)


    def create_cache_db(self, db):
        c = self.conn.cursor()
        log.info('Creating database schema')
        for sql in [self.SCHEMA, self.SCHEMA2]:
            log.debug(sql)
            c = self.conn.cursor()
            c.execute(sql)
            c.close()
        self.conn.commit()


    def close(self):
        log.info('Closing the connection to the cache database')
        self.conn.close()


    def exists(self, nick, name, email):
        c = self.conn.cursor()
        sql = self.EXIST.format(nick=nick, name=name, email=email)
        log.info('Look in the cache for {}'.format(email))
        log.debug(sql)
        results = []
        for row in c.execute(sql):
            results.append(row)
        c.close()
        return len(results) > 0


    def insert(self, nick, name, email):
        if self.exists(nick, name, email):
            log.debug('Entry for {} already exists'.format(nick))
            return True

        c = self.conn.cursor()
        sql = self.INSERT.format(nick=nick, name=name, email=email)
        log.info('Inserting {} in the cache'.format(email))
        log.debug(sql)
        result = c.execute(sql)
        c.close()
        self.conn.commit()
        return result


    def lookup(self, query):
        c = self.conn.cursor()
        sql = self.QUERY.format(q=query)
        log.info('Look in the cache for {}'.format(query))
        log.debug(sql)
        results = []
        for row in c.execute(sql):
            results.append(row)
        c.close()
        return results

    def lookup_group(self, query):
        c = self.conn.cursor()
        sql = self.QUERY_GROUP.format(query)
        log.debug(sql)
        results = []
        for row in c.execute(sql):
            results.append(row)
        c.close()
        return results





def get_ldap_results_for(query, host, user, password, base):
    results = []

    try:
        client = LdapClient(host, basedn=base)
        log.debug('Logging in as user %s' % user)
        client.bind(username=user, password=password)
        log.debug('Succesfully logged in.')

        filter = "(&(objectClass=*)(|(cn=*{query}*)(displayName=*{query}*)(givenName=*{query}*)(sn=*{query}*)(mail=*{query}*)))".format(query=query)
        entries = client.search(filter=filter, props=['mail', 'displayName', 'givenName', 'surname'])
        log.info('Found %s results from ldap' % len (entries))

        for entry in entries:
            results.append([
                entry['displayname'][0],
                entry['displayname'][0],
                entry['mail'][0]
            ])
    except ldap.SERVER_DOWN as e:
        log.warn('Cannot connect to exchange.')
        raise e
    except KeyboardInterrupt:
        pass

    return results




def main():
    from pycli_tools.parsers import get_argparser
    parser = get_argparser(prog=PROG, version=__version__,
                                 default_config=DEFAULT_CONFIG, description=DESC)
    parser.add_argument('-e', '--endpoint', metavar='endpoint',
                        help='The ldap endpoint to query')
    parser.add_argument('-u', '--username', metavar='username',
                        help='The username to login with')
    parser.add_argument('-p', '--password', metavar='password',
                        help='The password to login with')
    parser.add_argument('-d', '--cache-db',
                        dest='cache_db',
                        metavar='path/to/cache.db',
                        help='Location of the cache database')
    parser.add_argument('query',
                        nargs='+',
                        help='Name or email to lookup. If the query '
                             'contains a `!!` you can skip the cache and '
                             'force a lookup agains the ldap directory.')
    args = parser.parse_args()

    if args.cache_db:
        log.info('Using %s for caching results' % args.cache_db)
        cache = AliasCache(args.cache_db)
    else:
        log.info('Not caching any results.')
        cache = None

    query = ' '.join(args.query)
    log.debug('Working with query: `%s`' % query)


    if query.startswith('@'):
        if not cache:
            raise Exception('Group lookups only work '
                            'when using a cache database')

        query = query.lstrip('@')
        log.debug('Now doing a group lookup for %s' % query)
        print ''
        for row in cache.lookup_group(query):
            print '{emails}\t{group}'.format(emails=row[1], group=row[0])

    else:
        if '!!' in query:
            log.info('Found `!!`. Force an ldap lookup')
            query = query.replace('!!', '')
            skip_cache = True
        else:
            skip_cache = False

        if not cache or skip_cache:
            log.debug('Skipping the local cache, hitting ldap')
            results = get_ldap_results_for(query, host=args.endpoint, user=args.username, password=args.password, base=args.base)

            if cache:
                log.debug('Caching results from ldap locally')
                for result in results:
                    cache.insert(*result)
        else:
            results = cache.lookup(query)

            if len(results) == 0:
                log.info('No cached entries found. Hitting ldap')
                results = get_ldap_results_for(query, host=args.endpoint, user=args.username, password=args.password, base=args.base)
                if cache:
                    log.debug('Caching results from ldap locally')
                    for result in results:
                        cache.insert(*result)
            else:
                log.debug('Found %s results from cache' % len (results))

        print ''
        for row in results:
            print '{email}\t{name}\t{nick}'.format(name=row[1], email=row[2], nick=row[0])

    if cache:
        cache.close()



if __name__ == '__main__':
    main()
