import logging
from email.parser import Parser
from muttpy import VERSION, DEFAULT_CONFIG



log = logging.getLogger(__name__)

PROG = 'mutt-email'
DESC = 'Process Maildir formatted emails'


def get_email(*headers):
    for header in headers:
        if header:
            for addr in header.split(','):
                yield addr.strip()


def list_all_emails(args):
    headers = Parser().parse(open(args.email[0], 'r'))
    addresses = [x for x in get_email(headers['To'],
                                      headers['Cc'],
                                      headers['Bcc'],
                                      headers['From'])]

    print '\n'.join(addresses)




def main():
    from pycli_tools import get_argparser
    parser = get_argparser(prog=PROG, version=VERSION,
                                 default_config=DEFAULT_CONFIG, description=DESC)
    parser.add_argument('email', nargs=1)
    parser.set_defaults(func=list_all_emails)
    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as e:
        if args.quiet:
            import sys
            sys.exit(1)
        else:
            if args.verbose == 0:
                log.error(e)
            else:
                raise e


if '__main__' == __name__:
    main()
