from common import Connective, TruthValue, UNARY_CONNECTIVES, BINARY_CONNECTIVES


class Formula:
    def __init__(self, formula_string):
        self.formula_string = formula_string
        self.marked = False

    def __repr__(self):
        return 'string: {}, marked: {}'.format(self.formula_string, self.marked)

    def __hash__(self):
        return hash(self.formula_string)

    def __eq__(self, other):
        return self.formula_string == other.formula_string

    def __le__(self, other):
        return len(self.formula_string) <= len(other.formula_string)

    def __ge__(self, other):
        return len(self.formula_string) >= len(other.formula_string)

    def __lt__(self, other):
        return len(self.formula_string) < len(other.formula_string)

    def __gt__(self, other):
        return len(self.formula_string) > len(other.formula_string)

    @staticmethod
    def _build_formula(formula):
        return '{}{}{}'.format(Connective.OPEN.value, formula, Connective.CLOSE.value)

    def find_next_symbol(self, sub_formula_string):
        symbol = sub_formula_string[0]
        if symbol == Connective.OPEN.value:
            left_parenthesis = 1
            right_parenthesis = 0

            index = 1
            while left_parenthesis > right_parenthesis:
                if sub_formula_string[index] == Connective.OPEN.value:
                    left_parenthesis += 1
                elif sub_formula_string[index] == Connective.CLOSE.value:
                    right_parenthesis += 1
                index += 1

            assert sub_formula_string[index] in BINARY_CONNECTIVES
            return sub_formula_string[index], index

        elif symbol in UNARY_CONNECTIVES:
            return sub_formula_string[0], 0

        else:

            assert self.is_elementary(sub_formula_string) or sub_formula_string == '1' or sub_formula_string == '0', \
                sub_formula_string
            return None, 0

    def mark(self):
        assert not self.marked, 'formula is already marked'
        self.marked = True

    def is_alpha(self):
        symbol, index = self.find_next_symbol(self.formula_string)

        if symbol == Connective.AND.value:
            return True, (self.formula_string[1:index - 1], self.formula_string[index + 2:-1])

        if symbol == Connective.GLOBALLY.value:
            return True, (self.formula_string[2:-1], Connective.NEXT.value +
                          self._build_formula(self.formula_string))

        if symbol == Connective.NOT.value:
            second_symbol, second_index = self.find_next_symbol(self.formula_string[2:-1])
            second_index += 2

            if second_symbol == Connective.NOT.value:
                sub_formula = self.formula_string[4:-2]
                return True, (sub_formula, sub_formula)

            if second_symbol == Connective.OR.value:
                return True, (Connective.NOT.value + self._build_formula(self.formula_string[3:second_index-1]),
                              Connective.NOT.value + self._build_formula(self.formula_string[second_index+2:-2]))

            if second_symbol == Connective.IMPLIES.value:
                return True, (self.formula_string[3:second_index-1],
                              Connective.NOT.value + self._build_formula(self.formula_string[second_index+2:-2]))

            if second_symbol == Connective.NEXT.value:
                sub_formula = Connective.NOT.value + self._build_formula(self.formula_string[4:-2])
                sub_formula = Connective.NEXT.value + self._build_formula(sub_formula)
                return True, (sub_formula, sub_formula)

            if second_symbol == Connective.FINALLY.value:
                sub_formula = Connective.NEXT.value + self._build_formula(self.formula_string[2:-1])
                sub_formula = Connective.NOT.value + self._build_formula(sub_formula)

                return True, (Connective.NOT.value + self._build_formula(self.formula_string[4:-2]), sub_formula)

        return False, (None, None)

    def is_beta(self):
        symbol, index = self.find_next_symbol(self.formula_string)

        if symbol == Connective.OR.value:
            return True, (self.formula_string[1:index - 1], self.formula_string[index + 2:-1])

        if symbol == Connective.IMPLIES.value:
            return True, (Connective.NOT.value + self._build_formula(self.formula_string[1:index-1]),
                          self.formula_string[index + 2:-1])

        if symbol == Connective.UNTIL.value:
            sub1 = Connective.NEXT.value + self._build_formula(self.formula_string)
            sub1 = self._build_formula(sub1)
            sub2 = self._build_formula(self.formula_string[1:index - 1])
            return True, (self.formula_string[index + 2:-1], sub2 + Connective.AND.value + sub1)

        if symbol == Connective.FINALLY.value:
            return True, (self.formula_string[2:-1],
                          Connective.NEXT.value + self._build_formula(self.formula_string))

        if symbol == Connective.NOT.value:
            second_symbol, second_index = self.find_next_symbol(self.formula_string[2:-1])
            second_index += 2

            if second_symbol == Connective.AND.value:
                return True, (Connective.NOT.value + self._build_formula(self.formula_string[3:second_index-1]),
                              Connective.NOT.value + self._build_formula(self.formula_string[second_index+2:-2]))

            if second_symbol == Connective.UNTIL.value:
                sub1 = Connective.NOT.value + self._build_formula(self.formula_string[3:second_index-1])
                sub2 = Connective.NOT.value + self._build_formula(self.formula_string[second_index+2:-2])
                formula1 = self._build_formula(sub1) + Connective.AND.value + self._build_formula(sub2)

                sub3 = Connective.NEXT.value + self._build_formula(self.formula_string[2:-1])
                sub3 = Connective.NOT.value + self._build_formula(sub3)
                formula2 = self._build_formula(sub2) + Connective.AND.value + self._build_formula(sub3)
                return True, (formula1, formula2)

            if second_symbol == Connective.GLOBALLY.value:
                sub1 = Connective.NEXT.value + self._build_formula(self.formula_string[second_index:-1])

                return True, (Connective.NOT.value + self._build_formula(self.formula_string[4:-2]),
                              Connective.NOT.value + self._build_formula(sub1))

            return False, (None, None)

    def is_true(self, sub_formula=None):
        formula_string = sub_formula or self.formula_string
        return formula_string == TruthValue.TRUE.value

    def is_next(self, sub_formula=None):
        formula_string = sub_formula or self.formula_string
        return formula_string[0] == Connective.NEXT.value

    def is_elementary(self, sub_formula=None):
        formula_string = sub_formula or self.formula_string
        is_atomic = len(formula_string) == 4 and formula_string.islower()
        is_atomic_negation = (len(formula_string) == 7 and formula_string[2].islower() and
                              formula_string[0] == Connective.NOT.value)
        is_next = self.is_next(formula_string)

        return is_atomic or is_atomic_negation or is_next

    def is_eventuality(self):
        symbol, index = self.find_next_symbol(self.formula_string)
        if symbol == Connective.FINALLY.value or symbol == Connective.UNTIL.value:
            return True
        if symbol == Connective.NOT.value:
            second_symbol, second_index = self.find_next_symbol(self.formula_string[2:-1])
            if second_symbol == Connective.GLOBALLY.value:
                return True
        return False
