from bzrc import BZRC, Command, Answer
import sys, math, time, random
import numpy as np
import kalman_plot
import kalman_args

class Agent(object):

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.commands = []
        self.constants = self.bzrc.get_constants()
        self.mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.tank=self.mytanks[0]
        self.enemy=othertanks[0]
        self.firstTime=True
        self.goalAngle=0
        self.mu = np.matrix(
            [[0],
            [0],
            [0],
            [0],
            [0],
            [0]]
        )

        self.sigma_t = kalman_args.sigma_t
        self.sigma_x = kalman_args.sigma_x

        self.H = np.matrix(
            [[1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0]]
        )

        self.sigma_z = np.matrix(
            [[kalman_args.posnoise**2, 0],
            [0, kalman_args.posnoise**2]]
        )

        delta_t = kalman_args.delta_t
        self.F = np.matrix(
            [[1, delta_t, delta_t**2/2, 0, 0, 0],
            [0, 1, delta_t, 0, 0, 0],
            [0, -kalman_args.c, 1, 0, 0, 0],
            [0, 0, 0, 1, delta_t, delta_t**2/2],
            [0, 0, 0, 0, 1, delta_t],
            [0, 0, 0, 0, -kalman_args.c, 1]]
        )
        command = Command(0, 0, 0, False)
        self.commands.append(command)
        results = self.bzrc.do_commands(self.commands)

    def tick(self, delta_t, accum_time):
        tickRate = kalman_args.tick_rate
        if accum_time>tickRate or self.firstTime:
            self.firstTime=False
            other_tank = self.bzrc.get_othertanks()[0]

            z = np.matrix(
                [[other_tank.x],
                [other_tank.y]]
            )

            F = self.F
            K = (F * self.sigma_t * F.T + self.sigma_x) * self.H.T * (self.H * (F * self.sigma_t * F.T + self.sigma_x) * self.H.T + self.sigma_z).I
            self.mu = F * self.mu + K * (z - self.H * F * self.mu)
            if (self.mu[0,0]>400):
                self.mu[0,0]=400
            if (self.mu[0,0]<-400):
                self.mu[0,0]=-400
            if (self.mu[3,0]>400):
                self.mu[3,0]=400
            if (self.mu[3,0]<-400):
                self.mu[3,0]=-400
            self.sigma_t = (np.matrix(np.identity(6)) - K * self.H) * (F * self.sigma_t * F.T + self.sigma_x)
            if kalman_args.print_estimate_vs_actual:
                print('')
                print('Observed: ' + str(other_tank.x) + ', ' + str(other_tank.y))
                print('Predicted: ' + str((F*self.mu)[0,0]) + ', ' + str((F*self.mu)[3,0]))
                print('Kalman Estimate: ' + str(self.mu[0,0]) + ', ' + str(self.mu[3,0]))
                print('')

            self.move_to_position(self.tank,self.mu[0,0],self.mu[3,0])
            results = self.bzrc.do_commands(self.commands)
            '''Some time has passed; decide what to do next'''
            # Get information from the BZRC server
            self.update()

            # Reset my set of commands (we don't want to run old commands)
            self.commands = []
            bulletX = int(self.constants['shotspeed']) * kalman_args.delta_t * math.cos(self.tank.angle) + self.tank.x
            bulletY = int(self.constants['shotspeed']) * kalman_args.delta_t * math.sin(self.tank.angle) + self.tank.y

            # distance = math.sqrt((other_tank.x-self.tank.x)**2+(other_tank.y-self.tank.y)**2)
            futureMu = self.mu
            numIterations = 0
            shotDist = 0
            distanceEnemy = math.sqrt((futureMu[0,0]-bulletX)**2+(futureMu[3,0]-bulletY)**2)
            if distanceEnemy<100:
                self.bzrc.shoot(0)
            while shotDist<800:
                numIterations+=1
                futureMu = F * futureMu
                if (futureMu[0,0]>400):
                    futureMu[0,0]=400
                if (futureMu[0,0]<-400):
                    futureMu[0,0]=-400
                if (futureMu[3,0]>400):
                    futureMu[3,0]=400
                if (futureMu[3,0]<-400):
                    futureMu[3,0]=-400
                bulletX = int(self.constants['shotspeed']) * kalman_args.delta_t * math.cos(self.tank.angle) + bulletX
                bulletY = int(self.constants['shotspeed']) * kalman_args.delta_t * math.sin(self.tank.angle) + bulletY
                if (bulletX>400):
                    bulletX=400
                if (bulletX<-400):
                    bulletX=-400
                if (bulletX>400):
                    bulletX=400
                if (bulletX<-400):
                    bulletX=-400
                if (bulletY>400):
                    bulletY=400
                if (bulletY<-400):
                    bulletY=-400
                if (bulletY>400):
                    bulletY=400
                if (bulletY<-400):
                    bulletY=-400
                if kalman_args.print_bullets:
                    print "bulletX: "+str(bulletX)
                    print "bulletY: "+str(bulletY)
                # print "futureMu:"
                # print futureMu
                shotDist+=int(self.constants['shotspeed']) * kalman_args.delta_t
                distanceEnemy = math.sqrt((futureMu[0,0]-bulletX)**2+(futureMu[3,0]-bulletY)**2)
                # time.sleep(2)
                if distanceEnemy<10:
                    print "shoot"
                    # time.sleep(2)
                    self.bzrc.shoot(0)
                if kalman_args.print_distance_from_shot:
                    print "distanceEnemy: "+str(distanceEnemy)
            if kalman_args.print_iterations:
                print "iterations:"
                print numIterations
            if kalman_args.print_mu:
                print "mu:"
                print self.mu
                print "futureMu:"
                print futureMu
            # Send the commands to the server
            if kalman_args.print_mu_sigma_t:
                print "mu (mean):"
                print self.mu
                print "sigma_t (covariance):"
                print self.sigma_t
            # print "angle:"
            # print self.tank.angle
            if kalman_args.plot_estimate:
                return kalman_plot.plot(self)*-1 # Don't include the time where the agent is paused to view the plot.
            return 0
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
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.tank = mytanks[0]
        self.enemy = othertanks[0]
        self.flags = flags
        # if self.tank.angle<0:
        #     self.move_to_position(self.tank,200,400)
        #     results = self.bzrc.do_commands(self.commands)
        # elif self.tank.angle>.5:
        #     self.move_to_position(self.tank,0,0)
        #     results = self.bzrc.do_commands(self.commands)
        # elif self.tank.angle<.5:
        #     self.move_to_position(self.tank,-200,-400)
        #     results = self.bzrc.do_commands(self.commands)
        # print "goalAngle:"
        # print self.goalAngle
        # command = Command(0, 0, self.goalAngle, False)
        # self.commands.append(command)

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
