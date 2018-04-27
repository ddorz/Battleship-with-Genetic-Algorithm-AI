from tkinter import PhotoImage, Canvas, NORMAL
from collections import OrderedDict
from Ship import Ship
import Utils

"""
Presenter for game grids
"""
class GridPresenter(Canvas):

    # Grid geometry
    PIXELS_PER_TILE = 60
    TILES_PER_GRID_DIM = 10
    HORIZONTAL_OFFSET = 30
    VERTICAL_OFFSET = 30
    TOTAL_PIXELS_PER_DIM = PIXELS_PER_TILE * TILES_PER_GRID_DIM + HORIZONTAL_OFFSET + VERTICAL_OFFSET

    # Grid outline color
    GRID_OUTLINE_COLOR = "black"

    # State => grid tile color
    TILE_COLORS = {
        Ship.State.NULL: Utils.null_fill(),
        Ship.State.MISS: "grey",
        Ship.State.HIT: "red",
        Ship.State.SUNK: "black",
        Ship.State.PLACED: "peru"
    }

    TILE_TAG = "tile"

    def __init__(self, app, home=False):
        Canvas.__init__(self, app)

        self.gif1 = PhotoImage(file='incl/water6.gif')

        self.config(height=self.TOTAL_PIXELS_PER_DIM, width=self.TOTAL_PIXELS_PER_DIM)

        # _home is set true for human player's grid
        self._home = home
        self.controller = GridController(self.TILES_PER_GRID_DIM)
        self._ships = {}
        self._prevState = {}

        self._generate_grid()

    """Generate the grid"""
    def _generate_grid(self):
        self._tiles = {}
        self._coords = {}

        # Add background image to grid
        self.create_image((self.HORIZONTAL_OFFSET, self.VERTICAL_OFFSET),
                          image=self.gif1,
                          state=NORMAL,
                          anchor='nw')
        self.pack()

        # Add coordinate labels to top and left side of grid
        for i in range (self.TILES_PER_GRID_DIM):
            self.create_text((self.PIXELS_PER_TILE * (i + 0.5) + self.HORIZONTAL_OFFSET, self.VERTICAL_OFFSET / 2),
                             text=str(i + 1))
            self.create_text((self.HORIZONTAL_OFFSET / 2, self.PIXELS_PER_TILE * (i + 0.5) + self.VERTICAL_OFFSET),
                             text=chr(i + ord('A')))

        # Draw the coordinate grid
        for i in range(self.TILES_PER_GRID_DIM):
            for j in range(self.TILES_PER_GRID_DIM):
                bbox = (self.PIXELS_PER_TILE * i + self.HORIZONTAL_OFFSET,
                        self.PIXELS_PER_TILE * j + self.VERTICAL_OFFSET,
                        self.PIXELS_PER_TILE * (i + 1) + self.HORIZONTAL_OFFSET,
                        self.PIXELS_PER_TILE * (j + 1) + self.VERTICAL_OFFSET)
                idx = self.create_rectangle(bbox,
                                            outline=self.GRID_OUTLINE_COLOR,
                                            tags=(self.TILE_TAG, self.coordinate_to_str(i, j)))
                self._tiles[idx] = (i, j)
                self._coords[(i, j)] = idx

    """Convert x, y coordinates to string"""
    def coordinate_to_str(self, x, y):
        return chr(x + ord('A')) + str(y + 1)

    """Get the coordinates of a tile given tile idx"""
    def get_tile_coord(self, tileIdx):
        return self._tiles[tileIdx]

    """Get all tiles"""
    def get_all_tiles(self):
        return self._tiles.values()

    """Get the idx of a tile given x, y coordinate"""
    def get_tile_idx(self, x, y):
        return self._coords[(x, y)]

    """'Process a shot tile"""
    def process_shot(self, tileIdx, callback=None):
        """Shoot this tile. Return the result."""

        i, j = self.get_tile_coord(tileIdx)
        result = self.controller.process_shot(i, j)

        if result == Ship.State.SUNK:
            for x, y in self.controller.get_sunk_ship(i, j).get_covering_tiles():
                self.itemconfigure(self.find_withtag(self.coordinate_to_str(x, y)), fill=self.TILE_COLORS[Ship.State.SUNK])
        else:
            self.itemconfigure(self.find_withtag(self.coordinate_to_str(i, j)), fill=self.TILE_COLORS[result])

        return result

    """Reset the controller"""
    def reset(self):
        self.controller.reset()
        self.unbind("<Button>")
        self._ships = {}
        self._prevState = {}

        # Reset tiles
        for i, (x, y) in self._tiles.items():
            self._prevState[i] = False
            self.itemconfig(i, state=NORMAL)
            self._set_tile_state(x, y)

    """Add a ship to the grid"""
    def add_ship_to_grid(self, ship):
        if ship.is_sunk():
            for x, y in ship.get_covering_tiles():
                self._set_tile_state(x, y, state=Ship.State.SUNK)
        else:
            for coord, hit in zip(ship.get_covering_tiles(), ship.get_hits()):
                if hit or self._home:
                    self._set_tile_state(coord[0], coord[1], state=Ship.State.HIT if hit else Ship.State.PLACED)
                    self.itemconfigure(self.find_withtag(self.coordinate_to_str(coord[0], coord[1])), outline=ship.get_outline())

    """Add a new ship"""
    def add_ship(self, x, y, ship, orientation, callback=None):
        coords = (x, y)

        if ship is None:
            return False

        result = self.controller.can_add_ship(Ship(coords, ship, orientation))
        if result:
            if ship in self.controller.get_ships():
                prev_ship = self.controller.get_ships()[ship]
                for tile in prev_ship.get_covering_tiles():
                    self._set_tile_state(*tile)  # reset state

            self.controller.add_ship(coords, ship, orientation)
            self.add_ship_to_grid(Ship(coords, ship, orientation))

            if callback is not None:
                callback()

        return result

    """Set the state of tile at x, y"""
    def _set_tile_state(self, x, y, state=None):
        state = self.controller.get_tile_state(x, y) if state is None else state
        self.itemconfigure(self.find_withtag(self.coordinate_to_str(x, y)), fill=self.TILE_COLORS[state], outline="black")


