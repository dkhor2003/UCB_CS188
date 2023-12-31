# valueIterationAgents.py
# -----------------------
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


# valueIterationAgents.py
# -----------------------
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


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.new_values = util.Counter() # A Counter is a dict with default 0
        self.prev_values = util.Counter()
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for depth in range(self.iterations):
            all_states = self.mdp.getStates()
            for state in all_states: 
                action_qVal = self.computeActionFromValues(state)
            self.prev_values = self.new_values.copy()
            
    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.prev_values[state]

    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        next_states = self.mdp.getTransitionStatesAndProbs(state, action)
        q_value = 0
        for next_state in next_states:
            reward = self.mdp.getReward(state, action, next_state[0])
            probability = next_state[1]
            q_value += probability * (reward + (self.discount * self.getValue(next_state[0])))
            
        return q_value

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
            return None
        actions = self.mdp.getPossibleActions(state)
        action_qVal = [(action, self.getQValue(state, action)) for action in actions]
        best_action_qVal = max(action_qVal, key=lambda qVal: qVal[1])
        self.new_values[state] = best_action_qVal[1]
        return best_action_qVal[0]

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        all_states = self.mdp.getStates() 
        for depth in range(self.iterations):
            state = all_states[depth % len(all_states)]
            self.computeActionFromValues(state)
            self.prev_values = self.new_values.copy()
            

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        all_states = self.mdp.getStates()
        state_pred = {state: set() for state in all_states}
        for state in state_pred:
            actions = self.mdp.getPossibleActions(state)
            for action in actions:
                transition_states = self.mdp.getTransitionStatesAndProbs(state, action)
                for next_state in transition_states:
                    if next_state[1] > 0: state_pred[next_state[0]].add(state)
                
        heap = util.PriorityQueue()
        
        for state in state_pred:
            if self.mdp.isTerminal(state):
                continue
                
            actions = self.mdp.getPossibleActions(state)
            max_qVal = max([self.computeQValueFromValues(state, action) for action in actions])
            diff = abs(max_qVal - self.getValue(state))
            heap.update(state, -diff)
            
        for iteration in range(self.iterations):
            if heap.isEmpty():
                break
            state = heap.pop()
            self.computeActionFromValues(state)
            self.prev_values = self.new_values.copy()
            for pred in state_pred[state]:
                actions = self.mdp.getPossibleActions(pred)
                max_qVal = max([self.computeQValueFromValues(pred, action) for action in actions])
                diff = abs(max_qVal - self.getValue(pred))
                if diff > self.theta:
                    heap.update(pred, -diff)
                    
            self.prev_values = self.new_values.copy()
            
                
            

