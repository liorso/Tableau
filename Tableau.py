from common import NodeType, TruthValue
from node import Node
from formula import Formula


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

    def remove_pre_states(self):
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
        # return child if exists, else None
        if child.node_type == NodeType.PRE_STATE:
            return self.pre_states.get(child.id, None)
        if child.node_type == NodeType.STATE:
            return self.states.get(child.id, None)
        assert False, "Not good?"

    def get_next_branch(self):
        new_tableau = Tableau()
        original_root = self.pre_states[1]
        original_curr_root = original_root
        new_curr_root = Node(tableau=new_tableau, parents=set(), children=set(), node_type=NodeType.PRE_STATE,
                             initial=True, formulas=original_root.formulas, node_id=original_root.id)

        while True:
            if len(original_curr_root.children) == 0:
                return new_tableau

            elif len(original_curr_root.children) == 1:
                child = original_curr_root.children.pop()

                child_in_new_tableau = new_tableau.is_child_in_tableau(child)
                if child_in_new_tableau:
                    child_in_new_tableau.parents.add(new_curr_root)
                    new_curr_root.children.add(child_in_new_tableau)
                    return new_tableau

                new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(), node_type=child.node_type,
                                initial=child.initial, formulas=child.formulas, node_id=child.id)
                new_curr_root.children.add(new_node)
                new_curr_root = new_node
                original_curr_root = child
                continue

            elif len(original_curr_root.children) == 2:
                children = list(original_curr_root.children)
                if children[0].node_type == NodeType.FUTURE:
                    new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(),
                                    node_type=children[1].node_type, initial=children[1].initial,
                                    formulas=[children[1].formulas], node_id=children[1].id)
                    new_curr_root.children.add(new_node)
                    new_curr_root = new_node
                    children[0].node_type = NodeType.PRE_STATE
                    self.future_states.remove(children[0])
                    self.pre_states[children[0].id] = children[0]
                    children[1].done_branch = True
                    original_curr_root = children[1]

                elif children[1].node_type == NodeType.FUTURE:
                    new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(),
                                    node_type=children[0].node_type, initial=children[0].initial,
                                    formulas=children[0].formulas, node_id=children[0].id)
                    new_curr_root.children.add(new_node)
                    new_curr_root = new_node
                    children[1].node_type = NodeType.PRE_STATE
                    self.future_states.remove(children[1])
                    self.pre_states[children[1].id] = children[1]
                    children[0].done_branch = True
                    original_curr_root = children[0]

                elif children[0].done_branch:
                    child_in_new_tableau = new_tableau.is_child_in_tableau(children[1])
                    if child_in_new_tableau:
                        child_in_new_tableau.parents.add(new_curr_root)
                        new_curr_root.children.add(child_in_new_tableau)
                        return new_tableau

                    new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(),
                                    node_type=children[1].node_type, initial=children[1].initial,
                                    formulas=children[1].formulas, node_id=children[1].id)
                    new_curr_root.children.add(new_node)
                    new_curr_root = new_node
                    original_curr_root = children[1]

                else:
                    assert children[1].done_branch, "WTF"
                    child_in_new_tableau = new_tableau.is_child_in_tableau(children[0])
                    if child_in_new_tableau:
                        child_in_new_tableau.parents.add(new_curr_root)
                        new_curr_root.children.add(child_in_new_tableau)
                        return new_tableau

                    new_node = Node(tableau=new_tableau, parents=new_curr_root, children=set(),
                                    node_type=children[0].node_type, initial=children[0].initial,
                                    formulas=[children[0].formulas], node_id=children[0].id)
                    new_curr_root.children.add(new_node)
                    new_curr_root = new_node
                    original_curr_root = children[0]
                continue

            assert False, "wtf??"

    def is_open(self):
        for state in self.states.values():
            if state.initial:
                return True
        return False
