from enum import Enum


"""
Object representing a ship
"""
class Ship(object):

    # Possible states for ships
    class State(Enum):
        NULL = 0
        PLACED = 1
        MISS = 2
        HIT = 3
        SUNK = 4

    # Possible orientations on the grid for ships
    class Orientation(Enum):
        VERTICAL = 0
        HORIZONTAL = 1

    # Ship types/names
    MAN_OF_WAR = "Man-of-War"
    GALLEON = "Galleon"
    COG = "Cog"
    SLOOP = "Sloop"
    WHERRY = "Wherry"

    # List of ship types
    SHIPS = [
        MAN_OF_WAR,
        GALLEON,
        COG,
        SLOOP,
        WHERRY
    ]

    # Ship type => ship size
    SIZES = {
        MAN_OF_WAR: 5,
        GALLEON: 4,
        COG: 3,
        SLOOP: 3,
        WHERRY: 2
    }
    
    OUTLINES = {
        MAN_OF_WAR: "grey",
        GALLEON: "burlywood4",
        COG: "cornsilk4",
        SLOOP: "darkgoldenrod4",
        WHERRY: "goldenrod4"
    }

    def __init__(self, coords, type=None, orientation=None):
        self._coords = coords
        self._type = type
        self._orientation = orientation
        self._shipType = None
        self._hits = set([])

        if self._type is not None:
            assert self._type in self.SHIPS
            self._size = self.SIZES[self._type]
            self._outline = self.OUTLINES[self._type]

    """Get the origin of a ship as coordinates """
    def get_origin(self):
        return self._coords

    """Get the size of a ship"""
    def get_size(self):
        return self._size
    
    """Get the outline color corresponding to the ship's type"""
    def get_outline(self):
        return self._outline

    """Get the orientation of a ship"""
    def get_orientation(self):
        return self._orientation

    """Get the type/name of a ship"""
    def get_type(self):
        return self._type

    """Get the tiles a ship is covering"""
    def get_covering_tiles(self):
        if self._orientation is self.Orientation.VERTICAL:
            return [(self._coords[0], self._coords[1] + i) for i in range(self._size)]
        else:
            return [(self._coords[0] + i, self._coords[1]) for i in range(self._size)]

    """Get list of coordinates where ship has been ship"""
    def get_hits(self):
        return [coord in self._hits for coord in self.get_covering_tiles()]

    """Set the orientation of a ship"""
    def set_orientation(self, value):
        assert value in self.Orientation
        self._orientation = value

    """Return true if ship intersects with another"""
    def intersects_with(self, otherShip):
        return len(set(self.get_covering_tiles()).intersection(set(otherShip.get_covering_tiles()))) > 0

    """Return true if ship has been sunk"""
    def is_sunk(self):
        return self._size == len(self._hits)

    """Rotate the ship"""
    def rotate(self):
        if self._orientation is self.Orientation.VERTICAL:
            self._orientation = self.Orientation.HORIZONTAL
        else:
            self._orientation = self.Orientation.VERTICAL

    """Add a new coordinate of the ship's that has been hit"""
    def add_hit(self, x, y):
        self._hits.add((x, y))
