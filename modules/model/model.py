import random
from typing import Literal, Optional, TypedDict

from modules.observer.observer import Observer
from modules.storage.storage import Game, GamerType, Storage
from modules.utils.constants import MAP_CARDS_FOR_SCORE, OBSERVER_MESSAGES, Card, Deck

ChangeStatePayload = TypedDict(
    'ChangeStatePayload',
    {
        'action': Literal['Взять карту'] | Literal['Пас']
    }
)

class Model(Observer):
    _storage: Storage
    _current_game: Game
    _deck: Deck = []

    def __init__(self, storage: Storage) -> None:
        super().__init__()
        self._storage = storage

    def start(self) -> None:
        has_last_not_ended_game = self._storage.has_last_not_ended_game()

        self._current_game = self._storage.get_current_game()
        self._deck = self._current_game['state']['deck']

        if not has_last_not_ended_game:
            self._shuffle_cards()
            self._add_card('computer')
            self._storage.update_game_in_history(self._current_game)

        self.notify(
            OBSERVER_MESSAGES['change_state'],
            self._current_game
        )

    def change_state(self, payload: ChangeStatePayload) -> None:
        self._computer_move()
        if payload['action'] == 'Взять карту':
            self._add_card('human')
        self._calculate_score('human')

        self._storage.update_game_in_history(self._current_game)

        if self._is_finished() or payload['action'] == 'Пас':
            self._finish_game()
        else:
            self.notify(OBSERVER_MESSAGES['change_state'], self._current_game)

    def _finish_game(self) -> None:
        finished_game: Game = {
            **self._current_game,  # type: ignore
            'finished': True,
            'winner': self._get_winner()
        }

        self._current_game = finished_game
        self._storage.update_game_in_history(finished_game)
        self.notify(OBSERVER_MESSAGES['finish'], self._current_game)

    def _get_winner(self) -> Optional[GamerType]:
        user_score = self._current_game['state']['human_score']
        computer_score = self._current_game['state']['computer_score']

        computer_has_big_score_than_user = user_score <= 21 and computer_score > 21
        is_user_winner = (user_score <= 21 and user_score > computer_score) or computer_has_big_score_than_user

        human_has_big_score_than_computer = computer_score <= 21 and user_score > 21
        is_computer_winner = (computer_score <= 21 and computer_score > user_score) or human_has_big_score_than_computer

        if is_user_winner:
            return 'human'

        if is_computer_winner:
            return 'computer'

        return None

    def _is_finished(self) -> bool:
        user_score = self._current_game['state']['human_score']
        computer_score = self._current_game['state']['computer_score']

        return user_score >= 21 or computer_score >= 21

    def _computer_move(self) -> None:
        score = self._current_game['state']['computer_score']

        if score < 16:
            self._add_card('computer')

        self._calculate_score('computer')

    def _calculate_score(self, gamer_type: GamerType) -> None:
        cards: List[Card] = self._current_game['state'][f'{gamer_type}_cards'] # type: ignore
        result = 0
        for card in cards:
            result += MAP_CARDS_FOR_SCORE[card['type']]
        self._current_game['state'][f'{gamer_type}_score'] = result # type: ignore

    def _add_card(self, gamer_type: GamerType) -> None:
        card = self._deck.pop()
        self._current_game['state'][f'{gamer_type}_cards'].append(card)  # type: ignore

    def _shuffle_cards(self) -> None:
        for i in range(1, random.randint(10, 30)):
            random.shuffle(self._deck)
