string = "es español de españa"


def to_tuple(lst):
    return tuple(to_tuple(i) if isinstance(i, list) else i for i in lst)


rule_next_id = 1

rules = {"S": [0, []]}
digrams = {}

S = rules["S"]


def enforce_rule_utility(useless_rule_symbol, reference_rule_symbol):
    useless_rule = rules[useless_rule_symbol]
    reference_rule = rules[reference_rule_symbol]
    ref_index = reference_rule.index((useless_rule_symbol, ))
    length = len(useless_rule[1])

    # updating digram reference in hash table
    for i in range(len(useless_rule[1]) - 1):
        digrams[(useless_rule[1][i], useless_rule[1][i+1])] = reference_rule_symbol

    # deriving right-hand rule
    reference_rule[1].pop(ref_index)
    useless_rule.reverse()
    for i in useless_rule:
        reference_rule[1].insert(ref_index, i)

    # updating context
    if ref_index > 0:
        link(reference_rule_symbol, ref_index - 1)
    if ref_index + length <= len(reference_rule):
        link(reference_rule_symbol, ref_index + length - 1)


def link(rule_symbol, first_index):
    global rule_next_id
    rule = rules[rule_symbol]
    rh = rule[1]  # right hand
    digram = (rh[first_index], rh[first_index + 1])
    if digram in digrams:
        other_non_terminal = digrams[digram]
        other_rule = rules[other_non_terminal]

        if len(other_rule[1]) == 2:  # Use existing rule
            rh.pop(first_index)
            rh.pop(first_index)
            rh.insert(first_index, (other_non_terminal, ))
            other_rule[0] += 1
        else:  # Create new rule
            rh.pop(first_index)
            rh.pop(first_index)
            
            new_rule = [2, [digram[0], digram[1]]]
            new_rule_id = rule_next_id
            rule_next_id += 1
            rules[new_rule_id] = new_rule

            rh.insert(first_index, (new_rule_id,))
            for i in range(len(other_rule[1])):
                if other_rule[1][i] == digram[0]:
                    if other_rule[1][i + 1] == digram[1]:
                        other_rule[1].pop(i)
                        other_rule[1][i] = (new_rule_id,)

                        #update context of other rule
                        if other_non_terminal == rule_symbol and abs(first_index - i) <= 2:
                            digrams.pop((digram[1], digram[0]))
                            digrams[(new_rule_id, new_rule_id)] = rule_symbol

                        if i > 0:
                            temp = (other_rule[1][i - 1], digram[0])
                            if temp in digrams:
                                digrams.pop(temp)
                                link(other_non_terminal, i - 1)
                        if i < len(other_rule[1]) - 1:
                            temp = (digram[1], other_rule[1][i + 1])
                            if temp in digrams:
                                digrams.pop(temp)
                                link(other_non_terminal, i)
                        break

            digrams[digram] = new_rule_id  # update reference in hash table

        # update context of this rule
        if first_index > 0:
            context_left = rh[first_index - 1]
            temp = (context_left, digram[0])
            if temp in digrams:
                digrams.pop(temp)
                link(rule_symbol, first_index - 1)
        if first_index < len(rh) - 1:
            context_right = rh[first_index + 1]
            temp = (digram[1], context_right)
            if temp in digrams:
                digrams.pop(temp)
                link(rule_symbol, first_index)

        # reduce reference number in both symbols of the replaced digram if they are non-terminals
        if type(digram[0]) is tuple:
            rules[digram[0][0]][0] -= 1
            if rules[digram[0][0]][0] <= 1:
                enforce_rule_utility(digram[0][0], rule_symbol)
        if type(digram[1]) is tuple:
            rules[digram[1][0]][0] -= 1
            if rules[digram[0][0]][0] <= 1:
                enforce_rule_utility(digram[1][0], rule_symbol)

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