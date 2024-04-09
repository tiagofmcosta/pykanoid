from enum import Enum, auto, verify, UNIQUE

from pykanoid.settings import TOTAL_LIVES


@verify(UNIQUE)
class State(Enum):
    IDLE = auto()
    START = auto()
    PLAYING = auto()
    LIFE_LOST = auto()
    LEVEL_CLEARED = auto()
    WAITING_BALL_RELEASE = auto()
    GAME_LOST = auto()
    GAME_WON = auto()
    NEXT_LEVEL = auto()


class InvalidTransitionError(Exception):
    def __init__(self, next_state: State, valid_transitions: set[State], *args):
        super().__init__(args)
        self.next_state = next_state
        self.valid_transitions = valid_transitions

    def __str__(self):
        return f"{self.next_state} is not a valid state in {self.valid_transitions}"


class StateMachine:
    __valid_transitions = {
        State.IDLE: {State.START},
        State.START: {State.WAITING_BALL_RELEASE},
        State.WAITING_BALL_RELEASE: {State.PLAYING},
        State.PLAYING: {State.LIFE_LOST, State.LEVEL_CLEARED},
        State.LIFE_LOST: {
            State.PLAYING,
            State.WAITING_BALL_RELEASE,
            State.GAME_LOST,
            State.GAME_WON,
        },
        State.LEVEL_CLEARED: {State.NEXT_LEVEL, State.GAME_WON},
        State.GAME_LOST: {State.IDLE},
        State.GAME_WON: {State.IDLE},
        State.NEXT_LEVEL: {State.WAITING_BALL_RELEASE},
    }

    def transition(self, current_state, next_state) -> State:
        valid_transitions = self.__valid_transitions[current_state]

        if next_state in valid_transitions:
            return next_state

        raise InvalidTransitionError(next_state, valid_transitions)


class Status:
    __STATE_MACHINE = StateMachine()

    def __init__(self):
        self.__score = 0
        self.__state = State.IDLE
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

        if next_state == State.LIFE_LOST:
            self.__lives -= 1
        elif next_state == State.START:
            self.__score = 0
            self.__lives = TOTAL_LIVES

    def update_score(self, score):
        self.__score += score
