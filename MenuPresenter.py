from tkinter import Frame, Menu, messagebox as tkmessagebox

"""
Presenter for bar menu
"""
class MenuPresenter(Frame):

    # Menu labels
    FILE_MENU_LABEL = "File"
    HELP_MENU_LABEL = "Help"

    # Menu options
    NEW_GAME_MENU_OPTION = "New Game"
    EXIT_MENU_OPTION = "Exit"
    SHOW_RULES_MENU_OPTION = "Show Rules"

    # Menu options mapped to their respective menus
    MENU_OPTIONS_DICT = {
        NEW_GAME_MENU_OPTION: FILE_MENU_LABEL,
        EXIT_MENU_OPTION: FILE_MENU_LABEL,
        SHOW_RULES_MENU_OPTION: HELP_MENU_LABEL
    }

    # Rules msg box title and rules doc
    RULES_MSGBOX_TITLE = "Pirate Battleship Rules"
    RULES_FILE_PATH = "incl/rules.txt"

    def __init__(self, app, menu):
        Frame.__init__(self, app)

        self.fileMenu = Menu(menu, tearoff=0)
        self.helpMenu = Menu(menu, tearoff=0)
        self.fileMenuOptions = {}
        self.helpMenuOptions = {}

        self._create_menus()

        menu.add_cascade(label=self.FILE_MENU_LABEL, menu=self.fileMenu)
        menu.add_cascade(label=self.HELP_MENU_LABEL, menu=self.helpMenu)
        self.master.config(menu=menu)

    """Create menus for top menu bar and attach options"""
    def _create_menus(self):
        i = 0
        j = 0
        for menuOption, menuLabel in self.MENU_OPTIONS_DICT.items():
            if menuLabel is self.FILE_MENU_LABEL:
                self.fileMenu.add_command(label=menuOption)
                self.fileMenuOptions[self._create_menu_key(menuLabel, menuOption)] = i
                i += 1
            elif menuLabel is self.HELP_MENU_LABEL:
                self.helpMenu.add_command(label=menuOption)
                self.helpMenuOptions[self._create_menu_key(menuLabel, menuOption)] = j
                j += 1

    """Attach a function to a menu option"""
    def attach_menu_cmd(self, label, option, cmd):
        if label is self.FILE_MENU_LABEL:
            self.fileMenu.entryconfig(self.fileMenuOptions[self._create_menu_key(label, option)], command=cmd)
        elif label is self.HELP_MENU_LABEL:
            self.helpMenu.entryconfig(self.helpMenuOptions[self._create_menu_key(label, option)], command=cmd)

    """Display the games rules (for 'Rules' menu option)"""
    def display_game_rules(self):
        file = open(self.RULES_FILE_PATH, "r")
        tkmessagebox.showinfo(self.RULES_MSGBOX_TITLE, file.read())
        file.close()

    """Given a menu label and menu option, create a key for fileMenuOptions/helpMenuOptions dicts"""
    @staticmethod
    def _create_menu_key(menuLabel, menuOption):
            return menuLabel + ":" + menuOption.strip(" ")