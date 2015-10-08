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

    def printSelf(self):
        nodeString=""
        for node in self.elements:
            nodeString+=str(node)+" "
        print nodeString

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

def aStar(graph, weights, start, goal):
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

class Node:
    def __init__(self, vertex, parent):
        self.vertex=vertex
        self.parent=parent

def bfs(graph, start, goal):
    frontier = Queue()
    newNode = Node(start,None)
    frontier.put(newNode)
    visited = []
    visited.append(start)
    currentNode = Node(start,None)
    while not frontier.empty():
        currentNode = frontier.get()
        if currentNode.vertex==goal:
            break
        # print "current: "+str(current)
        # print("Visiting %r" % current)
        for node in graph[currentNode.vertex]:
            if node not in visited:
                newNode=Node(node,currentNode)
                frontier.put(newNode)
                visited.append(node)
    path = []
    while currentNode is not None:
        path.append(currentNode.vertex)
        currentNode=currentNode.parent
    path=path[::-1]
    print "bfs path: "+str(path)
    return path

def recurseDFS(graph, path, node, goal, visited):
    path.append(node)
    visited.append(node)
    for node in graph[node]:
        if node==goal:
            return path
        if node not in visited and goal not in path:
            path=recurseDFS(graph, path, node, goal, visited)
    return path

def dfs(graph, start, goal):
    path=[]
    currentNode=Node(start,None)
    visited, stack = [], [currentNode]
    while stack:
        currentNode = stack.pop()
        if currentNode.vertex == goal:
            break
        if currentNode.vertex not in visited:
            visited.append(currentNode.vertex)
            for node in graph[currentNode.vertex]:
                stack.append(Node(node,currentNode))
    while currentNode is not None:
        path.append(currentNode.vertex)
        currentNode=currentNode.parent
    path=path[::-1]
    print "dfs path: "+str(path)
    return path
 