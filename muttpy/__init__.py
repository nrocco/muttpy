import logging
from os import path



VERSION = '1.2'
DEFAULT_CONFIG = '~/.muttpyrc'


def get_argparser_instance(**kwargs):
    from argparse import ArgumentParser
    from ConfigParser import ConfigParser

    main_parser = ArgumentParser(add_help=False)
    main_parser.add_argument('-c', '--config',
                             help='path to the config file.')
    main_parser.add_argument('-v', '--verbose', action='count',
                             default=0, help='output more verbose')
    main_parser.add_argument('-q', '--quiet', action='store_true',
                             help='surpress all output')
    args, remaining_argv = main_parser.parse_known_args()

    if args.config and not path.isfile(args.config):
        raise Exception('No config file found at %s' % args.config)

    config = ConfigParser()
    config.read(path.expanduser(args.config or DEFAULT_CONFIG))

    prog = kwargs.get('prog')
    if config.has_section(prog):
        defaults = dict(config.items(prog))
    else:
        defaults = {}

    parser = ArgumentParser(parents=[main_parser], **kwargs)
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + VERSION)
    parser.set_defaults(verbose=args.verbose,
                        quiet=args.quiet, **defaults)

    loglevel = 100 if args.quiet else max(30 - args.verbose * 10, 10)
    logging.basicConfig(level=loglevel, format='%(message)s')

    return parser, remaining_argv
