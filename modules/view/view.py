from modules.observer.observer import Observer
from modules.utils.constants import OBSERVER_MESSAGES


class View(Observer):
    def start_game(self) -> None:
        print('Приветствую! Готов сыграть в Blackjack?')
        input('Нажми любую кнопку чтобы продолжить: ')
        self.notify(OBSERVER_MESSAGES['init'])
