from Ship import Ship
from GridPresenter import GridPresenter
import random
from numpy import genfromtxt
from GeneticAlgorithm import GeneticAI

"""
AI opponent class for testing the UI. 
Only places ships on the opponent grid so playing the game can be tested.
"""
class AI(object):

    def __init__(self, playerGrid=None, aiGrid=None, geneticAI=False, aiGridController=None, playerGridController=None):
        self._aiGrid = aiGrid
        self._playerGrid = playerGrid
        if geneticAI:
            genes1 = genfromtxt('GeneticAI/genes1.csv', delimiter=',')
            genes2 = genfromtxt('GeneticAI/genes2.csv', delimiter=',')
            self._geneticAI = GeneticAI(genes1, genes2)
        else:
            self._geneticAI = None

        if self._aiGrid is None or self._playerGrid is None:
            self._aiGridController = aiGridController
            self._playerGridController = playerGridController
        else:
            self._aiGridController = aiGrid.controller
            self._playerGridController = playerGrid.controller

        self._shipPlacements = {}

    """Return true if ship can be placed"""
    def _can_place_ship(self, ship):
        return self._aiGridController.can_add_ship(ship)

    """Place a ship"""
    def _place_ship(self, ship):
        self._aiGridController.add_ship(ship.get_origin(), ship.get_type(), ship.get_orientation())
        self._shipPlacements[ship.get_type()] = ship

    """Place ships on the grid randomly"""
    def place_all_ships(self):
        valid_squares = set(zip(range(GridPresenter.TILES_PER_GRID_DIM), range(GridPresenter.TILES_PER_GRID_DIM)))
        i = 0

        while i < len(Ship.SHIPS) and len(valid_squares) > 0:
            sq = random.sample(valid_squares, 1)[0]
            pos = random.choice([Ship.Orientation.VERTICAL, Ship.Orientation.HORIZONTAL])
            ship = Ship(coords=(sq[0], sq[1]), type=Ship.SHIPS[i], orientation=pos)

            if self._can_place_ship(ship):
                self._place_ship(ship)
                i += 1
                valid_squares.difference_update(set(ship.get_covering_tiles()))

        return len(self._shipPlacements) == len(Ship.SHIPS)

    def choose_coordinate(self):
        if self._geneticAI:
            return self._geneticAI.get_best_action(self._playerGridController)
        else:
            return (0,0)