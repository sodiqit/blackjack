from typing import Literal, Optional, Union
from typing_extensions import TypedDict
import inquirer
from modules.model.model import BET_STATUS, AvailableBetsWithBalance, Game, GamerType
from modules.observer.observer import Observer
from modules.storage.storage import Balance
from modules.utils.constants import CARDS, OBSERVER_MESSAGES, SUITS, Card


def get_winner(gamer_type: Optional[GamerType]) -> str:
    if gamer_type == 'human':
        return 'Вы'
    elif gamer_type == 'computer':
        return 'Компьютер'
    return 'Ничья'


Statistics = TypedDict('Statistics', {
    'winrate': float,
    'balance': Balance
})

FinishScreenPayload = TypedDict('FinishScreenPayload', {
    'game': Game,
    'statistics': Statistics,
    'available_bets': list[str]
})


class View(Observer):
    def start_game(self, payload: AvailableBetsWithBalance) -> None:
        self._continue_prompt('Приветствую! Готов сыграть в Blackjack?')
        self._check_user_balance(payload)
        
    def render(self, game: Game) -> None:
        print(self._get_game_info_message(game))

        answer = self._create_prompt(
            'action',
            message='Ваше действие',
            choices=['Взять карту', 'Пас']
        )

        self.notify(OBSERVER_MESSAGES['user_action'], answer)

    def render_finish_screen(self, payload: FinishScreenPayload) -> None:
        game = payload['game']
        statistics = payload['statistics']

        print(
            f"\nИгра окончена! Победитель: {get_winner(game['winner'])}",
            f"\nВаше количество очков: {game['state']['human_score']} | Количество очков компьютера: {game['state']['computer_score']}"
        )

        print(
            f"Winrate: {float('{:.2f}'.format(statistics['winrate'] * 100))}%",
            f"\nВаш баланс: {payload['statistics']['balance']['human']}$", 
            f"\nБаланс компьютера: {payload['statistics']['balance']['computer']}$"
        )

        self._continue_prompt('Хотите сыграть еще раз?')

        self._check_user_balance({ 
            'available_bets': payload['available_bets'], 
            'balance': payload['statistics']['balance'] 
        })

    def _check_user_balance(self, payload: AvailableBetsWithBalance) -> None:
        notify_type: Union[Literal['init'], Literal['restart']] = 'init'

        if payload['balance']['computer'] == 0:
            self._continue_prompt('Поздравляю! Ты обыграл казино! Хочешь сбросить весь прогресс и попробовать сначала?')
            notify_type = 'restart'

        if payload['balance']['human'] == 0:
            self._continue_prompt('Упс! Ты проиграл все деньги! Хочешь сбросить весь прогресс и попробовать сначала?')
            notify_type = 'restart'

        self._bet_prompt(payload['available_bets'] if notify_type == 'init' else ['5', '25', '50'], notify_type)

    def _get_game_info_message(self, game: Game) -> str:
        user_cards = game['state']['human_cards']
        return f"\nКоличество карт у компьютера: {len(game['state']['computer_cards'])}" + " | " + f"Ваше количество очков: {game['state']['human_score']}" + " | " + f"Ваши карты: {', '.join([self._get_card_info(card) for card in user_cards])}"

    def _get_card_info(self, card: Card) -> str:
        return f"'{CARDS[card['type']]} {SUITS[card['suit']]}'"

    def _continue_prompt(self, text: str) -> None:
        answer = self._create_prompt(
            'continue',
            message=text,
            choices=['Да', 'Нет']
        )

        if answer['continue'] == 'Нет':
            exit()

    def _bet_prompt(self, available_bets: list[str], notify_type: Union[Literal['init'], Literal['restart']] = 'init') -> None:
        bet_answer = self._create_prompt(
            'bet',
            message='Какой будет размер ставки?',
            choices=available_bets
        )
        self.notify(OBSERVER_MESSAGES[notify_type], {'bet': {
            'value': bet_answer['bet'],
            'status': BET_STATUS['made'],
            'gamer_type': 'human'
        }})

    def _create_prompt(self, key: str, message: str = '', choices: list = []) -> dict:
        questions = [inquirer.List(key, message=message, choices=choices)]
        answer = inquirer.prompt(questions)
        return answer
