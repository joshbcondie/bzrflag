# Sample code from http://www.redblobgames.com/pathfinding/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
#
# Feel free to use this code in your own projects, including commercial projects
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>

import Queue
import collections
import heapq

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

class Node:
    def __init__(self, vertex, parent):
        self.vertex=vertex
        self.parent=parent
        self.cost=0

    def setCost(self,weight):
        self.cost=weight

    def __eq__(self,other):
        if type(other) is not Node:
            return False
        if other.vertex==self.vertex:
            return True
        return False

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def aStar(graph, weights, vertices, start, goal):
    frontier = PriorityQueue()
    currentNode=Node(start,None)
    frontier.put(currentNode, 0)
    nodesSoFar=[]
    nodesSoFar.append(currentNode)
    while not frontier.empty():
        print "currentNode: "+str(currentNode.vertex)
        currentNode = frontier.get()
        
        if currentNode.vertex == goal:
            break
        
        for node in graph[currentNode.vertex]:
            print "checking node "+str(node)+" from "+str(currentNode.vertex)
            newNode=None
            index=-1
            for i in range(len(nodesSoFar)):
                if nodesSoFar[i].vertex==node:
                    newNode=nodesSoFar[i]
                    index=i
                    break
            newCost = currentNode.cost + weights[currentNode.vertex][node]
            if index==-1 or newCost < newNode.cost:
                priority = newCost + heuristic(vertices[currentNode.vertex],vertices[node])
                if newNode is None:
                    newNode=Node(node,currentNode)
                newNode.setCost(newCost)
                frontier.put(newNode, priority)
                if index is not -1:
                    nodesSoFar[index]=newNode
                else:
                    nodesSoFar.append(newNode)
        currentNode=newNode
    path = []
    while currentNode is not None:
        path.append(currentNode.vertex)
        currentNode=currentNode.parent
    path=path[::-1]
    print "a star path: "+str(path)
    return path

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

def dfs(graph, start, goal, obstacles):
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

def show_obstacle(self, obstacle):
    # print obstacle[0][0]
    pyplot.plot([obstacle[0][0],obstacle[1][0],obstacle[2][0],obstacle[3][0],obstacle[0][0]],[obstacle[0][1],obstacle[1][1],obstacle[2][1],obstacle[3][1],obstacle[0][1]])

 
def plotSearchProgress(vertices, currentNode, visited, obstacles):
    pyplot.figure(1)
    for obstacle in obstacles:
        self.show_obstacle(obstacle)

    for vertex in visited:
        pyplot.plot(vertices[vertex],'ro')

    # for node in visibilityGraph:
    #     for neighbor in node.neighbors:
    #         draw_edge = False
    #         if node.search_state == SearchStates.visited and neighbor.search_state == SearchStates.visited:
    #             edge_color = 'r'
    #             draw_edge = True
    #         elif node.search_state == SearchStates.visited and neighbor.search_state == SearchStates.frontier:
    #             edge_color = 'b'
    #             draw_edge = True

    #         if draw_edge:
    #             plot([node.point[0], neighbor.point[0]], [node.point[1], neighbor.point[1]], edge_color)

    #     node_color = 'go'
    #     if node.search_state == SearchStates.visited:
    #         node_color = 'ro'
    #     elif node.search_state == SearchStates.frontier:
    #         node_color = 'bo'

        # Plot a colored point for the node
        # plot([node.point[0]], [node.point[1]], node_color)
        
    pyplot.show()