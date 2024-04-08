from enum import Enum, auto, verify, UNIQUE

from pykanoid.settings import TOTAL_LIVES


@verify(UNIQUE)
class State(Enum):
    IDLE = auto()
    START = auto()
    PLAYING = auto()
    PAUSED = auto()
    LIFE_LOST = auto()
    GAME_LOST = auto()
    GAME_WON = auto()
    NEXT_LEVEL = auto()
    LEVEL_CLEARED = auto()
    RESET = auto()


class StateMachine:
    __valid_transitions = {
        State.START: {State.IDLE},
        State.IDLE: {State.PLAYING, State.PAUSED},
        State.PLAYING: {State.PAUSED, State.LIFE_LOST, State.LEVEL_CLEARED},
        State.PAUSED: {State.PLAYING},
        State.LIFE_LOST: {State.IDLE, State.GAME_LOST},
        State.GAME_LOST: {State.RESET},
        State.GAME_WON: {State.RESET},
        State.LEVEL_CLEARED: {State.NEXT_LEVEL, State.GAME_WON},
        State.RESET: {State.START},
    }

    def transition(self, current_state, next_state) -> State:
        if next_state in self.__valid_transitions[current_state]:
            return next_state

        return current_state


class Status:
    __STATE_MACHINE = StateMachine()

    def __init__(self):
        self.__score = 0
        self.__state = State.START
        self.__lives = TOTAL_LIVES

    @property
    def score(self):
        return self.__score

    @property
    def state(self):
        return self.__state

    @property
    def lives(self):
        return self.__lives

    def set_state(self, next_state: State):
        self.__state = self.__STATE_MACHINE.transition(self.__state, next_state)

        if next_state == State.RESET:
            self.__lives = TOTAL_LIVES
        elif next_state == State.LIFE_LOST:
            self.__lives -= 1
        elif next_state == State.START:
            self.__score = 0

    def update_score(self, score):
        self.__score += score
