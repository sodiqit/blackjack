import random
from typing import Literal, Union, Optional, TypedDict

from modules.observer.observer import Observer
from modules.storage.storage import Balance, Game, GamerType, Storage
from modules.utils.constants import MAP_CARDS_FOR_SCORE, OBSERVER_MESSAGES, Card, Deck

ChangeStatePayload = TypedDict(
    'ChangeStatePayload',
    {
        'action': Literal['Взять карту'] | Literal['Пас']
    }
)

BetStatus = Union[Literal['MADE'], Literal['LOSE'], Literal['WIN'], Literal['DRAW']] 

BET_STATUS: dict[str, BetStatus] = {
    'made': 'MADE',
    'lose': 'LOSE',
    'win': 'WIN',
    'draw': 'DRAW',
}


BetPayload = TypedDict(
    'BetPayload',
    {
        'value': str, 
        'status': BetStatus, 
        'gamer_type': GamerType
    }
)

InitBetPayload = TypedDict('InitBetPayload', { 'bet': BetPayload })

AvailableBetsWithBalance = TypedDict('AvailableBetsWithBalance', { 'available_bets': list[str], 'balance': Balance })

class Model(Observer):
    _storage: Storage
    _current_game: Game
    _balance: Balance
    _deck: Deck = []

    def __init__(self, storage: Storage) -> None:
        super().__init__()
        self._storage = storage


    def start(self, payload: InitBetPayload) -> None:
        has_last_not_ended_game = self._storage.has_last_not_ended_game()

        self._current_game = self._storage.get_current_game()
        self._deck = self._current_game['state']['deck']
        self._balance = self._storage.get_balance()

        if not has_last_not_ended_game:
            self._shuffle_cards()
            self.add_event(payload['bet'])
            self._add_card('computer', 2)
            self._add_card('human', 2)
            self._storage.update_game_in_history(self._current_game)

        self.notify(
            OBSERVER_MESSAGES['change_state'],
            self._current_game
        )

    def get_available_bets_with_balance(self) -> AvailableBetsWithBalance:
        balance = None
        try:
            balance = self._storage.get_balance()
        except:
            balance = self._storage.get_default_balance()
        default_bets = ['5', '25', '50']
        available_bets = []

        for bet in default_bets:
            if int(bet) <= balance['human'] - balance['freeze_human_balance']:
                available_bets.append(bet)

        return { 'available_bets': available_bets, 'balance': balance } 

    def change_state(self, payload: ChangeStatePayload) -> None:
        self._computer_move()
        if payload['action'] == 'Взять карту':
            self._add_card('human', 1)

        self._storage.update_game_in_history(self._current_game)

        if self._is_finished() or payload['action'] == 'Пас':
            self._finish_game()
        else:
            self.notify(OBSERVER_MESSAGES['change_state'], self._current_game)

    def reset_state(self, payload: InitBetPayload) -> None:
        self._storage.remove_history_file()
        self.start(payload)

    def add_event(self, payload: BetPayload) -> None:
        balance = self._storage.get_balance()
        bet = int(payload['value']) # type: ignore
        self._current_game['events'].append({ 'gamer': payload['gamer_type'], 'value': bet, 'status': payload['status'] })
        self._storage.update_game_in_history(self._current_game)

        if payload['status'] == BET_STATUS['made']:
            self._storage.update_balance({ 'human': balance['human'], 'computer': balance['computer'], 'freeze_human_balance': balance['freeze_human_balance'] + bet })

        if payload['status'] == BET_STATUS['lose']:
            self._storage.update_balance({ 'human': balance['human'] - bet, 'computer': balance['computer'] + bet, 'freeze_human_balance': balance['freeze_human_balance'] - bet })

        if payload['status'] == BET_STATUS['win']:
            self._storage.update_balance({ 'human': balance['human'] + bet, 'computer': balance['computer'] - bet, 'freeze_human_balance': balance['freeze_human_balance'] - bet })

        if payload['status'] == BET_STATUS['draw']:
            self._storage.update_balance({ 'human': balance['human'], 'computer': balance['computer'], 'freeze_human_balance': balance['freeze_human_balance'] - bet })

    def _finish_game(self) -> None:
        finished_game: Game = {
            **self._current_game,  # type: ignore
            'finished': True,
            'winner': self._get_winner()
        }

        balance = self._storage.get_balance()

        if self._get_winner() is None:
            self.add_event({ 'gamer_type': 'human', 'value': str(balance['freeze_human_balance']), 'status': BET_STATUS['draw'] })
        else:
            self.add_event({ 'gamer_type': 'human', 'value': str(balance['freeze_human_balance']), 'status': BET_STATUS['win'] if self._get_winner() == 'human' else BET_STATUS['lose'] })

        self._current_game = finished_game
        self._storage.update_game_in_history(finished_game)
        self.notify(
            OBSERVER_MESSAGES['finish'], 
            {
                'game': self._current_game, 
                'statistics': {
                    'winrate': self._calculate_statistics(),
                    'balance': self._storage.get_balance()
                },
                'available_bets': self.get_available_bets_with_balance()['available_bets']
            })

    def _calculate_statistics(self) -> float:
        games = self._storage.get_all_games()
        winGames = list(filter(lambda item: item['winner'] == 'human', games))
        winrate = len(winGames) / len(games)
        return winrate

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

        return user_score >= 21

    def _computer_move(self) -> None:
        score = self._current_game['state']['computer_score']

        if score < 17:
            self._add_card('computer', 1)

    def _calculate_score(self, gamer_type: GamerType) -> None:
        cards: List[Card] = self._current_game['state'][f'{gamer_type}_cards'] # type: ignore
        result = 0
        for card in cards:
            result += MAP_CARDS_FOR_SCORE[card['type']]
        self._current_game['state'][f'{gamer_type}_score'] = result # type: ignore

    def _add_card(self, gamer_type: GamerType, count: int) -> None:
        for _ in range(count):
            card = self._deck.pop()
            self._current_game['state'][f'{gamer_type}_cards'].append(card)  # type: ignore
            self._calculate_score(gamer_type)

    def _shuffle_cards(self) -> None:
        for _ in range(1, random.randint(10, 30)):
            random.shuffle(self._deck)
