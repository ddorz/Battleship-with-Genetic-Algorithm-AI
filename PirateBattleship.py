from tkinter import *
from tkinter import messagebox as tkmessagebox
from enum import Enum

from MenuPresenter import MenuPresenter
from GridPresenter import GridPresenter
from Ship import Ship
from ShipPanels import ShipPanel, ShipPlacementPanel, ShipDamagePanel, OpponentShipPanel
from BattleshipAI import AI


"""
Controller for the game
"""
class GameController(object):
    
    def __init__(self):
        app = Tk()

        self.winner = None
        self.menuPresenter = MenuPresenter(app, Menu(app))
        self.gamePresenter = GamePresenter(app)

        self._create_event_hooks()
        self.new_game_callback()

        app.mainloop()

    """Add events hooks to UI elements"""
    def _create_event_hooks(self):
        # Add events for clicking radio buttons in ship panel
        for ship in Ship.SHIPS:
            self.gamePresenter.playerFrame.shipPanel.shipRadioButtons[ship].config(command=self.stage_ship_callback)

        # Add event for clicking opponent's grid
        self.gamePresenter.opponentGrid.tag_bind("tile", "<Button-1>", self.turn_callback)

        # Add event for clicking start button
        self.gamePresenter.startButton.config(command=self.start_game_callback)

        # Add events for clicking menu options
        for option, label in self.menuPresenter.MENU_OPTIONS_DICT.items():
            if option is self.menuPresenter.NEW_GAME_MENU_OPTION:
                self.menuPresenter.attach_menu_cmd(label, option, self.new_game_callback)
            elif option is self.menuPresenter.EXIT_MENU_OPTION:
                self.menuPresenter.attach_menu_cmd(label, option, self.exit_callback)
            elif option is self.menuPresenter.SHOW_RULES_MENU_OPTION:
                self.menuPresenter.attach_menu_cmd(label, option, self.menuPresenter.display_game_rules)

    """Callback for game over"""
    def game_over_callback(self, event=None):
        tkmessagebox.showinfo(self.gamePresenter.GAMEOVER_TITLE,
                              self.gamePresenter.GAMEOVER_WIN_MSG if self.winner is True else self.gamePresenter.GAMEOVER_LOSE_MSG)

    """Callback for new game"""
    def new_game_callback(self, event=None):
        self.gamePresenter._placedShips = {ship: False for ship in Ship.SHIPS}
        # Reset both grids and game presenter
        self.gamePresenter.playerGrid.reset()
        self.gamePresenter.opponentGrid.reset()
        self.gamePresenter.reset()
        self.gamePresenter.playerFrame.shipPanel.reset()
        self.winner = None

    """Callback for moving a ship to the placement panel"""
    def stage_ship_callback(self, event=None):
        if self.gamePresenter.playerFrame.shipPanel.get_current_ship() is not None:
            self.gamePresenter.playerFrame.shipPlacementPanel.stage_ship(
                Ship((0, 0), self.gamePresenter.playerFrame.shipPanel.get_current_ship(), Ship.Orientation.VERTICAL))

    """Callback for exiting game"""
    def exit_callback(self, event=None):
        self.gamePresenter.master.destroy()

    """Callback for starting the game"""
    def start_game_callback(self, event=None):
        self.gamePresenter.process_game_state(GamePresenter.GameState.PLAYING)

    """Callback for a new turn"""
    def turn_callback(self, event=None):
        """Player shoots here (1st):"""
        shot = self.gamePresenter.opponentGrid.get_tile_coord(self.gamePresenter.opponentGrid.find_withtag(CURRENT)[0])
        shotTileIdx = self.gamePresenter.opponentGrid.get_tile_idx(*shot)

        # Disable shot tile
        self.gamePresenter.opponentGrid.itemconfig(shotTileIdx, state=DISABLED)

        # See if a ship was sunk
        if self.gamePresenter.opponentGrid.process_shot(shotTileIdx) == Ship.State.SUNK:
            ship = self.gamePresenter.opponentGrid.controller.get_sunk_ship(*shot)
            self.gamePresenter.opponentFrame.opponentShipPanel.set_sunk(ship.get_type())
            # See if that was the last ship (game is over)
            if self.gamePresenter.opponentGrid.controller.all_sunk():
                self.winner = True

        """AI shoots here (2nd):"""
        if self.winner is None:

            aiShot = self.gamePresenter.ai.choose_coordinate()
            shotTileIdx = self.gamePresenter.playerGrid.find_withtag(self.gamePresenter.playerGrid.coordinate_to_str(aiShot[0], aiShot[1]))[0]

            # Update player grid with shot tile. Update ship panels
            result = self.gamePresenter.playerGrid.process_shot(shotTileIdx)
            if result == Ship.State.HIT or result == Ship.State.SUNK:
                ship = self.gamePresenter.playerGrid.controller.get_ship(aiShot[0], aiShot[1])
                assert ship is not None
                self.gamePresenter.playerFrame.shipDamagePanel.update_panel(ship)

            # See if all play ships have been sunk
            if self.gamePresenter.playerGrid.controller.all_sunk():
                self.winner = False

            ### Update AI with result here ###

        # End game if there is a winner
        if self.winner is not None:
            self.game_over_callback()


