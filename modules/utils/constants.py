from typing import Literal, Union, TypedDict


ObserverMessages = TypedDict(
    'ObserverMessages',
    {
        'init': Literal['INIT'],
        'deck_init': Literal['DECK_INIT']
    }
)
SubscribesType = Union[Literal['DECK_INIT'], Literal['INIT']]

CardTypes = Union[
    Literal['ace'],
    Literal['king'],
    Literal['queen'],
    Literal['jack'],
    Literal['10'],
    Literal['9'],
    Literal['8'],
    Literal['7'],
    Literal['6'],
    Literal['5'],
    Literal['4'],
    Literal['3'],
    Literal['2']
]

SuitTypes = Union[Literal['diamonds'], Literal['hearts'], Literal['spades'], Literal['clubs']]

Card = TypedDict(
    'Card',
    {
        'suit': SuitTypes,
        'type': CardTypes
    }
)

Deck = list[Card]

OBSERVER_MESSAGES: ObserverMessages = {
    'init': 'INIT',
    'deck_init': 'DECK_INIT'
}

CARDS: dict[CardTypes, str] = {
    'ace': 'Туз',
    'king': 'Король',
    'queen': 'Дама',
    'jack': 'Валет',
    '10': 'Десятка',
    '9': 'Девятка',
    '8': 'Восьмерка',
    '7': 'Семерка',
    '6': 'Шестерка',
    '5': 'Пятерка',
    '4': 'Четверка',
    '3': 'Тройка',
    '2': 'Двойка',
}

SUITS: dict[SuitTypes, str] = {
    'diamonds': 'Бубны',
    'hearts': 'Черви',
    'spades': 'Пики',
    'clubs': 'Трефы'
}


def generate_deck() -> Deck:
    suits = list(SUITS.keys())
    cards = list(CARDS.keys())
    result: Deck = []

    for suit in suits:
        for card in cards:
            deck_card: Card = {'suit': suit, 'type': card}
            result.append(deck_card)

    return result
