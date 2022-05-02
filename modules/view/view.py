from typing import Optional
import inquirer
from modules.model.model import Game, GamerType
from modules.observer.observer import Observer
from modules.utils.constants import CARDS, OBSERVER_MESSAGES, SUITS, Card


def get_winner(gamer_type: Optional[GamerType]) -> str:
    if gamer_type == 'human':
        return 'Вы'
    elif gamer_type == 'computer':
        return 'Компьютер'
    return 'Ничья'

class View(Observer):
    def start_game(self) -> None:
        answer = self._create_prompt(
            'continue',
            message='Приветствую! Готов сыграть в Blackjack?',
            choices=['Да', 'Нет']
        )
        if answer['continue'] == 'Нет':
            exit()
        self.notify(OBSERVER_MESSAGES['init'])

    def render(self, game: Game) -> None:
        print(self._get_game_info_message(game))

        answer = self._create_prompt(
            'action',
            message='Ваше действие',
            choices=['Взять карту', 'Пас']
        )

        self.notify(OBSERVER_MESSAGES['user_action'], answer)

    def render_finish_screen(self, game: Game) -> None:
        print(
            f"\nИгра окончена! Победитель: {get_winner(game['winner'])}",
            f"\nВаше количество очков: {game['state']['human_score']} | Количество очков компьютера: {game['state']['computer_score']}"
        )
        answer = self._create_prompt(
            'continue',
            message='Хотите сыграть еще раз?',
            choices=['Да', 'Нет']
        )

        if answer['continue'] == 'Нет':
            exit()
        self.notify(OBSERVER_MESSAGES['init'])
            

    def _get_game_info_message(self, game: Game) -> str:
        user_cards = game['state']['human_cards']
        return f"\nКоличество карт у компьютера: {len(game['state']['computer_cards'])}" + " | " + f"Ваше количество очков: {game['state']['human_score']}" + " | " + f"Ваши карты: {', '.join([self.get_card_info(card) for card in user_cards])}"

    def get_card_info(self, card: Card) -> str:
        return f"'{CARDS[card['type']]} {SUITS[card['suit']]}'"

    def _create_prompt(self, key: str, message: str = '', choices: list = []) -> dict:
        questions = [inquirer.List(key, message=message, choices=choices)]
        answer = inquirer.prompt(questions)
        return answer
