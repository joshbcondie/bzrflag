from bzrc import BZRC, Command, Answer
import sys, math, time, random
import numpy as np
import kalman_plot

class Agent(object):

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.commands = []
        self.mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.tank=self.mytanks[0]
        self.enemy=othertanks[0]
        self.goal=(self.enemy.x,self.enemy.y)
        self.firstTime=True

        self.mu = np.matrix(
            [[0],
            [0],
            [0],
            [0],
            [0],
            [0]]
        )

        self.sigma_t = np.matrix(
            [[100, 0, 0, 0, 0, 0],
            [0, 0.1, 0, 0, 0, 0],
            [0, 0, 0.1, 0, 0, 0],
            [0, 0, 0, 100, 0, 0],
            [0, 0, 0, 0, 0.1, 0],
            [0, 0, 0, 0, 0, 0.1]]
        )

        self.sigma_x = np.matrix(
            [[0.1, 0, 0, 0, 0, 0],
            [0, 0.1, 0, 0, 0, 0],
            [0, 0, 100, 0, 0, 0],
            [0, 0, 0, 0.1, 0, 0],
            [0, 0, 0, 0, 0.1, 0],
            [0, 0, 0, 0, 0, 100]]
        )

        self.H = np.matrix(
            [[1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0]]
        )

        #TODO: Make these values a parameter since default-posnoise may change
        self.sigma_z = np.matrix(
            [[25, 0],
            [0, 25]]
        )

    def tick(self, delta_t, accum_time):

        self.F = np.matrix(
            [[1, delta_t, delta_t**2/2, 0, 0, 0],
            [0, 1, delta_t, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, delta_t, delta_t**2/2],
            [0, 0, 0, 0, 1, delta_t],
            [0, 0, 0, 0, 0, 1]]
        )

        '''Some time has passed; decide what to do next'''
        # Get information from the BZRC server
        self.update()

        # Reset my set of commands (we don't want to run old commands)
        self.commands = []

        self.update_goal()
        self.move_to_position(self.tank,self.goal[0],self.goal[1])
        # Send the commands to the server
        results = self.bzrc.do_commands(self.commands)
        plotRate=10
        if accum_time>plotRate or self.firstTime:
            self.firstTime=False
            return kalman_plot.plot(self)*-1 # Don't include the time where the game is paused to view the plot.
        else:
            return accum_time+delta_t

    def normalize_angle(self, angle):
        '''Make any angle be between +/- pi.'''
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle

    def move_to_position(self, bot, target_x, target_y):
        # print "move to x: "+str(target_x)+" y: "+str(target_y)
        target_angle = math.atan2(target_y - bot.y,
                target_x - bot.x)
        relative_angle = self.normalize_angle(target_angle - bot.angle)
        command = Command(bot.index, 0, 2 * relative_angle, False)
        self.commands.append(command)

    def update(self):
        self.bzrc.shoot(0)
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.tank = mytanks[0]
        self.enemy = othertanks[0]
        self.flags = flags

    def update_goal(self):
        self.goal=(self.enemy.x,self.enemy.y)
        return

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
    count=0
    accum_time=0
    try:
        while True:
            time_diff = time.time() - prev_time
            prev_time=time.time()
            accum_time=agent.tick(time_diff, accum_time)

    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
