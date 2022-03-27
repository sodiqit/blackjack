from modules.observer.observer import Observer
from modules.utils.constants import OBSERVER_MESSAGES

class Model(Observer):
    def start(self) -> None:
        print('init model')
        self.notify(OBSERVER_MESSAGES['init'])
