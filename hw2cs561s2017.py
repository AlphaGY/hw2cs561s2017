import random

random.seed(None)


# prefix 1=positive -1=negative
class Literal:
    prefix = 1
    guest = 0
    table = 0

    def __init__(self, p, g, t):
        self.prefix = p
        self.guest = g
        self.table = t
        pass


class Clause:
    literals = []

    def __init__(self, ls):
        self.literals = ls
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
    guest_at_some_table_clause = Clause([])
    for j in range(total_tables):
        literal = Literal(1, i, j)
        # a guest must be at some table
        guest_at_some_table_clause.literals.append(literal)
        literal = Literal(-1, i, j)
        for k in range(j + 1, total_tables):
            # a guest can only be at one table = cannot be at two tables at the same time
            literal2 = Literal(-1, i, k)
            guest_at_one_table_clause = Clause([literal, literal2])
            kb.append(guest_at_one_table_clause)
    kb.append(guest_at_some_table_clause)
# read relationships from input file
new_line = input_file.readline()
while new_line != '':
    a = int(new_line.split(' ')[0]) - 1
    b = int(new_line.split(' ')[1]) - 1
    # friends must be at the same table
    if new_line.split(' ')[2] == 'F\n':
        for i in range(total_tables):
            guest1_literal = Literal(-1, a, i)
            guest2_literal = Literal(1, b, i)
            clause = Clause([guest1_literal, guest2_literal])
            kb.append(clause)
            guest1_literal = Literal(1, a, i)
            guest2_literal = Literal(-1, b, i)
            clause = Clause([guest1_literal, guest2_literal])
            kb.append(clause)
    # enemies cannot be at the same table
    if new_line.split(' ')[2] == 'E\n':
        for i in range(total_tables):
            guest1_literal = Literal(-1, a, i)
            guest2_literal = Literal(-1, b, i)
            clause = Clause([guest1_literal, guest2_literal])
            kb.append(clause)
    new_line = input_file.readline()
# initialize assignment
model = [[]] * total_guests
for i in range(total_guests):
    model[i] = [0] * total_tables


# check if two symbol are the same symbol
# doesn't care about the positiveness or negativeness of the literal
def is_same_symbol(symbol1, symbol2):
    if symbol1.guest == symbol2.guest and symbol1.table == symbol2.table:
        return True
    else:
        return False


# return the set of symbols in the sentence
def get_symbols_from_sentence(s):
    symbols = []
    for clause in s:
        for literal in clause.literals:
            already_exists = False
            for exist in symbols:
                if is_same_symbol(exist, literal):
                    already_exists = True
                    break
            if not already_exists:
                symbols.append(literal)
    return symbols


# 0=undecided 1=True -1=False
def literal_status_in_model(l, m):
    if m[l.guest][l.table] == 0:
        return 0
    elif l.prefix == m[l.guest][l.table]:
        return 1
    else:
        return -1


# for CNF, in a clause, if one literal is True then the clause is True
# 0=undecided 1=True -1=False
def is_clause_true(cl, m):
    exist_undecided = False
    for l in cl.literals:
        if literal_status_in_model(l, m) == 1:
            return 1
        if literal_status_in_model(l, m) == 0:
            exist_undecided = True
    if exist_undecided:
        return 0
    else:
        return -1


# check if every clauses is true in the given model
def every_clause_is_true(cls, m):
    for cl in cls:
        if is_clause_true(cl, m) != 1:
            return False
    return True


# check if exist some clause is false in the given model
def some_clause_is_false(cls, m):
    for cl in cls:
        if is_clause_true(cl, m) == -1:
            return True
    return False


# return positive symbols for a given clause
def get_positive_symbols(cl):
    positive = []
    for l in cl.literals:
        if l.prefix == 1:
            positive.append(l)
    return positive


# return negative symbols for a given clause
def get_negative_symbols(cl):
    negative = []
    for l in cl.literals:
        if l.prefix == -1:
            negative.append(l)
    return negative


