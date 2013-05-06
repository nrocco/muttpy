import vobject
import logging



log = logging.getLogger(__name__)


PROG = 'mutt-calendar'
DESC = 'Work with calendar items.'


#https://bitbucket.org/sterlingcamden/remindwhen/src/8f88bbb1bc3e8a02098895a3c6b7e3acf27ff4c7/icalrespond.rb?at=default
#text/calendar; open -a /Applications/iCal.app %s; needsterminal; nametemplate=%s.ics
#application/ics; open -a /Applications/iCal.app %s; needsterminal; nametemplate=%s.ics


def read_invition_from(file):
    log.debug('Reading event from %s', file)
    f = open(file, 'r')
    event = vobject.readOne(f.read())
    f.close()
    return event



def show_event(args):
    event = read_invition_from(args.event).vevent
    duration = event.dtend.value - event.dtstart.value

    if 'organizer' in event.contents:
        organizer_name = event.organizer.params['CN'][0]
        organizer_email = event.organizer.value.replace('MAILTO:', '').replace('mailto:', '')
        organizer = '%s <%s>' % (organizer_name, organizer_email)
    else:
        organizer = '?'


    print 'Summary:     %s' % event.summary.value

    if 'location' in event.contents:
        print 'Location:    %s' % event.location.value
    else:
        print 'Location:    ?'

    print 'Organizer:   %s' % organizer
    print 'Start:       %s' % event.dtstart.value
    print 'End:         %s' % event.dtend.value
    print 'Duration:    %s' % duration

    for i in event.contents['attendee']:
        print 'Person:      %s status: %s' % (i.params['CN'][0], i.params['PARTSTAT'][0])

    if 'description' in event.contents:
        print '\n', event.description.value.encode('utf-8').strip()


def get_event_organizer(args):
    event = read_invition_from(args.event).vevent
    print event.organizer.value.replace('MAILTO:','').replace('mailto:','').strip(),


def parse_cli_arguments():
    from muttpy import get_argparser_instance
    parser, argv = get_argparser_instance(prog=PROG, description=DESC)
    subparsers = parser.add_subparsers()

    parser_a = subparsers.add_parser('show', help='show event')
    parser_a.add_argument('event')
    parser_a.set_defaults(func=show_event)

    parser_b = subparsers.add_parser('organizer', help='get event organizer')
    parser_b.add_argument('event')
    parser_b.set_defaults(func=get_event_organizer)

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


if "__main__" == __name__:
    main()
