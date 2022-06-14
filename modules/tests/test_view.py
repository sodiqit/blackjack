from uuid import uuid4
import inquirer
import pytest
from pytest_mock import MockerFixture
from modules.storage.storage import Balance, Game
from modules.utils.constants import OBSERVER_MESSAGES, generate_deck
from modules.view.view import View

@pytest.fixture
def current_game() -> Game:
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
    return current_game

@pytest.fixture
def balance() -> Balance:
    return {
        'human': 100, 
        'computer': 500, 
        'freeze_human_balance': 0,
    }

class MockStdout:
    def __init__(self, mocker: MockerFixture):
        self.mocked_create_prompt = mocker.patch.object(inquirer, 'prompt')


def test_start_game_if_has_balance(mocker: MockerFixture, balance: Balance) -> None: 
    stub = mocker.stub('test_stub')
    view = View()
    view.subscribe(OBSERVER_MESSAGES['init'], stub)
    MockStdout(mocker)

    view.start_game({ 'available_bets': ['5'], 'balance': balance })

    stub.assert_called_once()

def test_restart_game_if_balance_ended(mocker: MockerFixture, balance: Balance) -> None: 
    stub = mocker.stub('test_stub')
    view = View()
    view.subscribe(OBSERVER_MESSAGES['restart'], stub)
    MockStdout(mocker)

    view.start_game({ 'available_bets': ['5'], 'balance': { **balance, 'human': 0 } }) # type: ignore

    stub.assert_called_once()
    
def test_render(mocker: MockerFixture, current_game: Game) -> None:
    stub = mocker.stub('test_stub')
    view = View()
    view.subscribe(OBSERVER_MESSAGES['user_action'], stub)
    fake_stdout = MockStdout(mocker)
    fake_stdout.mocked_create_prompt.return_value = 'Взять карту'

    view.render(current_game)

    stub.assert_called_with('Взять карту')

    fake_stdout.mocked_create_prompt.return_value = 'Пас'

    view.render(current_game)

    stub.assert_called_with('Пас')

def test_render_finish_screen(mocker: MockerFixture, current_game: Game, balance: Balance) -> None:
    stub = mocker.stub('test_stub')
    view = View()
    view.subscribe(OBSERVER_MESSAGES['init'], stub)
    MockStdout(mocker)

    view.render_finish_screen({ 'game': current_game, 'statistics': { 'balance': balance, 'winrate': 0.25 }, 'available_bets': ['5', '25', '50'] })

    stub.assert_called_once()

def test_render_finish_screen_if_balance_ended(mocker: MockerFixture, current_game: Game, balance: Balance) -> None:
    stub = mocker.stub('test_stub')
    view = View()
    view.subscribe(OBSERVER_MESSAGES['restart'], stub)
    MockStdout(mocker)

    view.render_finish_screen({ 'game': current_game, 'statistics': { 'balance': { **balance, 'human': 0 }, 'winrate': 0.25 }, 'available_bets': ['5', '25', '50'] }) # type: ignore

    stub.assert_called_once()
