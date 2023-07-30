# multiAgents.py
# --------------
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

from __future__ import division
from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        if successorGameState.isWin():
            return successorGameState.getScore() + 999
    
        if successorGameState.isLose():
            return successorGameState.getScore() - 999
    
        food_list = newFood.asList()
        ghost_positions = successorGameState.getGhostPositions()  
        calc_dist = lambda x: manhattanDistance(x, newPos)
        nearest_scared_ghost = [float("inf"), 0]
        nearest_ghost_dist = float("inf")
    
        for ghost_pos, scared_time in zip(ghost_positions, newScaredTimes):
            dist_to_ghost = calc_dist(ghost_pos)
            if scared_time > 0 and dist_to_ghost < nearest_scared_ghost[0]:
                nearest_scared_ghost = [dist_to_ghost, scared_time]
            elif dist_to_ghost < nearest_ghost_dist:
                nearest_ghost_dist = dist_to_ghost
  
        food_list = sorted(food_list, key=calc_dist)
        nearest_food_dist = calc_dist(food_list[0])
    
        food_score = 1 / nearest_food_dist
        ghost_score = -1 / nearest_ghost_dist
        scared_ghost_score = nearest_scared_ghost[1] / nearest_scared_ghost[0]
    
    
        return successorGameState.getScore() + food_score + ghost_score + scared_ghost_score
    

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """
    
    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        minimaxAction = self.value(gameState, self.index, 0)[1]
        return minimaxAction
        
    def value(self, gameState, agentIndex, moves_made):
        if moves_made >= self.depth or gameState.isWin() or gameState.isLose():
            return [self.evaluationFunction(gameState), Directions.STOP]
        if agentIndex == 0:
            return self.min_or_max(gameState, agentIndex, moves_made, mode="MAX")
        else:
            return self.min_or_max(gameState, agentIndex, moves_made, mode="MIN")
    
    def min_or_max(self, gameState, agentIndex, moves_made, mode):
        if mode == "MAX":
            score = float("-inf")
            compare = lambda new_score, prev_score: new_score > prev_score
        elif mode == "MIN":
            score = float("inf")
            compare = lambda new_score, prev_score: new_score < prev_score
        else:
            raise Exception("Choose between 'MAX' and 'MIN' only!")
            
        bestAction = Directions.STOP
        legalActions = gameState.getLegalActions(agentIndex)
        if agentIndex + 1 < gameState.getNumAgents():
            nextAgentIndex = agentIndex + 1
        else:
            nextAgentIndex = 0
            moves_made += 1
                
        for action in legalActions:
            successorState = gameState.generateSuccessor(agentIndex, action)
            next_state_utility = self.value(successorState, nextAgentIndex, moves_made)
            if compare(next_state_utility[0], score):
                score = next_state_utility[0]
                bestAction = action
            
        return [score, bestAction]
        

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        alpha = float("-inf")
        beta = float("inf")
        minimaxAction = self.value(gameState, self.index, alpha, beta, 0)[1]
        return minimaxAction
        
    def value(self, gameState, agentIndex, alpha, beta, moves_made):
        if moves_made >= self.depth or gameState.isWin() or gameState.isLose():
            return [self.evaluationFunction(gameState), Directions.STOP]
        if agentIndex == 0:
            return self.min_or_max(gameState, agentIndex, alpha, beta, moves_made, mode="MAX")
        else:
            return self.min_or_max(gameState, agentIndex, alpha, beta, moves_made, mode="MIN")
    
    def min_or_max(self, gameState, agentIndex, alpha, beta, moves_made, mode):
        if mode == "MAX":
            score = float("-inf")
            compare = lambda new_score, prev_score: new_score > prev_score
            best_option = beta
            max_mode = True
        elif mode == "MIN":
            score = float("inf")
            compare = lambda new_score, prev_score: new_score < prev_score
            best_option = alpha
            max_mode = False
        else:
            raise Exception("Choose between 'MAX' and 'MIN' only!")
            
        bestAction = Directions.STOP
        legalActions = gameState.getLegalActions(agentIndex)
        if agentIndex + 1 < gameState.getNumAgents():
            nextAgentIndex = agentIndex + 1
        else:
            nextAgentIndex = 0
            moves_made += 1
                
        for action in legalActions:
            successorState = gameState.generateSuccessor(agentIndex, action)
            next_state_utility = self.value(successorState, nextAgentIndex, alpha, beta, moves_made)
            if compare(next_state_utility[0], score):
                score = next_state_utility[0]
                bestAction = action
                
            if compare(score, best_option):
                return [score, bestAction]
            
            if max_mode:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)
                
            
        return [score, bestAction]

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        expectimaxAction = self.value(gameState, self.index, 0)[1]
        return expectimaxAction
        
    def value(self, gameState, agentIndex, moves_made):
        if moves_made >= self.depth or gameState.isWin() or gameState.isLose():
            return [self.evaluationFunction(gameState), Directions.STOP]
        if agentIndex == 0:
            return self.maxValue(gameState, agentIndex, moves_made)
        else:
            return self.expValue(gameState, agentIndex, moves_made)
    
    
    def maxValue(self, gameState, agentIndex, moves_made):
        score = float("-inf")
        bestAction = Directions.STOP
        legalActions = gameState.getLegalActions(agentIndex)
        if agentIndex + 1 < gameState.getNumAgents():
            nextAgentIndex = agentIndex + 1
        else:
            nextAgentIndex = 0
            moves_made += 1
            
        for action in legalActions:
            successorState = gameState.generateSuccessor(agentIndex, action)
            next_state_utility = self.value(successorState, nextAgentIndex, moves_made)
            if next_state_utility[0] > score:
                score = next_state_utility[0]
                bestAction = action
            
        return [score, bestAction]
    
    def expValue(self, gameState, agentIndex, moves_made):
        score = 0
        bestAction = Directions.STOP
        legalActions = gameState.getLegalActions(agentIndex)
        chance = (1 / len(legalActions))
        if agentIndex + 1 < gameState.getNumAgents():
            nextAgentIndex = agentIndex + 1
        else:
            nextAgentIndex = 0
            moves_made += 1

        for action in legalActions:
            successorState = gameState.generateSuccessor(agentIndex, action)
            next_state_utility = self.value(successorState, nextAgentIndex, moves_made)
            score += (next_state_utility[0] * chance)
            
        return [score, bestAction]
        
        

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: Evaluated states based on the distance to nearest unscared ghost, nearest scared ghost and its scared time,
                   and the nearest food. The closer the unscared ghost is to pacman, the lower the score; the closer the scared
                   ghost is to pacman and the longer the scared time, the higher the score; the closer the food is to pacman, 
                   the higher the score.
    """
    "*** YOUR CODE HERE ***"
    if currentGameState.isWin():
        return currentGameState.getScore() + 999
    
    if currentGameState.isLose():
        return currentGameState.getScore() - 999
    
    food_list = currentGameState.getFood().asList()
    pacman_pos = currentGameState.getPacmanPosition() 
    ghost_states = currentGameState.getGhostStates()
    scared_times = [ghostState.scaredTimer for ghostState in ghost_states]
    ghost_positions = currentGameState.getGhostPositions()  
    calc_dist = lambda x: manhattanDistance(x, pacman_pos)
    nearest_scared_ghost = [float("inf"), 0]
    nearest_ghost_dist = float("inf")
    
    for ghost_pos, scared_time in zip(ghost_positions, scared_times):
        dist_to_ghost = calc_dist(ghost_pos)
        if scared_time > 0 and dist_to_ghost < nearest_scared_ghost[0]:
            nearest_scared_ghost = [dist_to_ghost, scared_time]
        elif dist_to_ghost < nearest_ghost_dist:
            nearest_ghost_dist = dist_to_ghost
  
    food_list = sorted(food_list, key=calc_dist)
    nearest_food_dist = calc_dist(food_list[0])
        
    food_score = 1 / nearest_food_dist
    ghost_score = -1 / nearest_ghost_dist
    scared_ghost_score = nearest_scared_ghost[1] / nearest_scared_ghost[0]
    
    
    return currentGameState.getScore() + food_score + ghost_score + scared_ghost_score

    

# Abbreviation
better = betterEvaluationFunction

