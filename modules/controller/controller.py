from modules.model.model import Model
from modules.utils.constants import OBSERVER_MESSAGES
from modules.view.view import View


class Controller:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.bind_deps()
        self.view.start_game()

    def bind_deps(self) -> None:
        self.view.subscribe(OBSERVER_MESSAGES['init'], self.model.start)
        self.view.subscribe(OBSERVER_MESSAGES['user_action'], self.model.change_state)
        self.model.subscribe(OBSERVER_MESSAGES['change_state'], self.view.render)
