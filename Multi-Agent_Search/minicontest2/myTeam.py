# myTeam.py
# ---------
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions, Grid
import game
from util import nearestPoint
from capture import halfGrid

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed, first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

  # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

# class DummyAgent(CaptureAgent):
#     """
#       A Dummy agent to serve as an example of the necessary agent structure.
#       You should look at baselineTeam.py for more details about how to
#       create an agent as this is the bare minimum.
#       """

#     def registerInitialState(self, gameState):
#         """
#         This method handles the initial setup of the
#         agent to populate useful fields (such as what team
#         we're on).

#         A distanceCalculator instance caches the maze distances
#         between each pair of positions, so your agents can use:
#         self.distancer.getDistance(p1, p2)

#         IMPORTANT: This method may run for at most 15 seconds.
#         """

#         '''
#         Make sure you do not delete the following line. If you would like to
#         use Manhattan distances instead of maze distances in order to save
#         on initialization time, please take a look at
#         CaptureAgent.registerInitialState in captureAgents.py.
#         '''
#         CaptureAgent.registerInitialState(self, gameState)

#         '''
#         Your initialization code goes here, if you need any.
#         '''


#     def chooseAction(self, gameState):
#         """
#         Picks among actions randomly.
#         """
#         actions = gameState.getLegalActions(self.index)

#         '''
#         You should change this in your own agent.
#         '''

#         return random.choice(actions)

class ReflexCaptureAgent(CaptureAgent):
    """
    A base class for reflex agents that chooses score-maximizing actions
    """
 
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)
        width = gameState.data.layout.width
        height = gameState.data.layout.height
        middle = width // 2
        self.middleColumn = []
        for y in range(height):
            if not gameState.hasWall(middle, y):
                self.middleColumn.append((middle, y))
                
        self.initialFoodCount = len(self.getFood(gameState).asList())
        self.teamIndices = self.getTeam(gameState)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        foodLeft = len(self.getFood(gameState).asList())

        if foodLeft <= 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start,pos2)
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction

        return random.choice(bestActions)

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        return features

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.  They can be either
        a counter or a dictionary.
        """
        return {'successorScore': 1.0}


class OffensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that seeks food. This is an agent
    we give you to get an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.
    """
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        numFoodCarrying = myState.numCarrying
        myPos = myState.getPosition()
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        
        foodList = self.getFood(successor).asList()
        features['successor_score'] = -len(foodList)
        if len(foodList) > 0: 
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['food_eval'] = minDistance

        if numFoodCarrying >= 2:
            dist_to_mid = [self.getMazeDistance(myPos, a) for a in self.middleColumn]
            features["mid_eval"] = min(dist_to_mid) # Head back to deposit food
            
        enemyGhosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        activeGhosts = [a for a in enemyGhosts if a.scaredTimer == 0]
        scaredGhosts = [a for a in enemyGhosts if a.scaredTimer > 0]
            
        if len(activeGhosts) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in activeGhosts]
            features['unscared_ghost_eval'] = 10 / min(dists)
            
            capsule_list = self.getCapsules(successor)
            
            if capsule_list:
                closest_capsule = min(capsule_list, key=lambda capsule: self.getMazeDistance(myPos, capsule))
                my_dist_to_capsule = self.getMazeDistance(myPos, closest_capsule)
                ghost_to_capsule = [self.getMazeDistance(closest_capsule, a.getPosition()) for a in activeGhosts]
            
                if min(ghost_to_capsule) > my_dist_to_capsule:
                    # Pursue capsule if there is chance
                    features["capsule_dist"] = my_dist_to_capsule
                
                
        if len(scaredGhosts) > 0:
            dist_timer = [(self.getMazeDistance(myPos, a.getPosition()), a.scaredTimer) for a in scaredGhosts]
            min_dist_timer = min(dist_timer, key=lambda k: k[0])
            features['scared_ghost_eval'] = min_dist_timer[1] / min_dist_timer[0]
                
        return features

    def getWeights(self, gameState, action):
        return {"food_eval": -1, "mid_eval": -2, "unscared_ghost_eval": -1, "scared_ghost_eval": 100, "successor_score": 100, "capsule_dist": -100}

class DefensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that keeps its side Pacman-free. Again,
    this is to give you an idea of what a defensive agent
    could be like.  It is not the best or only way to make
    such an agent.
    """

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemyPacmen = [a for a in enemies if a.isPacman and a.getPosition() != None]
        
        features['on_defense'] = 1
        if myState.isPacman: features['on_defense'] = 0
                
        foodList = self.getFoodYouAreDefending(successor).asList()
        features['food_eval'] = len(foodList)
              
        features['num_invaders'] = len(enemyPacmen)
        
        if len(enemyPacmen) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in enemyPacmen]
            features['enemy_pacmen_eval'] = (1 / min(dists)) if myState.scaredTimer == 0 else (-1 / min(dists))
        
        else:
            enemyGhosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
            closestGhost = min(enemyGhosts, key = lambda ghost: self.getMazeDistance(myPos, ghost.getPosition()))
            dist_to_mid = [self.getMazeDistance(closestGhost.getPosition(), mid_pos) for mid_pos in self.middleColumn]
            # Wait at borderline to defend incoming pacmen
            features['mid_eval'] = min(dist_to_mid)

        if action == Directions.STOP: features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1
        return features

    def getWeights(self, gameState, action):
        return {'food_eval': 100, 'mid_eval': -2, 'num_invaders': -1000, 'on_defense': 1000, 'enemy_pacmen_eval': 10, 'stop': -100, 'reverse': -2}