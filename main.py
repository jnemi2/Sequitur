
string = "esto es español de españa"
#string = "aaaaaaaaaa"

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

        if len(other_rule[1]) == 2:  # Use existing rule
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

        else:  # Create new rule
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
        if type(digram[0]) is tuple:
            rules[digram[0][0]][0] -= 1
            if rules[digram[0][0]][0] <= 1:
                enforce_rule_utility(digram[0][0], new_rule_id)
        if type(digram[1]) is tuple:
            rules[digram[1][0]][0] -= 1
            if rules[digram[1][0]][0] <= 1:
                enforce_rule_utility(digram[1][0], new_rule_id)

    else:
        digrams[digram] = rule_symbol  # Insert digram in hash table


if len(string) < 2:
    S[1] = list(string)
else:
    S[1] = list(string[0:2])
    digrams[(S[1][0], S[1][1])] = "S"

    for n in string[2:]:
        digram = (S[1][len(S[1]) - 1], n)
        S[1].append(n)
        link("S", len(S[1]) - 2)

print(rules)
print(digrams)
