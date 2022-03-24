from modules.controller.controller import Controller
from modules.model.model import Model
from modules.view.view import View


def main() -> None:
    controller: Controller = Controller(Model(), View())


if __name__ == '__main__':
    main()
