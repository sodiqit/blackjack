from typing import Optional
from typing_extensions import TypedDict
from modules.model.model import Game
from modules.observer.observer import Observer
from modules.utils.constants import OBSERVER_MESSAGES, Deck

GamePayload = TypedDict(
    'GamePayload',
    {
        'game': Game,
        'deck': Deck,
    }
)


class View(Observer):
    _game: Optional[Game] = None
    _deck: Deck = []

    def start_game(self) -> None:
        print('Приветствую! Готов сыграть в Blackjack?')
        input('Нажми любую кнопку чтобы продолжить: ') # TODO: refactor for choices. Not input
        self.notify(OBSERVER_MESSAGES['init'])

    def init_game(self, game_payload: GamePayload) -> None:
        self._game = game_payload['game']
        self._deck = game_payload['deck']

        print(
            f"\nКоличество карт у компьютера: {len(game_payload['game']['state']['computer_cards'])} | " 
            f"Ваше количество очков: {game_payload['game']['state']['human_score']}"
        )
        answer = input('Взять карту') # TODO: add menu for choices 
