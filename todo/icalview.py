#!/usr/bin/env python
#https://bitbucket.org/sterlingcamden/remindwhen/src/8f88bbb1bc3e8a02098895a3c6b7e3acf27ff4c7/icalrespond.rb?at=default
#text/calendar; open -a /Applications/iCal.app %s; needsterminal; nametemplate=%s.ics
#application/ics; open -a /Applications/iCal.app %s; needsterminal; nametemplate=%s.ics

import vobject
import argparse
import sys

def read_invition_from(file):
    f = open(file, 'r')
    event = vobject.readOne(f.read())
    f.close()
    return event

if "__main__" == __name__:
    parser = argparse.ArgumentParser(description='View an event.')
    parser.add_argument('event')
    args = parser.parse_args()

    try:
        event = read_invition_from(args.event).vevent
    except Exception as e:
        print 'Cannot read invite'
        print e.message
        sys.exit(1)

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
