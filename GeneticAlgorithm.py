from numpy import exp, array, random, dot
import numpy as np
from Ship import Ship
import random
from itertools import combinations_with_replacement

class GeneticAI(object):

    INPUT_LAYER = 4
    HIDDEN_LAYER = 8
    OUTPUT_LAYER = 1

    def __init__(self, genes1, genes2):
        # Neural Network Weights
        self.genes1 = genes1
        self.genes2 = genes2
        self._cache = {}

    """ Runs neural network on all possible positions in the game.
        After finding every possible coordinate. Create a 3x3 matrix around.
        Use this matrix as input to neural network. Output of neural network is
        Heuristic score. Finding position on board with highest heuristic.
    """
    def get_best_action(self, gridcontroller):
        coord = [(0, 0)]
        coord_heuristic = 0

        for x in range(10):
            for y in range(10):
                if gridcontroller.get_tile_state(x, y).value <= 1:
                    inputArray = np.full((3, 3), 0.0)
                    for z in range(x-1,x+2):
                        for w in range(y-1, y+2):
                            if gridcontroller.is_coord_in_range(z, w):
                                state = gridcontroller.get_tile_state(z, w).value
                                value = 0.4

                                if state == 2:
                                    value = 0.0
                                elif state == 3:
                                    value = 2.0
                                elif state == 4:
                                    value = 0.0
                                inputArray[w - (y-1)][z - (x-1)] = value / 4.0


                    # Flatten 2d array to 1d
                    flatArray = np.array(inputArray).ravel()
                    # Remove Center block and corner blocks
                    flatAraryClipped = np.delete(flatArray, [8,6,4,2,0])
                    unique = flatAraryClipped.tostring()
                    if unique in self._cache:
                        h = self._cache[unique]
                    else:
                        h = self._process_action(flatAraryClipped)
                        self._cache[unique] = h
                    if h == coord_heuristic:
                        coord += [(x, y)]
                    elif h > coord_heuristic:
                        coord = [(x, y)]
                        coord_heuristic = h

        return random.choice(coord)

    """ Given a gamestate, count the number of actions until the game is over.
        Return this number as the fitness score.
    """
    def evaluate_fitness_for_gameState(self, gridController, limit=10):
        i = 0
        if limit != -1:
            for _ in range(limit):
                x, y = self.get_best_action(gridController)
                result = gridController.process_shot(x, y)
                if result == Ship.State.HIT:
                    i += 1
            return 100 - (i * limit)
        else:
            while not gridController.all_sunk():
                x, y = self.get_best_action(gridController)
                gridController.process_shot(x, y)
                i += 1

            return i

    """ Internal function for feedforwading the inputs through the NN.
    """
    def _process_action(self, inputs):
        l1_dot = dot(inputs, self.genes1)
        l1_output = self._nonlin(l1_dot)
        l2_dot = dot(l1_output, self.genes2)
        l2_output = self._nonlin(l2_dot)
        return l2_output.item(0)

    """ Internal function for calculating probability using sigmoid function.
    """
    def _nonlin(self, value):
        return 1 / (1 + np.exp(-value))