"""
Controller for game grids
"""
class GridController(object):

    MAX_SHIPS = len(Ship.SHIPS)

    def __init__(self, dim):
        self._gridDim = dim
        self._ships = {}
        self._coords = {}
        self._finalized = False
        self._stateDict = OrderedDict()

    def __deepcopy__(self, memo):
        from copy import copy, deepcopy
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    """Reset the grid"""
    def reset(self):
        self._ships = {}
        self._coords = {}
        self._finalized = False
        self._stateDict = OrderedDict()

    """Create _coords object for ship lookup"""
    def finalize(self, errorCheck=True):
        if errorCheck:
            assert len(self._ships) == self.MAX_SHIPS

        for shipName, ship in self._ships.items():
            for coord in ship.get_covering_tiles():
                self._coords[coord] = shipName

        self._finalized = True

    """Get a sunken ship on the grid at x, y coordinate"""
    def get_sunk_ship(self, x, y):
        if self._ships[self._coords[(x, y)]].is_sunk():
            return self._ships[self._coords[(x, y)]]

    """Get a ship on the grid at x, y coordinate"""
    def get_ship(self, x, y):
        if (x, y) in self._coords:
            return self._ships[self._coords[(x, y)]]

    """Process a shot on the grid"""
    def process_shot(self, x, y):
        if not self._finalized:
            self.finalize()

        if (x, y) in self._coords:
            ship = self._ships[self._coords[(x, y)]]
            ship.add_hit(x, y)
            if ship.is_sunk():
                for xy in ship.get_covering_tiles():
                    self._stateDict[xy] = Ship.State.SUNK
                self._stateDict[(x, y)] = Ship.State.SUNK
                return Ship.State.SUNK
            else:
                self._stateDict[(x, y)] = Ship.State.HIT
                return Ship.State.HIT

        self._stateDict[(x, y)] = Ship.State.MISS
        return Ship.State.MISS

    """Returns the number of ships sunk"""
    def num_sunk(self):
        return sum([ship.is_sunk() for ship in self._ships.values()])

    """Return true if all ships on the grid have been sunk"""
    def all_sunk(self):
        return all([ship.is_sunk() for ship in self._ships.values()])

    """Return true if all ships have been placed on the grid"""
    def all_placed(self):
        return len(self._ships) == self.MAX_SHIPS

    """Get the current state of tile at x, y coordinate"""
    def get_tile_state(self, x, y):
        coord = (x, y)
        return self._stateDict[coord] if coord in self._stateDict else Ship.State.NULL

    """Returns true if x, y coordinate is within range of the grid dimensions"""
    def is_coord_in_range(self, x, y):
        return 0 <= x < self._gridDim and 0 <= y < self._gridDim

    """Verify there are no conflicts with a ship to be placed.
        This prevents ships from being able to intersect"""
    def _no_ship_conflicts(self, ship):
        for otherShipName, otherShip in self._ships.items():
            # ignore unsunk ships once ship placement is finalized
            if self._finalized and not otherShip.is_sunk():
                continue
            if otherShipName == ship.get_type():
                continue
            if ship.intersects_with(otherShip):
                return False
        return True

    """Returns true if the given ship object can be added to grid"""
    def can_add_ship(self, ship):
        return all([self.is_coord_in_range(x, y) for x, y in ship.get_covering_tiles()]) \
               and self._no_ship_conflicts(ship)

    """Add a ship to the grid"""
    def add_ship(self, coord, shipType, orientation):
        ship = Ship(coord, shipType, orientation)
        if self.can_add_ship(ship):
            self._ships[shipType] = ship
            return True
        else:
            return False

    """Get _ships object, a mapping of ship types to ship objects"""
    def get_ships(self):
        return self._ships
