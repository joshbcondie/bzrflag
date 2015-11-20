#!/usr/bin/python -tt

from bzrc import BZRC, Command, Answer
import sys, math, time, random
import grid_filter_gl
import numpy as np

class Agent(object):

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        bases = self.bzrc.get_bases()
        for base in bases:
            if base.color == self.constants['team']:
                self.base = Answer()
                self.base.x = (base.corner1_x+base.corner3_x)/2
                self.base.y = (base.corner1_y+base.corner3_y)/2
        self.grid = np.zeros(shape=(int(self.constants['worldsize']),int(self.constants['worldsize'])))
        self.previousOutput = np.zeros(shape=(int(self.constants['worldsize']),int(self.constants['worldsize'])))
        self.tank={}
        # print "tank location: x: "+str(self.tank.x)+" y: "+str(self.tank.y)

        grid_filter_gl.init_window(800, 800)
        self.grid_size = 100
        self.points = []
        self.prior = .5
        self.threshold = .5
        self.posProb = float(self.constants['truepositive'])*self.prior/(float(self.constants['truepositive'])*self.prior + (1-float(self.constants['truenegative']))*(1-self.prior))
        self.negProb = (1-float(self.constants['truepositive']))*(1-self.prior)/((1-float(self.constants['truepositive']))*self.prior + float(self.constants['truenegative'])*(1-self.prior))
        worldsize = int(self.constants['worldsize'])
        if self.posProb>self.threshold:
            self.truePos=True
            print "When 1 is observed, assume 1"
        else:
            self.truePos=False
            print "When 1 is observed, assume 0"
        for i in range(self.grid_size / 2 - worldsize / 2, worldsize / 2, self.grid_size):
            for j in range(self.grid_size / 2 - worldsize / 2, worldsize / 2, self.grid_size):
                self.points.append((i, j))
        self.timer = 0
        self.past_position = {}
        self.goals = {}
        self.stuck = {}
        self.last_x = 0
        self.last_y = 0
        self.mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        for tank in self.mytanks:
            self.past_position[tank.index] = tank.x, tank.y
            self.goals[tank.index] = None
            self.stuck[tank.index] = 0
        self.update()

    def normalizePoint(self,val):
        return self.tank.x+int(self.constants['worldsize'])/2

    def getTankY(self,val):
        return self.tank.y+int(self.constants['worldsize'])/2

    def update(self):
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks[:1]
        self.tank = self.mytanks[0]
        self.othertanks = othertanks
        self.flags = flags
        sensorData=zip(*self.bzrc.get_occgrid(0)[1])
        start_x, start_y = self.bzrc.get_occgrid(0)[0]
        # print "row length: "+str(len(self.bzrc.get_occgrid(0)[1][0])-1) # 99
        # print "col length: "+str(len(self.bzrc.get_occgrid(0)[1])-1) # 99
        xStart=start_x+int(self.constants['worldsize'])/2
        yStart=start_y+int(self.constants['worldsize'])/2
        # try:
        #     # for row in range(len(self.bzrc.get_occgrid(0)[1][0])):
        #     #     for point in range(len(self.bzrc.get_occgrid(0)[1])):
        #     for row in range(self.grid_size):
        #         for point in range(self.grid_size):
        #             # Apply Bayes Rule on each point
        #             if point==1 and self.truePos:
        #                 self.grid[yStart+row][xStart+point]=1
        #                 print "row: "+str(row)+" col: "+str(point)
        #             else:
        #                 self.grid[yStart+row][xStart+point]=0
        # except ValueError:
        #     print "error"
        #     pass
        try:
            self.grid[yStart : yStart+len(self.bzrc.get_occgrid(0)[1][0]), xStart : xStart+len(self.bzrc.get_occgrid(0)[1])] = sensorData
        except ValueError:
            pass
        grid_filter_gl.update_grid(self.grid)
        grid_filter_gl.draw_grid()
        #occg = list(self.bzrc.get_occgrid(i.index) for i in self.mytanks)

    def tick(self, time_diff):
        '''Some time has passed; decide what to do next'''
        # Get information from the BZRC server
        self.update()

        # Reset my set of commands (we don't want to run old commands)
        self.commands = []

        # Decide what to do with each of my tanks
        for bot in self.mytanks:
            self.update_goal(bot)
            self.past_position[bot.index] = bot.x, bot.y

        # Send the commands to the server
        results = self.bzrc.do_commands(self.commands)

    def update_goal(self, bot):
        if self.goals[bot.index] is None:
            next_goal = self.next_goal(bot)
            self.goals[bot.index] = next_goal

        else:
            if self.last_x == bot.x and self.last_y == bot.y:
                self.timer += 1
            self.last_x = bot.x
            self.last_y = bot.y
            if self.timer > 50:
                print 'stuck on ' + str(self.points[self.goals[bot.index]][0]) + ', ' + str(self.points[self.goals[bot.index]][1])
                x,y = self.points[self.goals[bot.index]]
                self.points[self.goals[bot.index]] = (x - bot.vy * 2, y + bot.vx * 2)
                if bot.x < -390 or bot.x > 390 or bot.y < -390 or bot.y > 390:
                    print 'completely removed obstacle ' + str(x) + ', ' + str(y)
                    self.points.remove(self.points[self.goals[bot.index]])
                    self.goals[bot.index] = None
                self.timer = 0
                return
            x,y = self.points[self.goals[bot.index]]
            dx = x - bot.x
            dy = y - bot.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 30:
                print 'reached goal ' + str(x) + ', ' + str(y)
                self.points.remove(self.points[self.goals[bot.index]])
                self.goals[bot.index] = None
                self.bzrc.angvel(0, 0)
                return
            self.move_to_position(bot, x, y)
            
            for i in range(len(self.points)):
                x,y = self.points[i]
                dx = x - bot.x
                dy = y - bot.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist < 30:
                    if i < self.goals[bot.index]:
                        self.goals[bot.index] -= 1
                    self.points.remove((x, y))
                    print 'other point reached ' + str(x) + ', ' + str(y)
                    break
            #self.commands.append(GoodrichCommand(bot.index, dx/5, dy/5))
    
    def move_to_position(self, bot, target_x, target_y):
        target_angle = math.atan2(target_y - bot.y,
                target_x - bot.x)
        relative_angle = self.normalize_angle(target_angle - bot.angle)
        command = Command(bot.index, 1, 2 * relative_angle, True)
        self.commands.append(command)

    def random_pos(self):
        width = int(self.constants['worldsize'])
        x = random.randrange(width) - width/2
        y = random.randrange(width) - width/2
        return x,y

    def next_goal(self, bot):
        #if self.goals[bot.index] is not None:
        #    self.points.remove(self.points[self.goals[bot.index]])
        best = None
        for i in range(len(self.points)):
            x, y = self.points[i]
            dist = math.sqrt((x - (bot.x + bot.vx * 2))**2 + (y - (bot.y + bot.vy * 2))**2)
            if not best or dist < best[0]:
                best = [dist, i]
        if best:
            return best[1]
    
    def move_towards(self, bot, x, y):
        dx = x - bot.x
        dy = y - bot.y
        self.commands.append(GoodrichCommand(bot.index, dx/10, dy/10))

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
