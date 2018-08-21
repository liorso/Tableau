import copy
import math
from common import NodeType, Connective
from formula import Formula


class Node:
    id = 0

    def __init__(self, tableau, parents, children, node_type, initial, formulas, rank, min_child_rank):
        Node.id += 1
        self.id = Node.id
        self.tableau = tableau
        self.parents = parents if type(parents) == set else {parents}
        self.children = children if type(children) == set else {children}
        self.node_type = node_type
        self.initial = initial
        self.formulas = set(copy.deepcopy(formulas))
        self.rank = rank
        self.min_child_rank = min_child_rank
        self.cloned = False
        self.find_succesor_visited = False


        tableau.insert(self)

    def __repr__(self):
        return f'id: {self.id}, parents: {[node.id for node in self.parents]}, ' \
               f'children: {[node.id for node in self.children]}, node_type: {self.node_type} ' \
               f'initial: {self.initial}, formulas: {self.formulas}, rank: {self.rank}, ' \
               f'min_child_rank: {self.min_child_rank}, cloned: {self.cloned}'

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(id(self))

    def handle_alpha(self, formulas):
        new_formulas = set(self.formulas)
        new_formulas.update(formulas)

        node1 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.PRE_STATE,
                     initial=False, formulas=new_formulas, rank=math.inf, min_child_rank=math.inf)

        self.children.add(node1)

    def handle_beta(self, formulas):
        new_formulas = set(self.formulas)
        new_formulas.update({formulas.pop()})

        node1 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.PRE_STATE,
                     initial=False, formulas=new_formulas, rank=math.inf, min_child_rank=math.inf)

        new_formulas = set(self.formulas)
        new_formulas.update(formulas)
        node2 = Node(tableau=self.tableau, parents=self, children=set(), node_type=NodeType.PRE_STATE,
                     initial=False, formulas=new_formulas, rank=math.inf, min_child_rank=math.inf)

        self.children.add(node1)
        self.children.add(node2)

    def is_consistent(self):
        for formula in self.formulas:
            if formula.formula_string[0] == Connective.NOT.value:
                for second_formula in self.formulas:
                    if formula.formula_string[2:-1] == second_formula.formula_string:
                        return False
        return True

    def get_next_formulas(self):
        return {Formula(formula.formula_string[2:-1]) for formula in self.formulas if formula.is_next()}

    def remove(self):
        for parent in self.parents:
            parent.children.remove(self)
            parent.children.update(self.children)

        for child in self.children:
            child.parents.remove(self)
            child.parents.update(self.parents)

    def clear_find_succesor_visited_flag(self, successors):
        self.find_succesor_visited = False
        for successor in successors:
            successor.find_succesor_visited = False

    def find_all_successors(self):
        successors = self.find_all_successors_rec()
        self.clear_find_succesor_visited_flag(successors)
        return successors

    def find_all_successors_rec(self):
        if self.find_succesor_visited:
            return set()
        self.find_succesor_visited = True
        successors = set(self.children)
        for child in self.children:
            successors.update(child.find_all_successors_rec())
        return successors

    def simple_remove(self):
        for parent in self.parents:
            parent.children.remove(self)
        for child in self.children:
            child.parents.remove(self)
        self.node_type = NodeType.REMOVED

    def find_eventualities(self):
        eventualities = set([formula for formula in self.formulas if formula.is_eventuality()])
        return eventualities

    def fulfilled_finally(self, check_formula):
        successors = self.find_all_successors()
        successors.add(self)
        for successor in successors:
            for formula in successor.formulas:
                if check_formula == formula.formula_string:
                    return True
        return False

    def fulfilled_until(self, first_formula, second_formula):
        successors = self.find_all_successors()
        ans = self.fulfilled_until_rec(first_formula, second_formula)
        self.clear_find_succesor_visited_flag(successors)
        return ans

    def fulfilled_until_rec(self, first_formula, second_formula):
        if self.find_succesor_visited:
            return False
        self.find_succesor_visited = True
        first_formula_exists = False
        for formula in self.formulas:
            if second_formula == formula.formula_string:
                return True
            if first_formula == formula.formula_string:
                first_formula_exists = True
        if not first_formula_exists:
            return False
        for child in self.children:
            if child.fulfilled_until_rec(first_formula, second_formula):
                return True
        return False

    def fulfilled_not_globally(self, check_formula):
        successors = self.find_all_successors()
        successors.add(self)
        for successor in successors:
            fulfilled = False
            for formula in successor.formulas:
                if check_formula == formula:
                    fulfilled = True
                    break
            if not fulfilled:
                return True
        return False

    def has_unfulfilled_eventuality(self):
        eventualities = self.find_eventualities()
        for eventuality in eventualities:
            symbol, index = eventuality.find_next_symbol(eventuality.formula_string)
            if symbol == Connective.FINALLY.value and not self.fulfilled_finally(eventuality.formula_string[2:-1]):
                return True
            if symbol == Connective.UNTIL.value and not self.fulfilled_until(eventuality.formula_string[1:index - 1],\
                                                                             eventuality.formula_string[index + 2:-1]):
                return True
            if not self.fulfilled_not_globally(eventuality.formula_string[4:-2]):
                return True
        return False