# check if a set of symbols contains one particular symbol
def contain_symbol(sbls, sbl):
    for s in sbls:
        if is_same_symbol(s, sbl):
            return True
    return False


# delete every symbol that is equal to l from clause
def delete_literal_from_clause(cl, l):
    length = len(cl)
    i = 0
    while i < length:
        if is_same_symbol(cl[i], l):
            del cl[i]
            length -= 1
        else:
            i += 1
    return cl


# get pure symbol set
def get_pure_symbols(sbls, cls, m):
    result = []
    candidate_pure_positive_symbol = []
    candidate_pure_negative_symbol = []
    for cl in cls:
        if is_clause_true(cl, m) == 1:
            continue
        positive_sbls = get_positive_symbols(cl)
        negative_sbls = get_negative_symbols(cl)
        for p in positive_sbls:
            if contain_symbol(sbls, p) and not contain_symbol(candidate_pure_positive_symbol, p):
                candidate_pure_positive_symbol.append(p)
        for n in negative_sbls:
            if contain_symbol(sbls, n) and not contain_symbol(candidate_pure_negative_symbol, n):
                candidate_pure_negative_symbol.append(n)
    for s in sbls:
        if contain_symbol(candidate_pure_positive_symbol, s) and contain_symbol(candidate_pure_negative_symbol, s):
            candidate_pure_positive_symbol = delete_literal_from_clause(candidate_pure_positive_symbol, s)
            candidate_pure_negative_symbol = delete_literal_from_clause(candidate_pure_negative_symbol, s)
    for p in candidate_pure_positive_symbol:
        result.append(Literal(1, p.guest, p.table))
    for n in candidate_pure_negative_symbol:
        result.append(Literal(-1, n.guest, n.table))
    return result


# check whether a clause is a unit clause: only have one literal
def is_unit_clause(cl):
    if len(cl.literals) == 1:
        return True
    else:
        return False


# get unit clause set :symbols and their prefix are their values
def get_unit_clause(cls, m):
    result = []
    for cl in cls:
        if is_clause_true(cl, m) == 0:
            unassigned = Literal(0, -1, -1)
            # traditional definition of unit clause
            if is_unit_clause(cl):
                unassigned = cl.literals[0]
            # unit clause in DPLL context = has a single unassigned literal
            else:
                for l in cl.literals:
                    if literal_status_in_model(l, m) == 0:
                        if is_same_symbol(unassigned, Literal(0, -1, -1)):
                            unassigned = l
                        # more than one unassigned literal
                        else:
                            unassigned = Literal(0, -1, -1)
                            break
            if not is_same_symbol(unassigned, Literal(0, -1, -1)):
                result.append(unassigned)
    return result


# super set of symbols minus subset of symbols
def minus(super, sub):
    for sub_sbl in sub:
        length = len(super)
        i = 0
        while i < length:
            if is_same_symbol(super[i], sub_sbl):
                del super[i]

                length -= 1
            else:
                i += 1
    return super


# update model by assigning values to some symbol
def model_union(m, sbls):
    for s in sbls:
        m[s.guest][s.table] = s.prefix
    return m


def dpll(cls, sbls, m):
    # if every clause is true in this partial model, then terminate
    if every_clause_is_true(cls, m):
        return True
    # if exist some clause is false in this partial model, then terminate
    if some_clause_is_false(cls, m):
        return False
    # pure symbol rule
    pure_symbols = get_pure_symbols(sbls, cls, m)
    if len(pure_symbols) > 0:
        return dpll(cls, minus(sbls, pure_symbols), model_union(m, pure_symbols))
    # unit clause rule
    unit_clause_symbols = get_unit_clause(cls, m)
    if len(unit_clause_symbols) > 0:
        return dpll(cls, minus(sbls, unit_clause_symbols), model_union(m, unit_clause_symbols))
    s = [sbls[0]]
    sn = [Literal(0 - sbls[0].prefix, sbls[0].guest, sbls[0].table)]
    return dpll(cls, minus(sbls, s), model_union(m, s)) or dpll(cls, minus(sbls, s), model_union(m, sn))


