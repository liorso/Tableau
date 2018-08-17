import math
import copy
from common import NodeType, TruthValue
from node import Node
from formula import Formula
# TODO ranks and initial in node creations

class Tableau:

    def __init__(self):
        self.root_nodes = {}
        self.pre_states = {}
        self.proto_states = {}
        self.states = {}

        # TODO  - do we need?
        self.state_to_pre = []
        self.pre_to_state = []

    def __repr__(self):
        return f'self.root_nodes: {self.root_nodes}, self.pre_states: {self.pre_states},' \
               f'self.proto_states: {self.proto_states},  self.states: {self.states}' \

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
        for node in self.pre_states.values():
            if not node.cloned and len(node.children) == 0:
                node.cloned = True
                new_node = Node(tableau=self, parents=node, children=set(), node_type=NodeType.PROTO, initial=False,
                                formulas=node.formulas, rank=math.inf, min_child_rank=math.inf)
                node.children.append(new_node)

    def apply_alpha_beta(self):
        for node in self.proto_states.values():
            for formula in node.formulas:
                if formula.is_true():
                    new_node = Node(tableau=self, parents=node, children=set(), node_type=NodeType.STATE,
                                    initial=False, formulas=node.formulas, rank=math.inf, min_child_rank=math.inf)
                    node.children.append(new_node)

                if not formula.marked and not formula.is_elementary():
                    formula.mark()

                    is_alpha, formulas = formula.is_alpha()
                    if is_alpha:
                        node.handle_alpha(formulas)

                    is_beta, formulas = formula.is_beta()
                    assert is_beta, 'formula must be alpha/beta/elementary'
                    node.handle_beta(formulas)

            if len(node.children) == 0:
                node.node_type = NodeType.STATE

    def remove_proto_states(self):
        for proto_state in self.proto_states.values():
            assert proto_state.node_type == NodeType.PROTO
            for parent in proto_state.parents:
                assert parent.node_type == NodeType.PRE_STATE
                parent.children.remove(proto_state)
                parent.children.update(proto_state.children)

            for child in proto_state.children:
                assert child.node_type == NodeType.STATE
                child.parents.remove(proto_state)
                child.parents.update(proto_state.parents)

        self.proto_states = {}

    def next_rule(self):
        for state in self.states.values():
            if not state.cloned:
                state.cloned = True
                if state.is_consistent():
                    next_formulas = state.get_next_formulas()
                    if len(next_formulas) == 0:
                        next_formulas = set(TruthValue.TRUE)

                    for pre_state in self.pre_states.values():
                        if next_formulas == pre_state.formulas:
                            pre_state.parents.add(state)
                            state.children.add(pre_state)
                            break

                    new_node = Node(tableau=self, parents=state, children=set(), node_type=NodeType.PRE_STATE,
                                    initial=False, formulas=next_formulas, rank=math.inf, min_child_rank=math.inf)
                    state.children.add(new_node)

    def __eq__(self, other):
        return self.root_nodes == other.root_nodes and self.pre_states == other.pre_states \
               and self.proto_states == other.proto_states and self.states == other.states


def construct_pretableau(formula):
    tableau = Tableau()
    Node(tableau=tableau, parents=set(), children=set(), node_type=NodeType.PRE_STATE, initial=True,
         formulas=[formula], rank=math.inf, min_child_rank=math.inf)

    while True:
        print(tableau)
        current_tableau = copy.deepcopy(tableau)
        tableau.clone()
        print(tableau)
        if current_tableau == tableau:
            break

        tableau.apply_alpha_beta()
        print(tableau)
        tableau.remove_proto_states()
        tableau.next_rule()

    return tableau


def remove_prestates():
    # if id == 0 (root) mark child as initial
    return None


def remove_inconsistent():
    return None


def remove_eventualities():
    return None


def remove_non_succesors():
    return None


def build_tableau(formula):
    tableau = construct_pretableau(formula)
    tableau = remove_prestates()
    tableau = remove_inconsistent()

    while True:
        tableau = remove_eventualities()
        tableau = remove_non_succesors()

    return is_open(tableau)


def main():
    build_tableau(Formula('Xp'))

main()
