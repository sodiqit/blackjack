from typing import Callable, Optional, TypeVar, TypedDict, List
from modules.utils.constants import OBSERVER_MESSAGES, SubscribesType

SubscriberFunction = Callable[..., None]
Subscriber = TypedDict(
    'Subscriber',
    {
        'type': SubscribesType,
        'subscribers': List[SubscriberFunction]
    }
)
T = TypeVar('T')


def get_subscribers_by_type(subscription_type: SubscribesType) -> Callable[[Subscriber], bool]:
    def filter_fn(item: Subscriber) -> bool:
        return item['type'] == subscription_type

    return filter_fn


class Observer:
    _observers: List[Subscriber] = []

    def subscribe(self, subscription_type: SubscribesType, fn: SubscriberFunction) -> None:
        observers = self._find_subs(subscription_type)

        if len(observers) == 0:
            item: Subscriber = {'type': subscription_type, 'subscribers': [fn]}
            self._observers.append(item)
        else:
            subject = observers[0]
            subscribers = subject['subscribers']
            subscribers.append(fn)

    def unsubscribe(self, subscription_type: SubscribesType, fn: SubscriberFunction) -> None:
        observers = self._find_subs(subscription_type)
        if len(observers) > 0:
            subject = observers[0]
            subscribers = subject['subscribers']
            subscribers.remove(fn)

    def notify(self, subscription_type: SubscribesType, data: Optional[T] = None) -> None:
        observers = self._find_subs(subscription_type)

        if len(observers) > 0:
            subject = observers[0]
            subscribers = subject['subscribers']

            for subscriber in subscribers:
                if data is None:
                    subscriber()
                else:
                    subscriber(data)

    def _find_subs(self, subscription_type: SubscribesType) -> list[Subscriber]:
        subs_types = list(OBSERVER_MESSAGES.values())

        if subscription_type in subs_types:
            matches = filter(get_subscribers_by_type(
                subscription_type), self._observers)
            return list(matches)
        else:
            raise Exception(
                f'Not valid subscription_type\n Correct types: {subs_types}\n Incoming type: {subscription_type}'
            )
