#!/usr/bin/env python

from datetime import datetime, timedelta
import caldav
import logging
import os

log = logging.getLogger(__name__)

ID = 'caldav-today'
DEFAULT_CONFIG = '~/.%src' % ID
DESC = '''Query a caldav resource'''



def main(args):
    loglevel = 100 if args.quiet else max(30 - args.verbose * 10, 10)
    logging.basicConfig(level=loglevel, format='%(message)s')

    resource = ''.join(args.resource).lstrip('/')
    url = 'http://%s:%s@%s/%s' % (args.username, args.password, args.endpoint, resource)
    log.debug('Using %s' % url)

    client = caldav.DAVClient(url)
    principal = caldav.Principal(client, url)
    calendars = principal.calendars()

    log.debug('Found %d calendars' % len(calendars))

    if len(calendars) > 0:
        calendar = calendars[0]

    #log.debug('Using calendar %s' % calendar)
    today = datetime.today()
    events = calendar.date_search(today, end=today)
    #log.debug('Found %d events for %s' % (len(events), today))

    for event in events:
        evt = event.instance.contents['vevent'][0]
        print 'Summary: ', evt.contents['summary'][0].value
        print 'Start:   ', evt.contents['dtstart'][0].value
        print 'End:     ', evt.contents['dtend'][0].value
        print 'Status:  ', evt.contents['status'][0].value
        print 'Sequence ', evt.contents['sequence'][0].value
        print 'rrule    ', evt.contents['rrule'][0].value
        print evt.contents.keys()
        print '---------'

    return






if __name__ == '__main__':
    import sys
    from argparse import ArgumentParser
    from ConfigParser import ConfigParser

    conf_parser = ArgumentParser(add_help=False)
    conf_parser.add_argument('-c', '--config', help='Path to a config file.')
    args, remaining_argv = conf_parser.parse_known_args()

    config = ConfigParser()
    config.read(os.path.expanduser(args.config or DEFAULT_CONFIG))
    defaults = dict(config.items(ID)) if config.has_section(ID) else {}

    parser = ArgumentParser(parents=[conf_parser], description=DESC)
    parser.add_argument('-v', '--verbose', action='count',
                        default=0, help='Output more verbose')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Surpress all output')
    parser.add_argument('-e', '--endpoint', metavar='endpoint',
                        help='The caldav endpoint host name')
    parser.add_argument('-u', '--username', metavar='username',
                        help='The username to login with')
    parser.add_argument('-p', '--password', metavar='password',
                        help='The password to login with')
    parser.add_argument('resource', nargs=1)
    parser.set_defaults(**defaults)
    args = parser.parse_args(remaining_argv)

    try:
        main(args)
    except Exception as e:
        parser.error(e)
    else:
        parser.exit()
