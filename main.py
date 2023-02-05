
string = "esto es español de españa"
#string = "aaa"
#string = "aaaaaaaaaa"
#string = "ababababababab"
#string = "abababab"

rule_next_id = 1

rules = {"S": [0, []]}
digrams = {}

S = rules["S"]


def enforce_rule_utility(useless_rule_symbol, reference_rule_symbol):
    useless_rule = rules[useless_rule_symbol]
    reference_rule = rules[reference_rule_symbol]
    ref_index = reference_rule[1].index((useless_rule_symbol, ))
    length = len(useless_rule[1])

    # updating digram reference in hash table
    for i in range(len(useless_rule[1]) - 1):
        digrams[(useless_rule[1][i], useless_rule[1][i+1])] = reference_rule_symbol

    # deriving right-hand rule
    reference_rule[1].pop(ref_index)
    useless_rule[1].reverse()
    for i in useless_rule[1]:
        reference_rule[1].insert(ref_index, i)

    # updating context
    if ref_index > 0:
        link(reference_rule_symbol, ref_index - 1)
    if ref_index + length <= len(reference_rule):
        link(reference_rule_symbol, ref_index + length - 1)

    del rules[useless_rule_symbol]


def overlap(digram_index, rule1_symbol, rule2_symbol):
    if rule1_symbol != rule2_symbol:
        return -1
    rule1 = rules[rule1_symbol]
    digram = (rule1[1][digram_index], rule1[1][digram_index + 1])
    rule2 = rules[rule2_symbol]
    for i in range(len(rule2[1]) - 1):
        if rule2[1][i] == digram[0]:
            if rule2[1][i+1] == digram[1]:
                return i
    return None


def reduce_reference_count(digram, reference_rule_id):
    # reduce reference number in both symbols of the replaced digram if they are non-terminals
    if type(digram[0]) is tuple and len(digram[0]) == 1:
        rules[digram[0][0]][0] -= 1
        if rules[digram[0][0]][0] <= 1:
            enforce_rule_utility(digram[0][0], reference_rule_id)
    if type(digram[1]) is tuple and len(digram[1]) == 1:
        rules[digram[1][0]][0] -= 1
        if rules[digram[1][0]][0] <= 1:
            enforce_rule_utility(digram[1][0], reference_rule_id)


