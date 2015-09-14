#!/usr/bin/python -tt

from bzrc import BZRC, Command
import sys, math, time, random

# An incredibly simple agent.  All we do is find the closest enemy tank, drive
# towards it, and shoot.  Note that if friendly fire is allowed, you will very
# often kill your own tanks with this code.

#################################################################
# NOTE TO STUDENTS
# This is a starting point for you.  You will need to greatly
# modify this code if you want to do anything useful.  But this
# should help you to know how to interact with BZRC in order to
# get the information you need.
# 
# After starting the bzrflag server, this is one way to start
# this code:
# python agent0.py [hostname] [port]
# 
# Often this translates to something like the following (with the
# port name being printed out by the bzrflag server):
# python agent0.py localhost 49857
#################################################################

class Agent(object):

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.turn_times = [0, 0]
        self.turning = [False, False]
        self.random_turn_time = random.uniform(3, 8)
        self.shoot_times = [0, 0]
        self.random_shoot_time = random.uniform(1.5, 2.5)
        self.commands = []
        self.bzrc.speed(0, 1)
        self.bzrc.speed(1, 1)

    def tick(self, time_diff):
        '''Some time has passed; decide what to do next'''
        # Get information from the BZRC server
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks
        self.othertanks = othertanks
        self.flags = flags
        self.shots = shots
        self.enemies = [tank for tank in othertanks if tank.color !=
                self.constants['team']]

        # Reset my set of commands (we don't want to run old commands)
        self.commands = []

        # Decide what to do with each of my tanks
        self.move(mytanks[0], time_diff)
        self.move(mytanks[1], time_diff)

        # Send the commands to the server
        results = self.bzrc.do_commands(self.commands)

    def move(self, bot, time_diff):
        #if time_diff - self.shoot_times[bot.index] >= self.random_shoot_time:
        if time_diff >= 0:
            self.shoot_times[bot.index] = time_diff
            self.random_shoot_time = random.uniform(1.5, 2.5)
            self.bzrc.shoot(bot.index)
        
        if self.turning[bot.index]:
            if time_diff - self.turn_times[bot.index] >= 1:
                self.turn_times[bot.index] = time_diff
                self.turning[bot.index] = False
            self.bzrc.angvel(bot.index, 1)
        else:
            if time_diff - self.turn_times[bot.index] >= self.random_turn_time:
                self.turn_times[bot.index] = time_diff
                self.turning[bot.index] = True
                self.random_turn_time = random.uniform(3, 8)
            self.bzrc.angvel(bot.index, 0)

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
