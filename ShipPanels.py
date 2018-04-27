from tkinter import Frame, Label, StringVar, IntVar, Button, Canvas, W, NW, Radiobutton, LEFT
from Ship import Ship
from enum import Enum


"""
Panel for tracking player ships as they're placed on grid
"""
class ShipPanel(Frame):

    PANEL_WIDTH = 150
    PLACED_BG_COLOR = "green3"
    UNPLACED_BG_COLOR = "white"

    def __init__(self, master):
        Frame.__init__(self, master)

        self._shipVar = IntVar()
        self.shipRadioButtons = {}

        # Create radio buttons for each ship
        for i, shipType in enumerate(Ship.SHIPS):
            radioButton = Radiobutton(self, text=shipType, value=i, justify=LEFT,
                                      variable=self._shipVar, indicatoron=0)
            radioButton.grid(row=i, column=0, padx=10, pady=1, sticky=W)

            self.shipRadioButtons[shipType] = radioButton

    """Reset panel"""
    def reset(self):
        self._shipVar.set(len(Ship.SHIPS) + 1)
        for ship in Ship.SHIPS:
            self.shipRadioButtons[ship].config(background=self.UNPLACED_BG_COLOR)

    """Set a ship as placed. Sets the radio button frame background to green"""
    def set_placed(self, ship):
        self.shipRadioButtons[ship].config(background=self.PLACED_BG_COLOR)

    """Get name of currently selected ship"""
    def get_current_ship(self):
        return None if self.get_ship_var() > len(Ship.SHIPS) else Ship.SHIPS[self.get_ship_var()]

    """Get the variable for currently selected ship"""
    def get_ship_var(self):
        return self._shipVar.get()

    """Set the variable for currently selected ship"""
    def set_ship_var(self, value):
        self._shipVar.set(value)


"""
Panel for displaying/rotating selected player ships as they're placed on the grid
"""
class ShipPlacementPanel(Frame):

    CANVAS_WIDTH = 150
    SHIP_TILE_DIM = 20
    SHIP_TILE_COLOR = "peru"
    TILE_OUTLINE_COLOR = "black"
    TAG = "staging_ship"

    ROTATE_BUTTON_TEXT = {
        Ship.Orientation.VERTICAL: "Make Vertical",
        Ship.Orientation.HORIZONTAL: "Make Horizontal"
    }

    def __init__(self, master):
        Frame.__init__(self, master)

        self._canvas = Canvas(self)
        self._canvas.config(width=self.CANVAS_WIDTH)
        self._canvas.grid(row=2, pady=15)

        self._rotateButtonText = StringVar()
        self._rotateButtonText.set(self.ROTATE_BUTTON_TEXT[Ship.Orientation.HORIZONTAL])
        self._rotateButton = Button(self, textvariable=self._rotateButtonText, command=self.rotate_current_ship)
        self._rotateButton.grid(row=3)

        self._canvas.pack()
        self._rotateButton.pack()

        self._stagedShip = None
        self.clear_staging_grid()
        self._disable_rotate_button()

    """Reset the placement panel"""
    def reset(self):
        self._stagedShip = None
        self.clear_staging_grid()
        self._disable_rotate_button()

    """Repack placement panel UI elements"""
    def repack_ui_elements(self):
        self._canvas.pack()
        self._canvas.grid(row=2, pady=15)
        self._rotateButton.pack()
        self._rotateButton.grid(row=3)

    """Clear staging grid"""
    def clear_staging_grid(self):
        for item in self._canvas.find_withtag(self.TAG):
            self._canvas.delete(item)

    """Draw the ship currently staged for placement"""
    def _draw_staged_ship(self):
        self.clear_staging_grid()

        if self._stagedShip.get_orientation() == Ship.Orientation.VERTICAL:
            xpad = (self._canvas.winfo_width() - self.SHIP_TILE_DIM) / 2.0
            ypad = (self._canvas.winfo_height() - self.SHIP_TILE_DIM * self._stagedShip.get_size()) / 2.0
            for y in range(self._stagedShip.get_size()):
                self._draw_ship_tile(xpad, ypad + y * self.SHIP_TILE_DIM)
        else:
            xpad = (self._canvas.winfo_width() - self.SHIP_TILE_DIM * self._stagedShip.get_size()) / 2.0
            ypad = (self._canvas.winfo_height() - self.SHIP_TILE_DIM) / 2.0
            for x in range(self._stagedShip.get_size()):
                self._draw_ship_tile(xpad + x * self.SHIP_TILE_DIM, ypad)

    """Draw a single tile of the ship"""
    def _draw_ship_tile(self, x, y):
        self._canvas.create_rectangle(x, y, self.SHIP_TILE_DIM + x, self.SHIP_TILE_DIM + y,
                                      fill=self.SHIP_TILE_COLOR, outline=self.TILE_OUTLINE_COLOR, tag=self.TAG)

    """Stage ship for placement"""
    def stage_ship(self, ship):
        if ship is None:
            self._disable_rotate_button()
        else:
            self._stagedShip = ship
            self._rotateButtonText.set(self.ROTATE_BUTTON_TEXT[Ship.Orientation.HORIZONTAL if ship.get_orientation()
                is Ship.Orientation.VERTICAL else Ship.Orientation.VERTICAL])
            self._draw_staged_ship()
            self._enable_rotate_button()

    """Disable rotate button"""
    def _disable_rotate_button(self):
        self._rotateButton.grid_forget()

    """Enable rotate button"""
    def _enable_rotate_button(self):
        self._rotateButton.grid(row=3)

    """Get ship currently staged for placement"""
    def get_staged_ship(self):
        return self._stagedShip

    """Rotate ship currently staged for placement"""
    def rotate_current_ship(self):
        if self._stagedShip is not None:
            self._rotateButtonText.set(self.ROTATE_BUTTON_TEXT[self._stagedShip.get_orientation()])
            self._stagedShip.rotate()
            self._draw_staged_ship()


