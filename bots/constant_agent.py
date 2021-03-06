#!/usr/bin/python -tt

from bzrc import BZRC, Command, Answer
import sys, math, time, random
import kalman_args

class Agent(object):

    def __init__(self, bzrc):
        self.bzrc = bzrc
        bzrc.speed(0, .5)

    def tick(self, time_diff):
        if kalman_args.print_estimate_vs_actual:
            tanks = self.bzrc.get_mytanks()
            print('Actual: ' + str(tanks[0].x) + ', ' + str(tanks[0].y))

def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    #bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))

    agent = Agent(bzrc)

    prev_time = time.time()

    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
