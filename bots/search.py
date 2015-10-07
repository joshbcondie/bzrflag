# Sample code from http://www.redblobgames.com/pathfinding/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
#
# Feel free to use this code in your own projects, including commercial projects
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>

import Queue
import collections


class Queue:
    def __init__(self):
        self.elements = collections.deque()
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, x):
        self.elements.append(x)
    
    def get(self):
        return self.elements.popleft()

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]


def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def aStar(graph, weights, start):
    goal=len(graph)-1
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far

def bfs(graph, start):
    goal=len(graph)-1
    frontier = Queue()
    frontier.put(start)
    visited = []
    visited.append(start)
    
    while not frontier.empty():
        current = frontier.get()
        if current==goal:
            visited.append(node)
            return visited
        # print "current: "+str(current)
        print("Visiting %r" % current)
        for node in graph[current]:
            if node not in visited:
                frontier.put(node)
                visited.append(node)
        print visited
    return visited

def dfs(graph, start):
    visited, stack = [], [start]
    goal=len(graph)-1
    while stack:
        vertex = stack.pop()
        print "vertex: "+str(vertex)
        print "visited: "+str(visited)
        if vertex == goal:
            visited.append(vertex)
            return visited
        if vertex not in visited:
            visited.append(vertex)
            stack.extend(graph[vertex])
    return visited