"""
Panel for tracking damage to player ships as they're shot by opponent
"""
class ShipDamagePanel(Frame):

    class TileState(Enum):
        NORMAL = 0
        HIT = 1

    FILL_COLORS = {
        TileState.NORMAL: "forest green",
        TileState.HIT: "red"
    }

    SQUARE_DIM = 15
    SPACING = 12
    PADDING = 10
    OUTLINE_COLOR = "black"

    def __init__(self, master):
        Frame.__init__(self, master)

        self._canvas = Canvas(self)
        self._canvas.grid(row=1)

        self._shipTiles = {}

        self._create_ship_damage_trackers()

        self._canvas.pack()

    """Repack canvas element"""
    def repack_canvas(self):
        return self._canvas.pack()

    """Update the panel based on new list of hit tiles"""
    def update_panel(self, ship, hitList=None):
        assert ship is not None
        if hitList is None:
            hitList = ship.get_hits()

        for i, hit in enumerate(hitList):
            self._canvas.itemconfig(self._shipTiles[ship.get_type()][i],
                                    fill=self.FILL_COLORS[self.TileState.HIT] if hit else self.FILL_COLORS[self.TileState.NORMAL])

    """Reset the panel"""
    def reset(self):
        for shipType in Ship.SHIPS:
            ship = Ship((0, 0), shipType, Ship.Orientation.VERTICAL)
            self.update_panel(ship, [0] * ship.get_size())

    """Create elements for tracking ship damage"""
    def _create_ship_damage_trackers(self):
        for i, (shipType, shipSize) in enumerate(Ship.SIZES.items()):
            y = i * (self.SPACING * 2 + self.SQUARE_DIM) + self.PADDING
            self._canvas.create_text(self.PADDING, y, text=shipType, anchor=NW)

            self._shipTiles[shipType] = [None] * shipSize

            for j in range(shipSize):
                self._shipTiles[shipType][j] = \
                    self._canvas.create_rectangle(self.PADDING + j * self.SQUARE_DIM,
                                                  self.SPACING + y,
                                                  self.PADDING + (j + 1) * self.SQUARE_DIM,
                                                  self.SPACING + self.SQUARE_DIM + y,
                                                  fill=self.FILL_COLORS[self.TileState.NORMAL],
                                                  outline=self.OUTLINE_COLOR)


"""
Panel for tracking in play/sunk opponent ships during the game
"""
class OpponentShipPanel(Frame):

    SHIP_LABEL_COLOR = "forest green"
    SUNK_SHIP_LABEL_COLOR = "red"

    def __init__(self, master):
        Frame.__init__(self, master)

        self._shipLabels = {}
        for i, shipType in enumerate(Ship.SHIPS):
            self._shipLabels[shipType] = Label(self, text=shipType,
                                               fg=self.SHIP_LABEL_COLOR, justify=LEFT)
            self._shipLabels[shipType].grid(row=i, column=0, sticky=W, ipady=5)

    """Set ship as sunk (updates text color to red)"""
    def set_sunk(self, shipType):
        self._shipLabels[shipType].config(fg=self.SUNK_SHIP_LABEL_COLOR)