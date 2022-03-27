from uuid import uuid4
import json
import os
from io import StringIO

from modules.observer.observer import Observer
from modules.utils.constants import generate_deck, Deck


class Model(Observer):
    _history_file_path = ''
    _media_path = ''
    _current_game = None
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

        self._deck = generate_deck()

    def _check_history_file(self) -> None:
        if os.path.isfile(self._history_file_path):
            with open(self._history_file_path, 'r') as file:
                jsonData = StringIO(file.read())
                data = json.load(jsonData)
                self._current_game = data[len(data) - 1]
        else:
            current_game = {
                'game_uuid': uuid4().hex,
                'events': [],
                'finished': False
            }
            init_data = json.dumps([current_game])

            self._create_file(self._history_file_path, str(init_data))
            self._current_game = current_game

    def _create_file(self, path: str, data: str) -> None:
        with open(path, 'w') as file:
            file.write(data)
