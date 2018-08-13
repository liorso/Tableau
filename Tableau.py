import enum
import math
import copy

# TODO ranks and initial in node creations

class NodeType(enum.Enum):
    PRE_STATE = 'pre_state'
    STATE = 'state'
    PROTO = 'proto'


class Formula:
    def __init__(self, formula_string):
        self.formula_string = formula_string
        self.marked = False

    def mark(self):
        assert not self.marked, 'formula is already marked'
        self.marked = True

    def split_alpha(self):
        pass

    def is_alpha(self):
        pass

    def split_beta(self):
        pass

    def is_beta(self):
        pass

    def is_true(self):
        return self.formula_string == 'T'

    def is_elementary:
        pass


class Node:
    id = 0

    def __init__(self, tableau, parents, children, node_type, initial, formulas, rank, min_child_rank):
        Node.id += 1
        self.id = Node.id
        self.tableau = tableau
        self.parents = parents if type(parents) == list else [parents]
        self.children = children if type(children) == list else[children]
        self.node_type = node_type
        self.initial = initial
        self.formulas = copy.deepcopy(formulas)
        self.rank = rank
        self.min_child_rank = min_child_rank
        self.cloned = False

        tableau.insert(self)

    def _repr__(self):
        return f'id: {self.id}, parents: {self.parents}, children: {self.children}, node_type: {self.node_type}' \
               f'initial: {self.initial}, formulas: {self.formulas}, rank: {self.rank}, ' \
               f'min_child_rank: {self.min_child_rank}'

    def __eq__(self, other):
        return self.id == other.id

    def handle_alpha(self, formula):
        a1, a2 = formula.split_alpha()

        node1 = Node(tableau=self.tableau, parents=self, children=[], node_type=NodeType.PRE_STATE,
                     initial=node.initial, formulas=self.formulas + [a1] + [a2],
                     rank=math.inf, min_child_rank=math.inf)

        self.children.append(node1)

    def handle_beta(self):
        b1, b2 = formula.split_beta()

        node1 = Node(tableau=self.tableau, parents=self, children=[], node_type=NodeType.PRE_STATE,
                     initial=node.initial, formulas=self.formulas + [b1],
                     rank=math.inf, min_child_rank=math.inf)

        node2 = Node(tableau=self.tableau, parents=self, children=[], node_type=NodeType.PRE_STATE,
                     initial=node.initial, formulas=self.formulas + [b2],
                     rank=math.inf, min_child_rank=math.inf)

        self.children.append(node1)
        self.children.append(node2)


class Tableau:

    def __init__(self):
        self.root_nodes = {}
        self.pre_states = {}
        self.proto_states = {}
        self.states = {}

        # TODO  - do we need?
        self.state_to_pre = []
        self.pre_to_state = []

    def insert(self, node):
        if node.node_type == NodeType.PRE_STATE:
            self.pre_states[node.id] = node
        if node.node_type == NodeType.STATE:
            self.states[node.id] = node
        if node.node_type == NodeType.PROTO:
            self.proto_states[node.id] = node

        if node.initial:
            self.root_nodes[node.id] = node

    def clone(self):
        for node in self.pre_states:
            if not node.cloned and node.children == []:
                node.cloned = True
                new_node = Node(tableau=self, parents=node, children=[], node_type=NodeType.PROTO, initial=node.initial,
                                formulas=node.formulas, rank=math.inf, min_child_rank=math.inf)
                node.children.append(new_node)


    def apply_alpha_beta(self):
        for node in self.proto_states:
            for formula in node.formulas:
                if formula.is_true():
                    new_node = Node(tableau=self, parents=node, children=[], node_type=NodeType.STATE,
                                    initial=node.initial, formulas=[formula], rank=math.inf, min_child_rank=math.inf)
                    node.children.append(new_node)

                if not formula.marked and not formula.is_elementary():
                    formula.mark()

                    if formula.is_alpha():
                        node.handle_alpha()
                    else:
                        assert formula.is_beta(), 'formula must be alpha/beta/elementary'
                        node.handle_beta()

            if len(node.children == 0):
                node.node_type = NodeType.STATE


    def remove_proto_states(self):
        pass

    def next_rule(self):
        pass

    def __eq__(self, other):
        return self.root_nodes == other.root_nodes and self.pre_states == other.pre_states \
               and self.proto_states == other.proto_states and self.states == other.states


def construct_pretableau(formula):
    tableau = Tableau()
    Node(tableau=tableau, parents=[], children=[], node_type=NodeType.PRE_STATE, initial=True,
         formulas=[formula], rank=math.inf, min_child_rank=math.inf)

    while True:
        current_tableau = copy.deepcopy(tableau)
        tableau.clone()

        if current_tableau == tableau:
            break

        tableau.apply_alpha_beta()
        tableau.remove_proto_states()
        tableau.next_rule()

    return tableau


def remove_prestates():
    return None


def remove_inconsistent():
    return None


def remove_inconsistent():
    return None


def remove_eventualities():
    return None


def remove_non_succesors():
    return None



def main(formula):
    tableau = construct_pretableau(formula)
    tableau = remove_prestates()
    tableau = remove_inconsistent()

    while True:
        tableau = remove_eventualities()
        tableau = remove_non_succesors()

    return is_open(tableau)