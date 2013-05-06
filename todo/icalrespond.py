#!/usr/bin/env python

import vobject
import argparse
import sys
from datetime import datetime



def read_invition_from(file):
    f = open(file, 'r')
    event = vobject.readOne(f.read())
    f.close()
    return event


def generate_response_for(invite):
    #cal = vobject.iCalendar()
    rsp = vobject.newFromBehavior('vcalendar')
    rsp.add('method')
    rsp.method.value = "REPLY"
    rsp.add('vevent')

    for key in ['uid', 'summary', 'dtstart', 'dtend', 'organizer']:
        if invite.vevent.contents.has_key(key):
            rsp.vevent.add(invite.vevent.contents[key][0])

    rsp.vevent.add('dtstamp')
    rsp.vevent.dtstamp.value = datetime.utcnow().replace(
        tzinfo = invite.vevent.dtstamp.value.tzinfo)

    return rsp


def set_mode_for_attendees(attendees, mode):
    for me in attendees:
        me.params['PARTSTAT'][0] = mode
        for i in ['RSVP', 'ROLE', 'X-NUM-GUESTS', 'CUTYPE']:
            if me.params.has_key(i):
                del me.params[i]
    return attendees




if "__main__" == __name__:
    parser = argparse.ArgumentParser(description='Respond to calendar invites.')
    parser.add_argument('event')
    parser.add_argument('-i', '--identity',
                        required=True, help='Identity to repond with')
    parser.add_argument('-a', '--accept', help='Accept the event',
                        action='store_true')
    parser.add_argument('-d', '--decline', help='Decline the event',
                        action='store_true')
    parser.add_argument('-t', '--tentative', help='Tentative the event',
                        action='store_true')
    args = parser.parse_args()

    if args.accept:
        mode = 'Accepted'
    elif args.decline:
        mode = 'Declined'
    elif args.tentative:
        mode = 'Tentative'
    else:
        print 'You must respond somehow :)'
        sys.exit(1)

    try:
        invitation = read_invition_from(args.event)
    except Exception as e:
        print 'Cannot read invite:'
        print e
        sys.exit(1)

    try:
        response = generate_response_for(invitation)
    except:
        print 'Cannot generate a response for this invite'
        sys.exit(1)

    me = [i for i in invitation.vevent.contents['attendee'] if i.value.endswith(args.identity)]
    if not me:
        print 'You (%s) are not invited to this event' % args.identity
        sys.exit(1)

    response.vevent.contents['attendee'] = set_mode_for_attendees(me, mode)
    print response.serialize()
