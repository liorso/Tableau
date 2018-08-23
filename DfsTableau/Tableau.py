from DfsTableau.common import NodeType, TruthValue, BetaOrder
from DfsTableau.node import Node
from DfsTableau.formula import Formula

class Tableau:

    def __init__(self):
        self.pre_states = {}
        self.proto_states = {}
        self.states = {}
        self.future_states = []  # We use list as a stack cause we care about order

    def __repr__(self):
        return f'pre_states: {self.pre_states}\nproto_states: {self.proto_states}\n' \
               f'future_states: {self.future_states}\nstates: {self.states}'

    def insert(self, node):
        if node.node_type == NodeType.PRE_STATE:
            self.pre_states[node.id] = node
        elif node.node_type == NodeType.STATE:
            self.states[node.id] = node
        elif node.node_type == NodeType.PROTO:
            self.proto_states[node.id] = node
        elif node.node_type == NodeType.FUTURE:
            self.future_states.append(node)

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
        return self.pre_states == other.pre_states \
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

    def is_child_in_tableau(self, child):
        if child.node_type == NodeType.PRE_STATE:
            return child.id in self.pre_states
        if child.node_type == NodeType.STATE:
            return child.id in self.states
        assert False, "Not good?"

    def get_next_branch(self):
        new_tableau = Tableau()
        original_root = self.pre_states[1]
        original_curr_root = original_root
        new_curr_root = Node(tableau=new_tableau, parents=set(), children=set(), node_type=NodeType.PRE_STATE,
                             initial=True, formulas=[original_root.formulas])

        while True:
            if len(original_curr_root.children) == 0:
                return new_tableau

            elif len(original_curr_root.children) == 1:
                child = original_curr_root.children.values()[0]
                if new_tableau.is_child_in_tableau(child):
                    return new_tableau
                new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(), node_type=child.node_type,
                                initial=child.initial, formulas=[child.formulas])
                new_curr_root.children.add(new_node)
                new_curr_root = new_node
                continue

            elif len(original_curr_root.children) == 2:
                childs = original_curr_root.values()
                if childs[0].node_type == NodeType.FUTURE:
                    new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(),
                                    node_type=childs[1].node_type, initial=childs[1].initial,
                                    formulas=[childs[1].formulas])
                    new_curr_root.children.add(new_node)
                    new_curr_root = new_node
                    childs[0].node_type = NodeType.PRE_STATE
                    self.future_states.remove(childs[0])
                    self.pre_states[childs[0].id] = childs[0]
                    childs[1].done_branch = True

                elif childs[1].node_type == NodeType.FUTURE:
                    new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(),
                                    node_type=childs[0].node_type, initial=childs[0].initial,
                                    formulas=[childs[0].formulas])
                    new_curr_root.children.add(new_node)
                    new_curr_root = new_node
                    childs[1].node_type = NodeType.PRE_STATE
                    self.future_states.remove(childs[1])
                    self.pre_states[childs[1].id] = childs[1]
                    childs[0].done_branch = True

                elif childs[0].done_branch:
                    if new_tableau.is_child_in_tableau(child):
                        return new_tableau
                    new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(),
                                    node_type=childs[1].node_type, initial=childs[1].initial,
                                    formulas=[childs[1].formulas])
                    new_curr_root.children.add(new_node)
                    new_curr_root = new_node

                else:
                    assert childs[1].done_branch, "WTF"
                    if new_tableau.is_child_in_tableau(child):
                        return new_tableau
                    new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(),
                                    node_type=childs[0].node_type, initial=childs[0].initial,
                                    formulas=[childs[0].formulas])
                    new_curr_root.children.add(new_node)
                    new_curr_root = new_node

                continue

            assert False, "wtf??"


    def is_open(self):
        for state in self.states.values():
            if state.initial:
                return True
        return False

