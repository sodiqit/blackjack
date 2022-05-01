import random
import json
import os
from typing import Literal, Union, Optional, TypedDict
from uuid import uuid4
from io import StringIO

from modules.observer.observer import Observer
from modules.utils.constants import OBSERVER_MESSAGES, Card, generate_deck, Deck

GamerType = Union[Literal['human'], Literal['computer']]

State = TypedDict(
    'State',
    {
        'computer_cards': list[Card],
        'human_cards': list[Card],
        'human_score': int,
        'computer_score': int,
        'deck': Deck,
    }
)

Game = TypedDict(
    'Game',
    {
        'game_uuid': str,
        'events': list,
        'state': State,
        'finished': bool,
        'winner': Optional[GamerType],
    }
)

ChangeStatePayload = TypedDict(
    'ChangeStatePayload',
    {
        'action': Literal['Взять карту'] | Literal['Пас']
    }
)

''' 
TODO: Add method for calculation scores for computer and player;
      Add sync history file with change game state;
      Add handle exceptions and if game crash, take last state and continue game;
      Relocate deck into game state;
'''


class Model(Observer):
    _history_file_path = ''
    _media_path = ''
    _current_game: Optional[Game] = None
    _deck: Deck = []

    def __init__(self) -> None:
        super().__init__()
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        path = 'media/history.json'
        self._media_path = os.path.join(fileDir, 'media')
        self._history_file_path = os.path.join(fileDir, path)

    def start(self) -> None:
        if not os.path.isdir(self._media_path):
            os.makedirs(self._media_path)

        self._check_history_file()
        if self._current_game:
            self._deck = self._current_game['state']['deck']
        else:
            print('Не удалось получить колоду')
            exit()
        self._shuffle_cards()
        self._add_card('computer')
        self.notify(
            OBSERVER_MESSAGES['change_state'],
            self._current_game
        )

    def change_state(self, payload: ChangeStatePayload) -> None:
        if payload['action'] == 'Взять карту':
            self._add_card('human')
        self._add_card('computer')
        self.notify(OBSERVER_MESSAGES['change_state'], self._current_game)

    def _add_card(self, gamer_type: GamerType) -> None:
        card = self._deck.pop()
        self._current_game['state'][f'{gamer_type}_cards'].append(card)  # type: ignore

    def _shuffle_cards(self) -> None:
        for i in range(1, random.randint(10, 30)):
            random.shuffle(self._deck)

    def _check_history_file(self) -> None:
        if os.path.isfile(self._history_file_path):
            with open(self._history_file_path, 'r') as file:
                jsonData = StringIO(file.read())
                data = json.load(jsonData)
                self._current_game = data[len(data) - 1]
        else:
            current_game: Game = {
                'game_uuid': uuid4().hex,
                'events': [],
                'state': {
                    'computer_cards': [],
                    'human_cards': [],
                    'human_score': 0,
                    'computer_score': 0,
                    'deck': generate_deck()
                },
                'winner': None,
                'finished': False,
            }
            init_data = json.dumps([current_game])

            self._create_file(self._history_file_path, str(init_data))
            self._current_game = current_game

    def _create_file(self, path: str, data: str) -> None:
        with open(path, 'w') as file:
            file.write(data)
