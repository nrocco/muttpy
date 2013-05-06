import logging
from email.parser import Parser



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


def parse_cli_arguments():
    from muttpy import get_argparser_instance
    parser, argv = get_argparser_instance(prog=PROG, description=DESC)
    parser.add_argument('email', nargs=1)
    parser.set_defaults(func=list_all_emails)
    return parser.parse_args(argv)


def main():
    args = parse_cli_arguments()
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
