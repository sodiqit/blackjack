from io import StringIO
import json
import os
from typing import Any, Literal, Optional, TypedDict, Union
from uuid import uuid4

from modules.utils.constants import Card, Deck, generate_deck

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

class Storage:
    def __init__(self) -> None:
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        path = 'media/history.json'
        self._media_path = os.path.join(fileDir, 'media')
        self._history_file_path = os.path.join(fileDir, path)

    def get_current_game(self) -> Game:
        if not os.path.isdir(self._media_path):
            os.makedirs(self._media_path)

        if os.path.isfile(self._history_file_path):
            last_game = self._get_last_game()
            current_game = last_game

            if last_game['finished']:
                current_game = self._create_new_game()
                self.add_game_in_history(current_game)

            return current_game
        else:
            current_game = self._create_new_game()
            init_data = json.dumps([current_game])

            self._create_file(self._history_file_path, str(init_data))
            return current_game

    def has_last_not_ended_game(self) -> bool:
        if not os.path.isdir(self._media_path):
            os.makedirs(self._media_path)

        if os.path.isfile(self._history_file_path):
            last_game = self._get_last_game()

            return last_game and not last_game['finished']
        else:
            return False

    def update_game_in_history(self, updated_game: Game) -> None:
        games = self._read_history_file()
        games[len(games) - 1] = updated_game

        data = json.dumps(games)

        self._create_file(self._history_file_path, str(data))

    def add_game_in_history(self, updated_game: Game) -> None:
        games = self._read_history_file()
        games.append(updated_game)

        data = json.dumps(games)

        self._create_file(self._history_file_path, str(data))

    def get_all_games(self) -> list[Game]:
        return self._read_history_file()

    def _get_last_game(self) -> Game:
        with open(self._history_file_path, 'r') as file:
            jsonData = StringIO(file.read())
            data = json.load(jsonData)
            last_game = data[len(data) - 1]

            return last_game

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
