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
        self.commands = []

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
        for bot in mytanks:
            closest_flag_dx = 10000000
            closest_flag_dy = 10000000
            force_x = 0
            force_y = 0
            for flag in flags:
                if bot.flag == "-" and flag.color not in bot.callsign and flag.poss_color not in bot.callsign:
                    dx = flag.x - bot.x
                    dy = flag.y - bot.y
                    if dx * dx + dy * dy < closest_flag_dx * closest_flag_dx + closest_flag_dy * closest_flag_dy:
                        closest_flag_dx = dx
                        closest_flag_dy = dy
                elif bot.flag != "-" and flag.color in bot.callsign:
                    closest_flag_dx = flag.x - bot.x
                    closest_flag_dy = flag.y - bot.y
            force_x += 1 * closest_flag_dx
            force_y += 1 * closest_flag_dy
            speed_x = math.cos(bot.angle) * force_x
            speed_y = math.sin(bot.angle) * force_y
            self.bzrc.speed(bot.index, speed_x + speed_y)
            #self.bzrc.speed(bot.index, 1)
            self.bzrc.angvel(bot.index, self.normalize_angle(math.atan2(force_y, force_x) - bot.angle))
            if bot.flag != "-" or random.uniform(0, 1) > 0.99:
                self.bzrc.shoot(bot.index)

        # Send the commands to the server
        results = self.bzrc.do_commands(self.commands)

    def move_to_position(self, bot, target_x, target_y):
        target_angle = math.atan2(target_y - bot.y,
                target_x - bot.x)
        relative_angle = self.normalize_angle(target_angle - bot.angle)
        command = Command(bot.index, 1, 2 * relative_angle, False)
        self.commands.append(command)

    def normalize_angle(self, angle):
        '''Make any angle be between +/- pi.'''
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle


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
