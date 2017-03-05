class Literal:
    prefix = True
    guest = 0
    table = 0

    def __init__(self, p, g, t):
        self.prefix = p
        self.guest = g
        self.table = t
        pass


# read from input file
input_file = open('input.txt', 'r')
# initialize the number of guests and tables
new_line = input_file.readline()
total_guests = int(new_line.split(' ')[0])
total_tables = int(new_line.split(' ')[1])

# initialize kb
kb = []
for i in range(total_guests):
    # a guest must be at some table
    guest_at_some_table_clause = []
    for j in range(total_tables):
        literal = Literal(True, i, j)
        # a guest must be at some table
        guest_at_some_table_clause.append(literal)
        literal = Literal(False, i, j)
        for k in range(j + 1, total_tables):
            # a guest can only be at one table = cannot be at two tables at the same time
            literal2 = Literal(False, i, k)
            guest_at_one_table_clause = [literal, literal2]
            kb.append(guest_at_one_table_clause)
    kb.append(guest_at_some_table_clause)
# read relationships from input file
new_line = input_file.readline()
while new_line != '':
    a = int(new_line[0]) - 1
    b = int(new_line[2]) - 1
    # friends must be at the same table
    if new_line[4] == 'F':
        for i in range(total_tables):
            guest1_literal = Literal(False, a, i)
            guest2_literal = Literal(True, b, i)
            clause = [guest1_literal, guest2_literal]
            kb.append(clause)
            guest1_literal = Literal(True, a, i)
            guest2_literal = Literal(False, b, i)
            clause = [guest1_literal, guest2_literal]
            kb.append(clause)
    # enemies cannot be at the same table
    if new_line[4] == 'E':
        for i in range(total_tables):
            guest1_literal = Literal(False, a, i)
            guest2_literal = Literal(False, b, i)
            clause = [guest1_literal, guest2_literal]
            kb.append(clause)
    new_line = input_file.readline()


# return the list of positive literals in clause
def get_positive_literals(clause):
    positive_literals = []
    for literal in clause:
        if literal.prefix:
            positive_literals.append(literal)
    return positive_literals


# return the list of negative literals in clause
def get_negative_literals(clause):
    negative_literals = []
    for literal in clause:
        if not literal.prefix:
            negative_literals.append(literal)
    return negative_literals


# check if two literals are the same
def is_same_literal(literal1, literal2):
    if literal1.guest == literal2.guest and literal1.table == literal2.table and literal1.prefix == literal2.prefix:
        return True
    else:
        return False


# check if two literals are complementary symbols
def is_complementary_symbol(symbol1, symbol2):
    if symbol1.guest == symbol2.guest and symbol1.table == symbol2.table and symbol1.prefix != symbol2.prefix:
        return True
    else:
        return False


# calculate complementary set of literals of two clauses
def get_complementary_literals(clause1, clause2):
    complementary = []
    for literal1 in clause1:
        for literal2 in clause2:
            if is_complementary_symbol(literal1, literal2):
                complementary.append(literal1)
    return complementary


# check whether a clause is a tautology
def is_tautology(clause):
    for i in range(len(clause) - 1):
        for j in range(i + 1, len(clause)):
            if is_complementary_symbol(clause[i], clause[j]):
                return True
    return False


# PL resolve
def pl_resolve(complementary, clause1, clause2):
    resolvents = []
    for comp in complementary:
        resolvent = []
        for literal1 in clause1:
            if not is_same_literal(comp, literal1):
                resolvent.append(literal1)
        for literal2 in clause2:
            if not is_complementary_symbol(comp, literal2):
                resolvent.append(literal2)
        if not is_tautology(resolvent):
            resolvents.append(resolvent)
    return resolvents


# check if two clauses are the same
def is_same_clause(c1, c2):
    if len(c1) == len(c2):
        for i in c1:
            is_same = False
            for j in c2:
                if is_same_literal(i, j):
                    is_same = True
                    break
            if not is_same:
                return False
        return True


# check if sub is the subset of super
def is_subset(super, sub):
    for i in sub:
        is_sub = False
        for j in super:
            if is_same_clause(i, j):
                is_sub = True
                break
        if not is_sub:
            return False
    return True


# check whether some clauses contain empty clause
def contains_empty(clauses):
    for clause in clauses:
        if len(clause) == 0:
            return True
    return False


# use PL_Resolution to check whether KB is satisfiable
def pl_resolution(kb):
    new = []
    while True:
        for i in range(len(kb) - 1):
            ci = kb[i]
            for j in range(i + 1, len(kb)):
                cj = kb[j]
                complementary = get_complementary_literals(ci, cj)
                if len(complementary) > 0:
                    resolvent = pl_resolve(complementary, ci, cj)
                    if contains_empty(resolvent):
                        return False
                    new += resolvent
        if is_subset(kb, new):
            return True
        kb += new


if pl_resolution(kb):
    print 'yes'
else:
    print 'no'
