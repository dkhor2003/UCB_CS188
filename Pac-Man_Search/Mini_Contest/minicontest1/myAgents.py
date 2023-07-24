# myAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from game import Agent, Directions
from searchProblems import PositionSearchProblem, manhattanHeuristic

import util
from util import manhattanDistance
import time
import search
import random

"""
IMPORTANT
`agent` defines which agent you will use. By default, it is set to ClosestDotAgent,
but when you're ready to test your own agent, replace it with MyAgent
"""
pacmen_num = 0
pacmen_status = {}
pacmen_positions = []

def createAgents(num_pacmen, agent='MyAgent'): #ClosestDotAgent
    global pacmen_num
    pacmen_num = num_pacmen
    return [eval(agent)(index=i) for i in range(num_pacmen)]

class MyAgent(Agent):
    """
    Implementation of your agent.
    """

    def initialize(self):
        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """

        "*** YOUR CODE HERE"
        global pacmen_status, pacmen_positions, pacmen_num
        pacmen_status = {agentIndex: [None, []] for agentIndex in range(pacmen_num)}
        pacmen_positions = [(-1, -1) for agentIndex in range(pacmen_num)]
        
    def getAction(self, gameState):
        global pacmen_status, pacmen_positions
        pacmen_positions[self.index] = gameState.getPacmanPosition(self.index)
        problem = AnyFoodSearchProblem(gameState, self.index)
        food_grid = gameState.getFood()
        food_list = food_grid.asList()
        if pacmen_status[self.index][0] not in food_list:
            pacmen_status[self.index][1] = []
    
        rand = random.randint(0, len(food_list)-1)
        random_food = food_list[rand]
        if pacmen_status[self.index][0] != random_food and len(pacmen_status[self.index][1]) == 0:
            pacmen_status[self.index][0] = random_food
            close_to_self = []
            self_position = pacmen_positions[self.index]
            for pacman_index in range(pacmen_num):
                other_position = pacmen_positions[pacman_index]
                close_to_self.append(pacman_index != self.index and manhattanDistance(self_position, other_position) <= 2)
            
            nearby_pacmen = [i for i in range(len(close_to_self)) if close_to_self[i]]
            
            def computeDistanceToFood(pacmen_list, target):
                dist_to_target = []
                for pacman in pacmen_list:
                    dist_to_target.append(manhattanDistance(pacmen_positions[pacman], target))
                return dist_to_target
            
            if nearby_pacmen:
                min_dist_food = [float("inf"), None]
                for food in food_list:
                    self_dist = manhattanDistance(self_position, food)
                    if self_dist < min(computeDistanceToFood(nearby_pacmen, food)) and self_dist < min_dist_food[0]:
                        min_dist_food = [self_dist, food]
                if min_dist_food[1] == None:
                    pacmen_status[self.index][1] = [Directions.STOP]
                else:
                    goal = min_dist_food[1]
                    problem = PositionSearchProblem(gameState, agentIndex=self.index, goal=goal, warn=False, visualize=False)
                    pacmen_status[self.index][1] = search.astar(problem, heuristic=manhattanHeuristic)
                
            else:
                pacmen_status[self.index][1] = search.bfs(problem)
                
        elif pacmen_status[self.index][0] == random_food and len(pacmen_status[self.index][1]) == 0:
            pacmen_status[self.index][1] = search.bfs(problem)

        return pacmen_status[self.index][1].pop(0)

        

"""
Put any other SearchProblems or search methods below. You may also import classes/methods in
search.py and searchProblems.py. (ClosestDotAgent as an example below)
"""

class ClosestDotAgent(Agent):

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition(self.index)
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState, self.index)
        "*** YOUR CODE HERE ***"
        return search.bfs(problem)
    

    def getAction(self, state):
        return self.findPathToClosestDot(state)[0]

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """
        x,y = state

        "*** YOUR CODE HERE ***"
        return self.food[x][y]
