#!/usr/bin/python -tt

from bzrc import BZRC, Command, Answer
import sys, math, time, random, numpy, matplotlib.pyplot as pyplot
import search

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
        self.update()
        self.past_position = {}
        self.goals = {}
        self.stuck = {}
        for tank in self.mytanks:
            self.past_position[tank.index] = tank.x, tank.y
            self.goals[tank.index] = None
            self.stuck[tank.index] = 0
        self.set_flag_goals()
        
        self.vertex_positions = []
        self.vertex_positions.append((self.base.x, self.base.y))
        self.obstacles = self.bzrc.get_obstacles()
        for obstacle in self.obstacles:
            for i in range(len(obstacle)):
                x = obstacle[i][0] - obstacle[(i + 2) % 4][0]
                y = obstacle[i][1] - obstacle[(i + 2) % 4][1]
                dist = math.sqrt(x ** 2 + y ** 2)
                self.vertex_positions.append((obstacle[i][0] + x / dist * 10, obstacle[i][1] + y / dist * 10))
        self.vertex_positions.append(self.goals[0])
        
        #print "self.vertex_positions = " + str(self.vertex_positions)
        
        self.adjacency_matrix = numpy.zeros([len(self.vertex_positions), len(self.vertex_positions)])
        
        for i in range(len(self.obstacles)):
            for j in range(4):
                index = i * 4 + j + 1
                if j < 3:
                    self.adjacency_matrix[index][index + 1] = self.adjacency_matrix[index + 1][index] = math.sqrt((self.vertex_positions[index][0] - self.vertex_positions[index + 1][0]) ** 2 + (self.vertex_positions[index][1] - self.vertex_positions[index + 1][1]) ** 2)
                else:
                    first_corner = i * 4 + 1
                    self.adjacency_matrix[index][first_corner] = self.adjacency_matrix[first_corner][index] = math.sqrt((self.vertex_positions[index][0] - self.vertex_positions[first_corner][0]) ** 2 + (self.vertex_positions[index][1] - self.vertex_positions[first_corner][1]) ** 2)
        
        for i in range(len(self.vertex_positions)):
            for j in range(i + 1, len(self.vertex_positions)):
                if i == 0 or j == len(self.vertex_positions) - 1 or (i - 1) / 4 != (j - 1) / 4:
                    #print "i = " + str(i)
                    #print "j = " + str(j)
                    xa = self.vertex_positions[i][0]
                    ya = self.vertex_positions[i][1]
                    xb = self.vertex_positions[j][0]
                    yb = self.vertex_positions[j][1]
                    #print "a = (" + str(xa) + ", " + str(ya) + ")"
                    #print "b = (" + str(xb) + ", " + str(yb) + ")"
                    intersect = False
                    
                    for m in range(len(self.obstacles)):
                        if intersect:
                            break
                        for n in range(4):
                            index = m * 4 + n + 1
                            if index == i or index == j:
                                continue
                            xc = self.vertex_positions[index][0]
                            yc = self.vertex_positions[index][1]
                            #print "c = (" + str(xc) + ", " + str(yc) + ")"
                            if n < 3:
                                if index + 1 == i or index + 1 == j:
                                    continue
                                xd = self.vertex_positions[index + 1][0]
                                yd = self.vertex_positions[index + 1][1]
                            else:
                                first_corner = m * 4 + 1
                                if first_corner == i or first_corner == j:
                                    continue
                                xd = self.vertex_positions[first_corner][0]
                                yd = self.vertex_positions[first_corner][1]
                            #print "d = (" + str(xd) + ", " + str(yd) + ")"
                            if self.segments_intersect(xa, ya, xb, yb, xc, yc, xd, yd):
                                #print "intersection"
                                #print "a = (" + str(xa) + ", " + str(ya) + ")"
                                #print "b = (" + str(xb) + ", " + str(yb) + ")"
                                #print "c = (" + str(xc) + ", " + str(yc) + ")"
                                #print "d = (" + str(xd) + ", " + str(yd) + ")"
                                intersect = True
                                break
                    
                    if intersect:
                        self.adjacency_matrix[i][j] = self.adjacency_matrix[j][i] = 0
                    else:
                        self.adjacency_matrix[i][j] = self.adjacency_matrix[j][i] = math.sqrt((self.vertex_positions[i][0] - self.vertex_positions[j][0]) ** 2 + (self.vertex_positions[i][1] - self.vertex_positions[j][1]) ** 2)
        
        half_worldsize = int(self.constants['worldsize']) / 2
        tanklength = int(self.constants['tanklength'])
        for i in range(1, len(self.vertex_positions) - 1):
            if half_worldsize - self.vertex_positions[i][0] < tanklength or half_worldsize + self.vertex_positions[i][0] < tanklength or half_worldsize - self.vertex_positions[i][1] < tanklength or half_worldsize + self.vertex_positions[i][1] < tanklength:
                for j in range(len(self.vertex_positions)):
                    self.adjacency_matrix[i][j] = self.adjacency_matrix[j][i] = 0
        
        numpy.set_printoptions(threshold=numpy.nan)
        #print "self.adjacency_matrix = " + str(self.adjacency_matrix)
        self.updateGraph()
        #self.path = search.dfs(self.graph,0,len(self.vertex_positions) - 1)
        self.path = search.bfs(self.graph,0,len(self.vertex_positions) - 1)
        #self.path = search.aStar(self.graph,self.adjacency_matrix,0,len(self.vertex_positions) - 1)
        self.plot_visibility_graph()
        
        self.current_goal_index = 1
        self.goals[0] = self.vertex_positions[self.path[self.current_goal_index]]

    def updateGraph(self):
        graph=[]
        for i in range(len(self.vertex_positions)):
            nodes=[]
            print "node: "+str(i)
            for j in range(len(self.adjacency_matrix[0])):
                print "node: "+str(j)
                if (self.adjacency_matrix[i][j]!=0):
                    print "appending "+str(j)
                    nodes.append(j)

            graph.append(nodes)
        self.graph=graph
    # def updateGraph(self):
    #     graph={}
    #     for i in range(len(self.vertex_positions)):
    #         nodes=[]
    #         for j in range(len(self.adjacency_matrix[0])):
    #             if (self.adjacency_matrix[i][j]!=0):
    #                 nodes.append(j)

    #         graph.append(nodes)
    #     self.graph=graph

    def segments_intersect(self, x1, y1, x2, y2, x3, y3, x4, y4):
        if x1 == x2 and x3 == x4:
            return False
        elif x1 == x2:
            m = (y4 - y3) / (x4 - x3)
            b = y3 - m * x3
            if x1 * m + b >= min(y3, y4) and x1 * m + b >= min(y1, y2) and x1 * m + b <= max(y3, y4) and x1 * m + b <= max(y1, y2):
                return True
            return False
        elif x3 == x4:
            m = (y2 - y1) / (x2 - x1)
            b = y1 - m * x1
            if x3 * m + b >= min(y3, y4) and x3 * m + b >= min(y1, y2) and x3 * m + b <= max(y3, y4) and x3 * m + b <= max(y1, y2):
                return True
            return False
        
        m12 = (y2 - y1) / (x2 - x1)
        #print "m12 = " + str(m12)
        b12 = y1 - m12 * x1
        #print "b12 = " + str(b12)
        m34 = (y4 - y3) / (x4 - x3)
        #print "m34 = " + str(m34)
        b34 = y3 - m34 * x3
        #print "b34 = " + str(b34)
        if m12 == m34:
            return False
        x = (b34 - b12) / (m12 - m34)
        #print "x = " + str(x)
        if x >= min(x1, x2) and x >= min(x3, x4) and x <= max(x1, x2) and x <= max(x3, x4):
            return True
        return False

    def update(self):
        self.bzrc.shoot(0)
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks[:1]
        self.othertanks = othertanks
        self.flags = flags
        #occg = list(self.bzrc.get_occgrid(i.index) for i in self.mytanks)

    def set_flag_goals(self):
        for tank in self.mytanks:
            best = [0,None]
            flag = self.closest_flag(tank)
            if flag:
                self.goals[tank.index] = flag.x,flag.y

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
        if not self.goals[bot.index]:
            if bot.flag != '-':
                if self.current_goal_index - 1 >= 0:
                    self.current_goal_index -= 1
            elif self.current_goal_index + 1 < len(self.path):
                    self.current_goal_index += 1
            
            self.goals[bot.index] = self.vertex_positions[self.path[self.current_goal_index]]
        elif bot.flag != '-' and self.current_goal_index == len(self.path) - 1:
            # This isn't getting called
            self.current_goal_index -= 1
            self.vertex_positions[0] = (self.base.x, self.base.y)
        
        self.goals[bot.index] = self.vertex_positions[self.path[self.current_goal_index]]
        x,y = self.goals[bot.index]
        dx = x - bot.x
        dy = y - bot.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 20:
            #print "reached goal " + str(self.goals[bot.index])
            self.goals[bot.index] = None
            return
        #print "move to position " + str(x) + ", " + str(y)
        self.move_to_position(bot, x, y)
        #self.commands.append(GoodrichCommand(bot.index, dx/5, dy/5))
    
    def move_to_position(self, bot, target_x, target_y):
        target_angle = math.atan2(target_y - bot.y,
                target_x - bot.x)
        relative_angle = self.normalize_angle(target_angle - bot.angle)
        command = Command(bot.index, 1, 2 * relative_angle, False)
        self.commands.append(command)

    def random_pos(self):
        width = int(self.constants['worldsize'])
        x = random.randrange(width) - width/2
        y = random.randrange(width) - width/2
        return x,y

    def closest_flag(self, bot):
        best = None
        for flag in self.flags:
            if flag.color == self.constants['team']:
                continue
            if flag.poss_color != 'none':
                continue
            dist = math.sqrt((flag.x - bot.x)**2 + (flag.y - bot.y)**2)
            if not best or dist < best[0]:
                best = [dist, flag]
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

    def show_obstacle(self, obstacle):
        # print obstacle[0][0]
        pyplot.plot([obstacle[0][0],obstacle[1][0],obstacle[2][0],obstacle[3][0],obstacle[0][0]],[obstacle[0][1],obstacle[1][1],obstacle[2][1],obstacle[3][1],obstacle[0][1]])

    def plot_visibility_graph(self):
        pyplot.figure(1)
        for obstacle in self.obstacles:
            self.show_obstacle(obstacle)
        # for node in self.visibility_graph:
        #     for neighbor in node.neighbors:
        #         plot.plot([node.point[0], neighbor.point[0]], [node.point[1], neighbor.point[1]], 'g')
        for i in range(len(self.vertex_positions)):
            pyplot.plot(self.vertex_positions[i][0],self.vertex_positions[i][1],'go')
            pyplot.annotate(str(i),xy=(self.vertex_positions[i][0],self.vertex_positions[i][1]))
            for j in range(len(self.adjacency_matrix[0])):
                if (self.adjacency_matrix[i][j]!=0):
                    pyplot.plot([self.vertex_positions[i][0],self.vertex_positions[j][0]],[self.vertex_positions[i][1],self.vertex_positions[j][1]])
        # for point in self.adjacency_matrix:
        #     for target in point:
        #         pyplot.plot()
        pyplot.show()


    def plot_search_progress(visibility_graph, obstacles):
        pyplot.figure(2)
        for obstacle in obstacles:
            self.show_obstacle(obstacle)

        pyplot.show()
        for node in visibility_graph:
            for neighbor in node.neighbors:
                draw_edge = False
                if node.search_state == SearchStates.visited and neighbor.search_state == SearchStates.visited:
                    edge_color = 'r'
                    draw_edge = True
                elif node.search_state == SearchStates.visited and neighbor.search_state == SearchStates.frontier:
                    edge_color = 'b'
                    draw_edge = True

                if draw_edge:
                    plot([node.point[0], neighbor.point[0]], [node.point[1], neighbor.point[1]], edge_color)

            node_color = 'go'
            if node.search_state == SearchStates.visited:
                node_color = 'ro'
            elif node.search_state == SearchStates.frontier:
                node_color = 'bo'

            # Plot a colored point for the node
            plot([node.point[0]], [node.point[1]], node_color)

        pyplot.show()

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
