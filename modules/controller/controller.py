from modules.model.model import Model
from modules.view.view import View


class Controller:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        print('Controller', model, view)