def link(rule_symbol, first_index):
    global rule_next_id
    rule = rules[rule_symbol]
    rh = rule[1]  # right hand
    context_left = None
    context_right = None
    other_context_left = None
    other_context_right = None
    digram = (rh[first_index], rh[first_index + 1])
    if digram in digrams:
        other_non_terminal = digrams[digram]
        other_rule = rules[other_non_terminal]

        other_index = overlap(first_index, rule_symbol, other_non_terminal)
        if other_index < 0 or (other_index >= 0 and abs(first_index - other_index) >= 2):
            if len(other_rule[1]) == 2:
                # USE EXISTING RULE
                rh.pop(first_index)
                rh.pop(first_index)
                if first_index > 0:
                    context_left = rh[first_index - 1]
                    digrams.pop((context_left, digram[0]))
                    #digrams[(context_left, (other_non_terminal,))] = rule_symbol
                    #link(rule_symbol, first_index - 1)
                if first_index < len(rh) - 1:
                    context_right = rh[first_index]
                    digrams.pop((digram[1], context_right))
                    #digrams[((other_non_terminal,0), context_right)] = rule_symbol
                    #link(rule_symbol, first_index)
                rh.insert(first_index, (other_non_terminal, ))
                other_rule[0] += 1
                if first_index > 0:
                    link(rule_symbol, first_index - 1)
                if first_index < len(rh) - 1:
                    link(rule_symbol, first_index)

                # reduce reference number in both symbols of the replaced digram if they are non-terminals
                reduce_reference_count(digram, digrams[digram])

            else:
                if digram[0] == digram[1] and abs(first_index - other_index) == 2:
                    # CREATE REPETITION GRAMMAR
                    index = min(first_index, other_index)
                    for x in range(4):
                        rh.pop(index)
                    #reduce_reference_count(digram, rule_symbol)  # reduce reference by 4
                    #reduce_reference_count(digram, rule_symbol)
                    rep_grammar = (4, digram[0])  # Repetition Grammar (n, a)
                    rh.insert(index, rep_grammar)
                    # update context
                    digrams.pop(digram)
                    if index > 0:
                        contxt_left = rh[index - 1]
                        digrams.pop((contxt_left, digram[0]))
                        link(rule_symbol, index - 1)
                    if index < len(rh) - 1:
                        contxt_right = rh[index + 1]
                        digrams.pop((digram[1], contxt_right))
                        link(rule_symbol, index)
                else:
                    # CREATE NEW RULE
                    new_rule = [2, [digram[0], digram[1]]]
                    new_rule_id = rule_next_id
                    rule_next_id += 1
                    rules[new_rule_id] = new_rule
                    rh.pop(first_index)
                    rh.pop(first_index)
                    if first_index > 0:
                        context_left = rh[first_index - 1]
                        digrams.pop((context_left, digram[0]))
                        #digrams[(context_left, (new_rule_id,))] = rule_symbol
                    if first_index < len(rh) - 1:
                        context_right = rh[first_index]
                        digrams.pop((digram[1], context_right))
                        #digrams[((new_rule_id,0), context_right)] = rule_symbol

                    rh.insert(first_index, (new_rule_id,))
                    if first_index > 0:
                        link(rule_symbol, first_index - 1)
                    if first_index < len(rh) - 1:
                        link(rule_symbol, first_index)

                    for i in range(len(other_rule[1])):
                        if other_rule[1][i] == digram[0]:
                            if other_rule[1][i + 1] == digram[1]:
                                other_rule[1].pop(i)
                                if i > 0:
                                    other_context_left = other_rule[1][i-1]
                                    if (other_context_left, digram[0]) in digrams:
                                        digrams.pop((other_context_left, digram[0]))
                                    #digrams[(other_context_left, (new_rule_id,))] = other_non_terminal
                                if i < len(other_rule[1]) - 1:
                                    other_context_right = other_rule[1][i+1]
                                    if (digram[1], other_context_right) in digrams:
                                        digrams.pop((digram[1], other_context_right))
                                    #digrams[((new_rule_id,), other_context_right)] = other_non_terminal

                                other_rule[1][i] = (new_rule_id,)

                                if i > 0:
                                    link(other_non_terminal, i - 1)
                                if i < len(other_rule[1]) - 1:
                                    link(other_non_terminal, i)

                                break

                    digrams[digram] = new_rule_id  # update reference in hash table
                    # reduce reference number in both symbols of the replaced digram if they are non-terminals
                    reduce_reference_count(digram, new_rule_id)

    else:
        if len(digram[0]) == 2 and digram[0][1] == digram[1]:
            gr = digram[0]
            sym = digram[1]
            rh.pop(first_index)
            rh.pop(first_index)
            rh.insert(first_index, (gr[0]+1, sym))
            #update context
            if first_index > 0:
                context = rh[first_index-1]
                digrams.pop((context, gr))
                link(rule_symbol, first_index-1)
            if first_index < len(rh) - 1:
                context = rh[first_index+1]
                digrams.pop((gr, context))
                link(rule_symbol, first_index)

            reduce_reference_count((sym, " "), rule_symbol)
        elif len(digram[1]) == 2 and digram[1][1] == digram[0]:
            gr = digram[1]
            sym = digram[0]
            rh.pop(first_index)
            rh.pop(first_index)
            rh.insert(first_index, (gr[0]+1, sym))
            #update context
            if first_index > 0:
                context = rh[first_index-1]
                digrams.pop((context, gr))
                link(rule_symbol, first_index-1)
            if first_index < len(rh) - 1:
                context = rh[first_index+1]
                digrams.pop((gr, context))
                link(rule_symbol, first_index)

            reduce_reference_count((sym, " "), rule_symbol)
        else:
            # INSERT DIGRAM IN HASH TABLE
            digrams[digram] = rule_symbol


if len(string) < 2:
    S[1] = list(string)
else:
    S[1] = list(string[0:1])
    #digrams[(S[1][0], S[1][1])] = "S"

    for n in string[1:]:
        digram = (S[1][len(S[1]) - 1], n)
        S[1].append(n)
        link("S", len(S[1]) - 2)

print(rules)
print(digrams)
