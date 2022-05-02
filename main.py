from modules.controller.controller import Controller
from modules.model.model import Model
from modules.storage.storage import Storage
from modules.view.view import View


def main() -> None:
    controller: Controller = Controller(Model(Storage()), View())


if __name__ == '__main__':
    main()
