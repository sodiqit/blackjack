import pytest
from uuid import uuid4

from pytest_mock import MockerFixture
from modules.model.model import Model
from modules.utils.constants import OBSERVER_MESSAGES, generate_deck
from modules.storage.storage import Balance, Game, Storage

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

class MockStorage:
    def __init__(self, mocker: MockerFixture, current_game: Game, balance: Balance):
        self.mocked_has_last_not_ended_game = mocker.patch.object(Storage, 'has_last_not_ended_game')
        self.mocked_get_current_game = mocker.patch.object(Storage, 'get_current_game')
        self.mocked_update_game_in_history = mocker.patch.object(Storage, 'update_game_in_history')
        self.mocked_get_current_game.return_value = current_game
        self.mocked_get_balance = mocker.patch.object(Storage, 'get_balance')
        self.mocked_get_balance.return_value = balance
        self.mocked_add_game_in_history = mocker.patch.object(Storage, 'add_game_in_history')
        self.mocked_remove_history_file = mocker.patch.object(Storage, 'remove_history_file')
        self.mocked_update_balance = mocker.patch.object(Storage, 'update_balance')
        self.mocked_get_all_games = mocker.patch.object(Storage, 'get_all_games')
        self.mocked_get_all_games.return_value = [current_game]


def test_start_if_previous_game_ended(mocker: MockerFixture, current_game: Game, balance: Balance) -> None:
    model = Model(Storage())
    stub = mocker.stub(name='test_sub')
    fake_storage = MockStorage(mocker, current_game, balance)
    model.subscribe(OBSERVER_MESSAGES['change_state'], stub);

    model.start({ 'bet': { 'value': '10', 'status': 'MADE', 'gamer_type': 'human' } })

    assert model._current_game == current_game
    stub.assert_called()
    fake_storage.mocked_has_last_not_ended_game.assert_called_once()
    fake_storage.mocked_get_current_game.assert_called_once()
    fake_storage.mocked_update_game_in_history.assert_not_called()
    assert model._balance == balance

def test_start_if_has_not_ended_game(mocker: MockerFixture, current_game: Game, balance: Balance) -> None:
    model = Model(Storage())
    stub = mocker.stub(name='test_sub')
    fake_storage = MockStorage(mocker, current_game, balance)
    model.subscribe(OBSERVER_MESSAGES['change_state'], stub);
    fake_storage.mocked_has_last_not_ended_game.return_value = False

    model.start({ 'bet': { 'value': '10', 'status': 'MADE', 'gamer_type': 'human' } })

    assert model._current_game == current_game
    stub.assert_called()
    fake_storage.mocked_has_last_not_ended_game.assert_called_once()
    fake_storage.mocked_get_current_game.assert_called_once()
    fake_storage.mocked_update_game_in_history.assert_called()
    assert model._balance == balance

def test_get_available_bets_with_balance(mocker: MockerFixture, current_game: Game, balance: Balance) -> None:
    model = Model(Storage())
    fake_storage = MockStorage(mocker, current_game, balance)

    result = model.get_available_bets_with_balance()

    assert result['available_bets'] == ['5', '25', '50']
    assert result['balance'] == balance

    zero_balance = { **balance, 'human': 0 } # type: ignore
    fake_storage.mocked_get_balance.return_value = zero_balance

    result1 = model.get_available_bets_with_balance()

    assert result1['available_bets'] == []
    assert result1['balance'] == zero_balance

    low_balance = { **balance, 'human': 5 } # type: ignore
    fake_storage.mocked_get_balance.return_value = low_balance

    result2 = model.get_available_bets_with_balance()

    assert result2['available_bets'] == ['5']
    assert result2['balance'] == low_balance

    fake_storage.mocked_get_balance.assert_called()

def test_change_state_if_game_not_finished_and_user_continue(mocker: MockerFixture, current_game: Game, balance: Balance) -> None:
    stub = mocker.stub('test_sub')
    model = Model(Storage())
    model.subscribe(OBSERVER_MESSAGES['change_state'], stub)
    fake_storage = MockStorage(mocker, current_game, balance)
    model.start({ 'bet': { 'value': '10', 'status': 'MADE', 'gamer_type': 'human' } })
    model._current_game['state']['human_cards'] = [{ 'suit': 'diamonds', 'type': '2' }, { 'suit': 'diamonds', 'type': '2' }]

    model.change_state({ 'action': 'Взять карту' })

    fake_storage.mocked_update_game_in_history.assert_called()
    stub.assert_called()
    assert len(model._current_game['state']['human_cards']) == 3
    assert model._current_game['state']['human_score'] > 4

