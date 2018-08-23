from BfsTableau.common import NodeType, TruthValue
from BfsTableau.node import Node
from BfsTableau.formula import Formula


class Tableau:

    def __init__(self):
        self.root_nodes = {}
        self.pre_states = {}
        self.proto_states = {}
        self.states = {}

    def __repr__(self):
        return f'pre_states: {self.pre_states}\n' \
               f'proto_states: {self.proto_states}\nstates: {self.states}'

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
        changed = False
        for node in self.pre_states.values():
            if not node.cloned and len(node.children) == 0:
                node.cloned = True
                new_node = Node(tableau=self, parents=node, children=set(), node_type=NodeType.PROTO,
                                initial=node.initial, formulas=node.formulas)
                node.children.add(new_node)
                changed = True
        return changed

    def apply_alpha_beta(self):
        for node in self.proto_states.values():
            for formula in node.formulas:
                if formula.is_true():
                    new_node = Node(tableau=self, parents=node, children=set(), node_type=NodeType.STATE,
                                    initial=node.initial, formulas=node.formulas)
                    node.children.add(new_node)

                elif not formula.marked and not formula.is_elementary():
                    formula.mark()

                    is_alpha, formulas = formula.is_alpha()
                    formulas = {Formula(formulas[0]), Formula(formulas[1])}
                    if is_alpha:
                        node.handle_alpha(formulas)

                    else:
                        is_beta, formulas = formula.is_beta()
                        formulas = {Formula(formulas[0]), Formula(formulas[1])}
                        assert is_beta, 'formula must be alpha/beta/elementary'
                        node.handle_beta(formulas)

            if len(node.children) == 0:
                node.node_type = NodeType.STATE
                self.states[node.id] = node

        self.proto_states = {i: node for (i, node) in self.proto_states.items() if node.node_type == NodeType.PROTO}

    def remove_proto_states(self):
        for proto_state in self.proto_states.values():
            assert proto_state.node_type == NodeType.PROTO
            proto_state.remove()
        self.proto_states = {}

    def next_rule(self):
        for state in self.states.values():
            if not state.cloned:
                state.cloned = True
                if state.is_consistent():
                    next_formulas = state.get_next_formulas()
                    if len(next_formulas) == 0:
                        next_formulas = {Formula(TruthValue.TRUE.value)}

                    found_pre_state = False
                    for pre_state in self.pre_states.values():
                        if next_formulas == pre_state.formulas:
                            pre_state.parents.add(state)
                            state.children.add(pre_state)
                            found_pre_state = True
                            continue

                    if not found_pre_state:
                        new_node = Node(tableau=self, parents=state, children=set(), node_type=NodeType.PRE_STATE,
                                        initial=False, formulas=next_formulas)
                        state.children.add(new_node)

    def __eq__(self, other):
        return self.root_nodes == other.root_nodes and self.pre_states == other.pre_states \
               and self.proto_states == other.proto_states and self.states == other.states

    def remove_prestates(self):
        for pre_state in self.pre_states.values():
            assert pre_state.node_type == NodeType.PRE_STATE
            pre_state.remove()
        self.pre_states = {}

    @staticmethod
    def remove_state(node):
        successors = node.find_all_successors()
        candidates = successors
        bad = successors
        bad.add(node)

        changed = True
        while changed:
            changed = False
            for successor in successors:
                for parent in successor.parents:
                    if parent not in bad:
                        changed = True
                        candidates.remove(successor)
                        bad.remove(successor)

        candidates.add(node)
        for node_to_remove in candidates:
            node_to_remove.simple_remove()
        return candidates

    def remove_inconsistent(self):
        self.remove_non_successors()

    def remove_eventualities(self):
        removed = False
        changed_in_last_round = True

        while changed_in_last_round:
            changed_in_last_round = False
            for state in self.states.values():
                if state.node_type != NodeType.REMOVED and state.has_unfulfilled_eventuality():
                    self.remove_state(state)
                    removed = True
                    changed_in_last_round = True
        self.states = {node_id: node for node_id, node in self.states.items() if node.node_type != NodeType.REMOVED}
        return removed

    def remove_non_successors(self):
        changed = False
        removed = True
        while removed:
            removed = False
            for state in self.states.values():
                if len(state.children) == 0 and state.node_type != NodeType.REMOVED:
                    for parent in state.parents:
                        parent.children.remove(state)
                    state.node_type = NodeType.REMOVED
                    removed = True
                    changed = True
        self.states = {node_id: node for node_id, node in self.states.items() if node.node_type != NodeType.REMOVED}
        return changed

    def is_open(self):
        for state in self.states.values():
            if state.initial:
                return True
        return False

