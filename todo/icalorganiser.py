#!/usr/bin/env python

import vobject
import argparse
import sys

def read_invition_from(file):
    f = open(file, 'r')
    event = vobject.readOne(f.read())
    f.close()
    return event

if "__main__" == __name__:
    parser = argparse.ArgumentParser(description='Get organizer of an event.')
    parser.add_argument('event')
    args = parser.parse_args()

    try:
        event = read_invition_from(args.event).vevent
    except Exception as e:
        print 'Cannot read invite'
        print e.message
        sys.exit(1)

    try:
        print event.organizer.value.replace('MAILTO:','').replace('mailto:','').strip(),
    except:
        print '?'
        sys.exit(1)
