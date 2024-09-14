from PyQt5.QtWidgets import QMenuBar, QAction

class MenuComponent(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)

    def add_menu(self, title):
        menu = self.addMenu(title)
        return menu

    def add_action(self, menu, action_name, status_tip, trigger_function):
        action = QAction(action_name, self)
        action.setStatusTip(status_tip)
        action.triggered.connect(trigger_function)
        menu.addAction(action)
        return action

