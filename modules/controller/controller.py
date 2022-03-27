from modules.model.model import Model
from modules.utils.constants import OBSERVER_MESSAGES
from modules.view.view import View


class Controller:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.bind_deps()
        self.model.start()

    def bind_deps(self) -> None:
        print('Bind deps')
        self.model.subscribe(OBSERVER_MESSAGES['init'], self.view.start_game)
