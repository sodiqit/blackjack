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
