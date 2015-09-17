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
            force_x, force_y = self.get_net_force(bot.x, bot.y, bot.callsign, bot.flag != "-")
            speed_x = math.cos(bot.angle) * force_x
            speed_y = math.sin(bot.angle) * force_y
            self.bzrc.speed(bot.index, speed_x + speed_y)
            #self.bzrc.speed(bot.index, 1)
            self.bzrc.angvel(bot.index, self.normalize_angle(math.atan2(force_y, force_x) - bot.angle))
            if bot.flag != "-" or random.uniform(0, 1) > 0.99:
                self.bzrc.shoot(bot.index)

        # Send the commands to the server
        results = self.bzrc.do_commands(self.commands)

    def get_net_force(self, x, y, callsign, got_flag):
        (f1_x, f1_y) = self.get_attractive_force(x, y, callsign, got_flag)
        (f2_x, f2_y) = self.get_repulsive_force(x, y)
        (f3_x, f3_y) = self.get_tangential_force(x, y)
        return (f1_x + f2_x + f3_x, f1_y + f2_y + f3_y)

    def get_attractive_force(self, x, y, callsign, got_flag):
        flags = self.bzrc.get_flags()
        target_dx = 10000000
        target_dy = 10000000
        
        if not got_flag:
            for flag in flags:
                if flag.color not in callsign and flag.poss_color not in callsign:
                    dx = flag.x - x
                    dy = flag.y - y
                    if dx * dx + dy * dy < target_dx * target_dx + target_dy * target_dy:
                        target_dx = dx
                        target_dy = dy
        else:
            bases = self.bzrc.get_bases()
            for base in bases:
                if base.color in callsign:
                    target_dx = (base.corner1_x + base.corner2_x + base.corner3_x + base.corner4_x) / 4 - x
                    target_dy = (base.corner1_y + base.corner2_y + base.corner3_y + base.corner4_y) / 4 - y
        
        return (target_dx, target_dy)

    def get_repulsive_force(self, x, y):
        #TODO
        return (0, 0)

    def get_tangential_force(self, x, y):
        #TODO
        return (0, 0)

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
