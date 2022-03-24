from typing import Literal, Union, TypedDict


ObserverMessages = TypedDict(
    'ObserverMessages',
    {
        'init': Literal['INIT'],
        'update_state': Literal['UPDATE_STATE']
    }
)
SubscribesType = Union[Literal['UPDATE_STATE'], Literal['INIT']]

OBSERVER_MESSAGES: ObserverMessages = {
    'init': 'INIT',
    'update_state': 'UPDATE_STATE'
}
