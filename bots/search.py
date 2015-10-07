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

def aStar(graph, weights, start):
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
            return visited
        if vertex not in visited:
            visited.append(vertex)
            stack.extend(graph[vertex])
    return visited