"""
Presenter for the game
"""
class GamePresenter(Frame):

    # Game states
    class GameState(Enum):
        PLACING = 0
        PLAYING = 1

    # UI geometry
    X_PADDING = 25
    Y_PADDING = 25
    SHIP_PANEL_WIDTH = 150
    BUTTON_PANEL_HEIGHT = 50
    BUTTON_PADDING = 5
    WARNING_BAR_HEIGHT = 40

    # UI background color
    BACKGROUND_COLOR = "white"

    # Labels & text
    PLAYER_GRID_LABEL = "Your Board"
    OPPONENT_GRID_LABEL = "Enemy Board"
    START_BUTTON_LABEL = "Start Game"
    GAMEOVER_TITLE = "Game Over"
    GAMEOVER_WIN_MSG = "You win!"
    GAMEOVER_LOSE_MSG = "You lose!"
    WINDOW_TITLE_NORMAL = "Pirate Battleship"
    GRID_LABEL_FONT = ("Helvetica", 20)

    def __init__(self, app):
        Frame.__init__(self, app)

        self._placedShips = {}

        # Player frame contains player grid and ship panels
        self.playerFrame = Frame(self)
        self.playerFrame.place(x=self.X_PADDING + self.SHIP_PANEL_WIDTH,
                               y=self.Y_PADDING)
        self.playerLabel = Label(self.playerFrame, text=self.PLAYER_GRID_LABEL, font=self.GRID_LABEL_FONT)
        self.playerLabel.pack()
        self.playerGrid = GridPresenter(self.playerFrame, True)
        self.playerGrid.pack(side=LEFT, pady=20)

        # Player ship panel (visible before game has been started while player is placing ships)
        self.playerFrame.shipPanel = ShipPanel(self)
        self.playerFrame.shipPanel.place(x=self.X_PADDING, y=self.Y_PADDING * 5)
        self.playerFrame.shipPanel.set_ship_var(10)

        # Player ship placement panel (visible while player is placing ships, after selecting a ship from ship panel)
        self.playerFrame.shipPlacementPanel = ShipPlacementPanel(self)
        self.playerFrame.shipPlacementPanel.place(x=self.X_PADDING - 10, y=self.Y_PADDING * 10)
        self.playerFrame.shipPlacementPanel.reset()

        # Player ship damage panel (visible during the game)
        self.playerFrame.shipDamagePanel = ShipDamagePanel(self)
        self.playerFrame.shipDamagePanel.config(height=self.playerFrame.winfo_height())
        self.playerFrame.shipDamagePanel.place(x=self.X_PADDING, y=self.Y_PADDING * 5)

        # Opponent frame contains opponent grid and opponent ship panel
        self.opponentFrame = Frame(self)
        self.opponentFrame.place(x=self.playerGrid.TOTAL_PIXELS_PER_DIM + self.X_PADDING * 2 + self.SHIP_PANEL_WIDTH,
                                 y=self.Y_PADDING)
        self.opponentLabel = Label(self.opponentFrame, text=self.OPPONENT_GRID_LABEL, font=self.GRID_LABEL_FONT)
        self.opponentLabel.pack()
        self.opponentGrid = GridPresenter(self.opponentFrame, False)
        self.opponentGrid.pack(side=LEFT, pady=20)

        # Opponent ship panel (visible during the game)
        self.opponentFrame.opponentShipPanel = OpponentShipPanel(self)
        self.opponentFrame.opponentShipPanel.place(x=self.playerGrid.TOTAL_PIXELS_PER_DIM * 2 + self.X_PADDING * 3
                                                     + self.SHIP_PANEL_WIDTH, y=self.Y_PADDING * 5)

        # Start button
        self.buttonFrame = Frame(self)
        self.buttonFrame.place(
            x=self.playerGrid.TOTAL_PIXELS_PER_DIM / 2 - self.playerGrid.HORIZONTAL_OFFSET + ShipPanel.PANEL_WIDTH,
            y=self.playerGrid.TOTAL_PIXELS_PER_DIM + 2 * self.playerGrid.VERTICAL_OFFSET)
        self.startButton = Button(self.buttonFrame, text=self.START_BUTTON_LABEL)

        # Configure sizes and colors
        self.config(height=self.Y_PADDING * 3 + self.playerGrid.TOTAL_PIXELS_PER_DIM
                           + self.BUTTON_PANEL_HEIGHT + self.WARNING_BAR_HEIGHT,
                    background=self.BACKGROUND_COLOR)
        for child in self.winfo_children(): child.config(background=self.BACKGROUND_COLOR)

        self.pack(fill=BOTH, expand=1)
        self.grab_set()
        self.focus_set()

        self.ai = AI(self.playerGrid, self.opponentGrid, geneticAI=True)

    """Unpack the widgets of a frame to achieve the effect of hiding it"""
    def _hide_frame(self, frame):
        frame.lower()
        for child in frame.winfo_children(): child.pack_forget()

    """Process the current game state"""
    def process_game_state(self, state):
        # Placing State (player is placing ships and has not started game)
        if state == self.GameState.PLACING:
            self.config(width=self.X_PADDING * 3 + self.playerGrid.TOTAL_PIXELS_PER_DIM
                              + self.SHIP_PANEL_WIDTH + self.playerFrame.shipPlacementPanel.CANVAS_WIDTH)

            # Show the ship placement panel
            self.playerFrame.shipPlacementPanel.repack_ui_elements()
            self.playerFrame.shipPlacementPanel.lift(aboveThis=self.opponentFrame)
            self.playerFrame.shipPlacementPanel.reset()

            # Disable start button and hide opponent grid / damage panel
            self.startButton.pack(side=LEFT, padx=self.BUTTON_PADDING, pady=self.BUTTON_PADDING)
            self.startButton.config(state=DISABLED)
            self._hide_frame(self.opponentFrame)
            self._hide_frame(self.playerFrame.shipDamagePanel)
            self.playerFrame.shipPanel.lift(aboveThis=self.playerFrame.shipDamagePanel)

            ### AI places its ships here ###
            self.ai.place_all_ships()

        # Playing State (player has started game and is playing AI)
        elif state == self.GameState.PLAYING:
            self.config(width=self.X_PADDING * 4 + self.playerGrid.TOTAL_PIXELS_PER_DIM * 2 + self.SHIP_PANEL_WIDTH * 2)
            self.playerGrid.controller.finalize()
            self.opponentGrid.controller.finalize()

            # Display opponent grid
            self.opponentGrid.config(state=NORMAL)
            self.opponentFrame.lift(aboveThis=self.playerFrame.shipPlacementPanel)
            self.opponentLabel.pack()
            self.opponentGrid.pack(side=LEFT, pady=20)

            # Hide start button and placement panel, display damage panel
            self.startButton.pack_forget()
            self.playerFrame.shipPanel.set_ship_var(10)
            self.playerFrame.shipPlacementPanel.reset()
            self._hide_frame(self.playerFrame.shipPlacementPanel)
            self.playerFrame.shipDamagePanel.repack_canvas()
            self.playerFrame.shipDamagePanel.lift(aboveThis=self.playerFrame.shipPanel)

    """Reset the game"""
    def reset(self):
        self.master.title(self.WINDOW_TITLE_NORMAL)

        # Reset ship placement panel
        self.playerFrame.shipPanel.set_ship_var(10)
        self.playerFrame.shipPlacementPanel.reset()

        # Reset damage panel
        self.playerFrame.shipDamagePanel.reset()
        for ship, button in self.playerFrame.shipPanel.shipRadioButtons.items():
            button.config(foreground="black")

        # Reset grid click events
        for x, y in self.playerGrid.get_all_tiles():
            self.add_tile_click_events(x, y)

        # Reset to PLACING game state
        self.process_game_state(self.GameState.PLACING)

    """Add click events to grid tiles"""
    def add_tile_click_events(self, x, y):
        self.playerGrid.tag_bind(self.playerGrid.coordinate_to_str(x, y),
                                 "<Button-1>",
                                 lambda event: self.add_staged_ship(x, y, lambda: self.place_staged_ship(
                                     self.playerFrame.shipPanel.get_current_ship())))

    """Helper functions place a staged ship on the grid when a tile is clicked"""
    def add_staged_ship(self, x, y, callback):
        s = self.playerFrame.shipPlacementPanel.get_staged_ship()
        if s is not None:
            self.playerGrid.add_ship(x, y, s.get_type(), s.get_orientation(), callback)

    """Place a ship"""
    def place_staged_ship(self, ship):
        self._placedShips[ship] = True
        self.playerFrame.shipPanel.set_placed(ship)
        if all(self._placedShips.values()):
            self.startButton.config(state=NORMAL)


if __name__ == "__main__":
    g = GameController()
