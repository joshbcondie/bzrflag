#!/usr/bin/python -tt

from bzrc import BZRC, Command, Answer
import sys, math, time, random

class Agent(object):

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.speed = 1
        self.angvel = 1

    def tick(self, time_diff):
        if random.uniform(0, 1) < 0.001:
            if self.speed > 0:
                self.speed = -1 * random.uniform(0.7, 1)
            else:
                self.speed = random.uniform(0.7, 1)
        if random.uniform(0, 1) < 0.001:
            if self.angvel > 0:
                self.angvel = -1 * random.uniform(0.7, 1)
            else:
                self.angvel = random.uniform(0.7, 1)
        
        if self.speed > 1:
            self.speed = 1
        elif self.speed < -1:
            self.speed = -1
        
        if self.angvel > 1:
            self.angvel = 1
        elif self.angvel < -1:
            self.angvel = -1
        
        self.bzrc.speed(0, self.speed)
        self.bzrc.angvel(0, self.angvel)

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
            #prev_time = time.time()
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
