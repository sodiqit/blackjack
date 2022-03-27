from modules.observer.observer import Observer
from modules.utils.constants import OBSERVER_MESSAGES, Deck


class View(Observer):
    _deck: Deck = []

    def start_game(self) -> None:
        print('Приветствую! Готов сыграть в Blackjack?')
        input('Нажми любую кнопку чтобы продолжить: ')
        self.notify(OBSERVER_MESSAGES['init'])

    def init_deck(self, deck: Deck) -> None:
        self._deck = deck

        print(f'Колода успешно создана: {len(self._deck)} карт')

        for card in self._deck:
            print(f"Масть: {card['suit']}\n Тип: {card['type']} \n")