# check if two symbol are the same symbol
# doesn't care about the positiveness or negativeness of the literal
def is_same_symbol(symbol1, symbol2):
    if symbol1.guest == symbol2.guest and symbol1.table == symbol2.table:
        return True
    else:
        return False


# return the set of symbols in the sentence
def get_symbols_from_sentence(s):
    symbols = []
    for clause in s:
        for literal in clause.literals:
            already_exists = False
            for exist in symbols:
                if is_same_symbol(exist, literal):
                    already_exists = True
                    break
            if not already_exists:
                symbols.append(literal)
    return symbols


# one guest on one table
def generate_random_assignment():
    # initialize assignment
    model = [[]] * total_guests
    for i in range(total_guests):
        model[i] = [0] * total_tables
        for j in range(total_tables):
            model[i][j] = int(random.choice([-1, 1]))
    return model


# 0=undecided 1=True -1=False
def literal_status_in_model(l, m):
    if m[l.guest][l.table] == 0:
        return 0
    elif l.prefix == m[l.guest][l.table]:
        return 1
    else:
        return -1


# for CNF, in a clause, if one literal is True then the clause is True
# 0=undecided 1=True -1=False
def is_clause_true(cl, m):
    exist_undecided = False
    for l in cl.literals:
        if literal_status_in_model(l, m) == 1:
            return 1
        if literal_status_in_model(l, m) == 0:
            exist_undecided = True
    if exist_undecided:
        return 0
    else:
        return -1


# check if a give model is a correct assignment
def is_clauses_satisfied_by_model(cls, m):
    for c in cls:
        if is_clause_true(c, m) == -1:
            return False
    return True


# randomly select a false clause and return its index
def random_select_false_clause(cls, m):
    false_cls = []
    for i in range(len(cls)):
        if is_clause_true(cls[i], m) == -1:
            false_cls.append(i)
    return false_cls[random.randint(0, len(false_cls) - 1)]


def copy_model(m):
    model = [[]] * total_guests
    for i in range(total_guests):
        model[i] = [0] * total_tables
        for j in range(total_tables):
            model[i][j] = m[i][j]
    return model


# filp m[i][j]
def flip(m, i, j):
    new = copy_model(m)
    new[i][j] = 0 - m[i][j]
    return new


# return the model after randomly flip a symbol in a give clause
def random_flip_symbol(cl, m):
    i = random.randint(0, len(cl.literals) - 1)
    return flip(m, cl.literals[i].guest, cl.literals[i].table)


# return the number of satisfied clauses
def get_number_of_true_clause(cls, m):
    sum = 0
    for c in cls:
        if is_clause_true(c, m):
            sum += 1
    return sum


# return the model which maximizes the number of satisfied clauses
def maximize_satisfied_clauses(cls, m):
    max = get_number_of_true_clause(cls, m)
    max_model = copy_model(m)
    for i in range(total_guests):
        for j in range(total_tables):
            new = flip(m, i, j)
            temp = get_number_of_true_clause(cls, new)
            if temp > max:
                max_model = new
                max = temp
    return max_model


def walksat(cls, p):
    m = generate_random_assignment()
    while True:
        if is_clauses_satisfied_by_model(cls, m):
            return m
        clause_index = random_select_false_clause(cls, m)
        if random.random() < p:
            m = random_flip_symbol(cls[clause_index], m)
        else:
            m = maximize_satisfied_clauses(cls, m)


# print_assignment
def print_model(m):
    string = ''
    for i in range(total_guests):
        for j in range(total_tables):
            if m[i][j] == 1:
                string += (str(i + 1) + " " + str(j + 1))
        if i < total_guests - 1:
            string += '\n'
    return string


output = ''
symbols = get_symbols_from_sentence(kb)
if dpll(kb, symbols, model):
    output += 'yes\n'
    output += print_model(walksat(kb, 0.5))
else:
    output += 'no'
output_file = open('output.txt', 'w')
output_file.write(output)
