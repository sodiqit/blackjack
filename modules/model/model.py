import random
import json
import os
from typing import Any, Literal, Union, Optional, TypedDict
from uuid import uuid4
from io import StringIO

from modules.observer.observer import Observer
from modules.utils.constants import MAP_CARDS_FOR_SCORE, OBSERVER_MESSAGES, Card, generate_deck, Deck

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
'''


class Model(Observer):
    _history_file_path = ''
    _media_path = ''
    _current_game: Game
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
        self._computer_move()
        self._calculate_score('human')

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
        self._update_history(finished_game)
        self.notify(OBSERVER_MESSAGES['finish'], self._current_game)

    def _update_history(self, updated_game: Game) -> None:
        games = self._read_history_file()
        games.append(updated_game)

        data = json.dumps(games)

        self._create_file(self._history_file_path, str(data))

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

    def _check_history_file(self) -> None:
        if os.path.isfile(self._history_file_path):
            with open(self._history_file_path, 'r') as file:
                jsonData = StringIO(file.read())
                data = json.load(jsonData)
                last_game = data[len(data) - 1]

                if last_game['finished']:
                    self._current_game = self._create_new_game()
                else:
                    self._current_game = last_game
        else:
            current_game = self._create_new_game()
            init_data = json.dumps([current_game])

            self._create_file(self._history_file_path, str(init_data))
            self._current_game = current_game

    def _create_new_game(self) -> Game:
        return {
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

    def _read_history_file(self) -> Any:
        with open(self._history_file_path, 'r') as file:
            jsonData = StringIO(file.read())
            data = json.load(jsonData)
            return data

    def _create_file(self, path: str, data: str) -> None:
        with open(path, 'w') as file:
            file.write(data)