def test_change_state_if_game_finished_and_user_continue(mocker: MockerFixture, current_game: Game, balance: Balance) -> None:
    stub = mocker.stub('test_sub')
    model = Model(Storage())
    model.subscribe(OBSERVER_MESSAGES['change_state'], stub)
    fake_storage = MockStorage(mocker, current_game, balance)
    model.start({ 'bet': { 'value': '10', 'status': 'MADE', 'gamer_type': 'human' } })
    model._current_game['state']['human_cards'] = [{ 'suit': 'diamonds', 'type': '10' }, { 'suit': 'diamonds', 'type': 'ace' }]

    model.change_state({ 'action': 'Взять карту' })

    assert model._current_game['finished'] == True
    fake_storage.mocked_update_game_in_history.assert_called()
    stub.assert_called()
    assert stub.call_count == 1
    assert len(model._current_game['state']['human_cards']) == 3
    assert model._current_game['state']['human_score'] > 4

def test_change_state_if_user_not_continue(mocker: MockerFixture, current_game: Game, balance: Balance) -> None:
    stub = mocker.stub('test_sub')
    finish_stub = mocker.stub('test_finish')
    model = Model(Storage())
    model.subscribe(OBSERVER_MESSAGES['change_state'], stub)
    model.subscribe(OBSERVER_MESSAGES['finish'], finish_stub)
    fake_storage = MockStorage(mocker, current_game, balance)
    fake_storage.mocked_has_last_not_ended_game.return_value = False
    model.start({ 'bet': { 'value': '10', 'status': 'MADE', 'gamer_type': 'human' } })

    model.change_state({ 'action': 'Пас' })

    assert model._current_game['finished'] == True
    fake_storage.mocked_update_game_in_history.assert_called()
    stub.assert_called()
    finish_stub.assert_called_once()
    assert stub.call_count == 1
    assert len(model._current_game['state']['human_cards']) == 2
    assert model._current_game['state']['human_score'] > 0

def test_reset_state(mocker: MockerFixture, current_game: Game, balance: Balance) -> None:
    stub = mocker.stub('test_sub')
    model = Model(Storage())
    fake_storage = MockStorage(mocker, current_game, balance)
    model.subscribe(OBSERVER_MESSAGES['change_state'], stub)
    
    model.reset_state({ 'bet': { 'value': '10', 'status': 'MADE', 'gamer_type': 'human' } })

    fake_storage.mocked_remove_history_file.assert_called_once()
    stub.assert_called_once()

def test_add_event(mocker: MockerFixture, current_game: Game, balance: Balance) -> None:
    model = Model(Storage())
    fake_storage = MockStorage(mocker, current_game, balance)
    
    model.start({ 'bet': { 'value': '10', 'status': 'MADE', 'gamer_type': 'human' } })

    # "MADE" bet

    model.add_event({ 'value': '10', 'status': 'MADE', 'gamer_type': 'human' })

    fake_storage.mocked_update_balance.assert_called_with({'computer': 500, 'freeze_human_balance': 10, 'human': 100})

    # "LOSE" bet

    fake_storage.mocked_get_balance.return_value = { **balance, 'freeze_human_balance': 10 }

    model.add_event({ 'value': '10', 'status': 'LOSE', 'gamer_type': 'human' })

    fake_storage.mocked_update_balance.assert_called_with({'computer': 510, 'freeze_human_balance': 0, 'human': 90})

    # "WIN" bet

    fake_storage.mocked_get_balance.return_value = { **balance, 'freeze_human_balance': 10 }

    model.add_event({ 'value': '10', 'status': 'WIN', 'gamer_type': 'human' })

    fake_storage.mocked_update_balance.assert_called_with({'computer': 490, 'freeze_human_balance': 0, 'human': 110})

    # "DRAW" bet

    fake_storage.mocked_get_balance.return_value = { **balance, 'freeze_human_balance': 10 }

    model.add_event({ 'value': '10', 'status': 'DRAW', 'gamer_type': 'human' })

    fake_storage.mocked_update_balance.assert_called_with({'computer': 500, 'freeze_human_balance': 0, 'human': 100})