import enum


class NodeType(enum.Enum):
    PRE_STATE = 'pre_state'
    STATE = 'state'
    PROTO = 'proto'
    REMOVED = 'removed'
    FUTURE = 'future'


class Connective(enum.Enum):
    OPEN = '('
    CLOSE = ')'
    NOT = '!'
    GLOBALLY = 'G'
    NEXT = 'X'
    FINALLY = 'F'
    AND = 'A'
    OR = 'O'
    IMPLIES = '>'
    UNTIL = 'U'


class TruthValue(enum.Enum):
    TRUE = '1'
    FALSE = '0'


class BetaOrder(enum.IntEnum):
    NONE = 0
    FIRST = 1
    SECOND = 2


class TableauType(enum.Enum):
    BFS = 'bfs'
    DFS = 'dfs'


UNARY_CONNECTIVES = [Connective.NOT.value, Connective.GLOBALLY.value, Connective.NEXT.value, Connective.FINALLY.value]
BINARY_CONNECTIVES = [Connective.AND.value, Connective.OR.value, Connective.IMPLIES.value, Connective.UNTIL.value]
