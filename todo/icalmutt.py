#!/usr/bin/env python

import re
import argparse
import sys
import subprocess
import tempfile


if "__main__" == __name__:
    parser = argparse.ArgumentParser(description='Handle calendar invites with mutt.')
    parser.add_argument('event', help='Path to an .ics file containing the event')
    parser.add_argument('-i', '--identity',
                        required=True, help='Identity to repond with')
    args = parser.parse_args()

    try:
        print subprocess.check_output(['/home/nrocco/ical/icalview.py', args.event])
    except Exception as e:
        print 'Cannot view the event'
        print e
        sys.exit(1)


    while True:
        try:
            answer = raw_input("(a)ccept, (d)ecline, (t)entative: ").lower().strip()
        except KeyboardInterrupt:
            print
            sys.exit(1)

        if re.match(r'^[adt]$', answer):
            break
        else:
            print '%s is not a valid reponse' % answer


    try:
        response = subprocess.check_output(['/home/nrocco/ical/icalrespond.py', '-i', args.identity, '-%s' % answer, args.event])
    except Exception as e:
        print 'Cannot create invite reponse'
        print e
        sys.exit(1)


    tmpfile = tempfile.NamedTemporaryFile('w', delete=False)
    tmpfile.write(response)
    print tmpfile

