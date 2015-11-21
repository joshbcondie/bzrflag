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
        for row in range(len(self.grid)):
            for col in range(len(self.grid)):
                self.grid[row][col]=.5
        self.previousOutput = np.zeros(shape=(int(self.constants['worldsize']),int(self.constants['worldsize'])))
        self.tank={}
        # print "tank location: x: "+str(self.tank.x)+" y: "+str(self.tank.y)
        grid_filter_gl.init_window(800, 800)
        self.grid_size = 100
        self.points = []
        self.prior = .5
        self.threshold = .5
        self.chosenX=0
        self.chosenY=0
        self.needGoal=True
        self.trueP=float(self.constants['truepositive'])
        self.trueN=float(self.constants['truenegative'])
        worldsize = int(self.constants['worldsize'])
        for i in range(self.grid_size / 2 - worldsize / 2, worldsize / 2, self.grid_size):
            for j in range(self.grid_size / 2 - worldsize / 2, worldsize / 2, self.grid_size):
                self.points.append((i, j))
        self.timer = 0
        self.past_position = {}
        self.goals = {}
        self.stuck = {}
        self.stuck_count = 0
        self.last_x = 0
        self.last_y = 0
        self.mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        numTanks=1
        self.mytanks = self.mytanks[:numTanks]
        for tank in self.mytanks:
            self.past_position[tank.index] = tank.x, tank.y
            self.bzrc.speed(tank.index, 1)
            self.goals[tank.index] = None
            self.stuck[tank.index] = 0
            self.update(tank.index)

    def update(self, tankNum):
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        # self.mytanks = mytanks[:1]
        self.flags = flags
        # print self.bzrc.get_occgrid(tankNum)
        try:
            sensorData=zip(*self.bzrc.get_occgrid(tankNum)[1])
        except:
            print "error"
        start_x, start_y = self.bzrc.get_occgrid(tankNum)[0]
        # print "row length: "+str(len(self.bzrc.get_occgrid(0)[1][0])-1) # 99
        # print "col length: "+str(len(self.bzrc.get_occgrid(0)[1])-1) # 99
        xStart=start_x+int(self.constants['worldsize'])/2
        yStart=start_y+int(self.constants['worldsize'])/2
        try:
            # for row in range(len(self.bzrc.get_occgrid(0)[1][0])):
            #     for point in range(len(self.bzrc.get_occgrid(0)[1])):
            y=0
            x=0
            for row in sensorData:
                    for point in row:
                        try:
                            if self.chosenX==0 and self.chosenY==0:
                                self.chosenY=yStart+y
                                self.chosenX=xStart+x
                            # Apply Bayes Rule on each point and get the new prior.
                            prior=self.grid[yStart+y][xStart+x]
                            # point=0
                            if point==1:
                                posterior=self.trueP*prior/(self.trueP*prior + (1-self.trueN)*(1-prior))
                            # print prior
                            else:
                                posterior=(1-self.trueP)*prior/((1-self.trueP)*prior + self.trueN*(1-prior))
                            self.grid[yStart+y][xStart+x]=posterior
                            # print str(self.chosenY)+"  "+str(self.chosenX)
                            # if xStart+x==self.chosenX and yStart+y==self.chosenY:
                            #     print "posterior: "+str(posterior)
                            #     if point==1:
                            #         print "("+str(self.trueP)+"*"+str(prior)+"/("+str(self.trueP)+"*"+str(prior)+"(1-"+str(self.trueN)+")*(1-"+str(prior)+"))"
                            #     # print prior
                            #     print "posterior: "+str(self.grid[self.chosenY][self.chosenX])
                            x+=1
                        except IndexError:
                            continue
                    y+=1
                    x=0

        except ValueError:
            print "error"
            pass
        # try:
        #     self.grid[yStart : yStart+len(self.bzrc.get_occgrid(0)[1][0]), xStart : xStart+len(self.bzrc.get_occgrid(0)[1])] = sensorData
        # except ValueError:
        #     pass
        grid_filter_gl.update_grid(self.grid)
        grid_filter_gl.draw_grid()
        #occg = list(self.bzrc.get_occgrid(i.index) for i in self.mytanks)

    def tick(self, time_diff, count):
        '''Some time has passed; decide what to do next'''
        # Get information from the BZRC server
        for tank in self.mytanks:
            self.update(tank.index)

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
            print "goals are none"
            next_goal = self.next_goal(bot)
            self.goals[bot.index] = next_goal

        else:
            y=0
            x=0
            if self.last_x == bot.x and self.last_y == bot.y:
                self.timer += 1
            else:
                self.timer=0
            if self.timer==0:
                self.last_x = bot.x
                self.last_y = bot.y
            if self.timer > 10:
                # print 'stuck on ' + str(self.points[self.goals[bot.index]][0]) + ', ' + str(self.points[self.goals[bot.index]][1])
                self.stuck_count += 1
                last_goal = self.goals[bot.index]
                self.goals[bot.index] = self.random_goal(bot, last_goal)
                if self.stuck_count > 2 or self.goals[bot.index] == last_goal:
                    scale = random.uniform(2, 10)
                    if random.uniform(0, 1) < 0.5:
                        scale *= -1
                    self.points.append((min(400, max(-400, bot.x - bot.vy * scale + random.uniform(-200, 200))), min(400, max(-400, bot.y + bot.vx * scale + random.uniform(-200, 200)))))
                    self.goals[bot.index] = len(self.points) - 1
                    # print 'added point ' + str(self.points[len(self.points) - 1][0]) + ', ' + str(self.points[len(self.points) - 1][1])
                #self.points[self.goals[bot.index]] = (x - bot.vy * 2, y + bot.vx * 2)
                #if bot.x < -390 or bot.x > 390 or bot.y < -390 or bot.y > 390:
                #    print 'completely removed obstacle ' + str(x) + ', ' + str(y)
                #    self.points.remove(self.points[self.goals[bot.index]])
                #    self.goals[bot.index] = None
                self.timer = 0
                if self.grid[y][x] == .5:
                    return
                # self.points.remove(self.points[self.goals[bot.index]])
            x,y = self.points[self.goals[bot.index]]
                # self.points.remove(self.points[self.goals[bot.index]])
                # print "y: "+str(y)+" x: "+str(x)
            self.move_to_position(bot, x, y)
                # print self.grid[y][x]
            dx = x - bot.x
            dy = y - bot.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 50 or self.grid[y][x] != .5:
                print 'reached goal ' + str(x) + ', ' + str(y)
                print "bot is at x: "+str(bot.x)+" y: "+str(bot.y)
                if self.goals[bot.index] < len(self.points) - 1:
                    self.stuck_count = 0
                if bot.index<len(self.goals) and self.goals[bot.index]<len(self.points):
                    self.points.remove(self.points[self.goals[bot.index]])
                self.goals[bot.index] = None
                self.bzrc.angvel(0, 0)
                self.needGoal=True
                return
            
            for i in range(len(self.points)):
                x,y = self.points[i]
                dx = x - bot.x
                dy = y - bot.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist < 50:
                    if i < self.goals[bot.index]:
                        self.goals[bot.index] -= 1
                    self.points.remove((x, y))
                    # print 'other point reached ' + str(x) + ', ' + str(y)
                    break
            #self.commands.append(GoodrichCommand(bot.index, dx/5, dy/5))
    
    def move_to_position(self, bot, target_x, target_y):
        target_angle = math.atan2(target_y - bot.y,
                target_x - bot.x)
        relative_angle = self.normalize_angle(target_angle - bot.angle)
        command = Command(bot.index, 1, .5*relative_angle, True)
        self.commands.append(command)

    def next_goal(self, bot):
        #if self.goals[bot.index] is not None:
        #    self.points.remove(self.points[self.goals[bot.index]])
        best = None
        for i in range(len(self.points)):
            x, y = self.points[i]
            if self.stuck_count > 2:
                scale = random.uniform(2, 15)
            else:
                scale = 2
            dist = math.sqrt((x - (bot.x + bot.vx * scale))**2 + (y - (bot.y + bot.vy * scale))**2)
            if not best or dist > best[0]:
                best = [dist, i]
        if best:
            return best[1]
    
    def random_goal(self, bot, current_goal):
        best = None
        for i in range(len(self.points)):
            x, y = self.points[i]
            if random.uniform(0, 1) < 0.5:
                scale = -100
            else:
                scale = 100
            dist = math.sqrt((x - (bot.x - bot.vy * scale))**2 + (y - (bot.y + bot.vx * scale))**2)
            if not best or dist > best[0]:
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
    count=0
    try:
        while True:
            time_diff = time.time() - prev_time
            prev_time=time.time()
            agent.tick(time_diff, count)
            count+=1
            if count>10:
                count=0

    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
