import collections
import string
act = ""
last = ""
minus, plus = 0, 0
variables_dict = {}
operator_dict = {'0': 0, '+': 1, '-': 1, '/': 2, '*': 2}
alpha_list = string.ascii_letters
num_list = [str(x) for x in range(10)]
oper_list = ["+", "-", "/", "*", "(", ")", "=", " "]

_help = '''The program calculates expressions like these: 
    4 + 6 - 8
    a = 3 - 4
    3 + 8 * ((4 + 3) * 2 + 1) - 6 / (2 + 1)
    
    Two adjacent minus signs turn into a plus. The program uses an algorithm that converts an expression from 
    infix to postfix notation and calculates the result.
    
    "/exit" : Stop program
    "/help" : Display help text.
    '''


def input_ok(_str):
    # Check if legal mathematical expression with +-=*/ operators between numbers/variables.
    # Also check if variable names are alphabetical.

    if "**" in _str.replace(" ", "") or "//" in _str.replace(" ", ""):
        return False

    prior_sign = True
    _last = "sign"
    for i in _str:
        # isalpha() function returns true for characters outside the alphabet range so
        # input must be checked like this:
        if not(i in alpha_list or i in num_list or i in oper_list):
            return False

        if i.isnumeric() or i.isalpha():
            if prior_sign:
                _last = "num"
            else:
                return False

        elif i.isspace():
            if _last == "num":
                prior_sign = False
            _last = "space"
        elif i in "+-=*/":
            _last = "sign"
            prior_sign = True

    return True


def compute(_str):
    # Input has already been error-checked.
    # Replace possible variables, in input, with values from dict.
    # If assignment then add variable to dict.
    global variables_dict
    new_var = ""
    _act = _str.split(" ")
    new = ""
    for i in _act:
        if i.isalpha() and str(i) in variables_dict:
            new += str(variables_dict[i])

        else:
            new += str(i)

    expression = input_fix(new).lstrip()  # Add spaces around operators and adjust +/- if negative variables from dict.

    if "=" in expression:   # New identifier.
        new_var = str(_act[0])
        new_value = post_fix(expression.split(" = ")[1].lstrip())
        variables_dict.update({new_var: new_value})
    else:
        total = post_fix(expression)
        if total is not None:
            print(round(int(total)))


def post_fix(_str):
    # Converts an expression from infix to postfix notation.
    # Puts it in stack and computes the expression. Returns the result.
    # 1. Add operands (numbers and variables) to the result (postfix notation) as they arrive.
    # 2. If the stack is empty or contains a left parenthesis on top, push the incoming operator on the stack.
    # 3. If the incoming operator has higher precedence than the top of the stack, push it on the stack.
    # 4. If the incoming operator has lower or equal precedence than or to the top of the stack, pop the stack and
    #    add operators to the result until you see an operator that has a smaller precedence or a left parenthesis
    #    on the top of the stack; then add the incoming operator to the stack.
    # 5. If the incoming element is a left parenthesis, push it on the stack.
    # 6. If the incoming element is a right parenthesis, pop the stack and add operators to the result until you
    #    see a left parenthesis. Discard the pair of parentheses.
    # 7. At the end of the expression, pop the stack and add all operators to the result.

    global variables_dict, operator_dict
    _str2 = input_fix(_str).lstrip()
    _equation = _str2.split(" ")

    _que = collections.deque()
    _new = []
    loop = True
    _i = _x = 0
    while loop:
        if _equation[_i].isnumeric() or _equation[_i].isalpha():    # 1
            _new.append(_equation[_i])
        else:
            if not _que:
                _top = "0"
            else:
                _top = _que[-1]

            if _equation[_i] == "(":                                # 5
                _que.append(_equation[_i])
            elif _equation[_i] == ")":                              # 6
                while _que:
                    _sign = _que.pop()
                    if _sign == "(":        # ok break( )
                        break
                    else:
                        _new.append(_sign)
                if _sign != "(":            # needs to be left parenthesis on par with the right one in _equation[_i]
                    _que.append(_equation[_i])  # to have unbalanced parenthesis in _que to signal error later

            elif not _que or _que[-1] == "(":                       # 2
                _que.append(_equation[_i])
            elif operator_dict[_equation[_i]] > operator_dict[_top]:  # 3
                _que.append(_equation[_i])
            elif _que and operator_dict[_equation[_i]] <= operator_dict[_top] and _top != "(":  # 4
                while _que and _que[-1] != "(" and operator_dict[_equation[_i]] <= operator_dict[_que[-1]]:
                    _new.append(_que.pop())
                _que.append(_equation[_i])

        _i += 1
        if _i >= len(_equation):
            loop = False

    while _que:
        if _que[-1] in "()":
            print("Invalid expression")
            return
        _new.append(_que.pop())

    # now compute the expression
    _solve = collections.deque()
    # The next loop expects two numbers to pop from _solve. In case first number is negative we only have one
    # number before the '-' sign, so.. we fix it with a dummy number zero so it doesn't crash on popping _b.
    _solve.append(0)
    for _i in _new:
        if _i.isnumeric():
            _solve.append(_i)
        elif _i in "+-*/":
            _a = _solve.pop()
            _b = _solve.pop()
            _x = eval(str(_b) + _i + str(_a))
            _solve.append(_x)
        else:
            print("Unexpected char in expression.")
            print(_i)
            return

    if _solve:  # in case input was only one number with no sign and no equation.
        _x = _solve.pop()
    return _x


def unknown_variable(_str):
    # check if assignment side of expression contains undefined variable names.
    global variables_dict

    if "=" in _str:
        _list = _str.rsplit("=", 1)
        _unknown_var = [x for x in _list[1] if x.isalpha() and x not in variables_dict]
    else:
        _list = [_str]
        _unknown_var = [x for x in _list if x.isalpha() and x not in variables_dict]
    if len(_unknown_var) > 0:
        return True

    return False


def invalid_identifier(_str):
    # If first value is a variable, it must be all characters.

    _act = _str.replace(" ", "")
    if "=" in _act:
        _list = _act.split("=")
        if not _list[0].isalpha():
            return True

    return False


def invalid_assignment(_str):
    # Get rid of brackets and operators, except plus, split on plus and check if all numbers
    # or character-only variable-names, on the assignment side.

    _act = _str.replace(" ", "")

    if "=" in _act:
        if _act.count("=") > 1:
            return True
        _list = _act.replace("-", "+").replace("/", "+").replace("*", "+").replace("(", "").replace(")", "")\
            .split("=", 1)
        assignment = _list[1].split("+")
        assign_list = assignment
        if [i for i in assign_list if not (i.isalpha() or i.isnumeric() or i == "")]:
            return True

    return False


def input_fix(_str):
    # Get rid of excessive +/- signs and return mathematically correct string.
    # Place spaces around numbers and variables: ( 1 + b * 10 ) / 2
    if _str[0] == "/":  # If command then don't fix
        return _str

    while (" " in _str) or ("++" in _str) or ("--" in _str) or ("+-" in _str) or ("-+" in _str):
        _str = _str.replace(" ", "")
        _str = _str.replace("++", "+")
        _str = _str.replace("--", "+")
        _str = _str.replace("+-", "-")
        _str = _str.replace("-+", "-")

    return _str.replace("-", " - ").replace("+", " + ").replace("=", " = ")\
        .replace("*", " * ").replace("/", " / ").replace("(", "( ").replace(")", " )")


while act != "/exit":

    act_i = input()
    if act_i == "":
        continue
    else:
        act = input_fix(act_i).lstrip()

    if act == "/help":
        print(_help)
    elif act == "/exit":
        break
    elif act[0] == "/":
        print("Unknown command")        # /?
    elif invalid_identifier(act):
        print("Invalid identifier")     # a1 = 8 : Invalid identifier
    elif invalid_assignment(act):
        print("Invalid assignment")     # n = a2a,  a = 7 = 8 : Invalid assignment
    elif unknown_variable(act):
        print("Unknown variable")       # b = c : Unknown variable
    elif not input_ok(act):
        print("Invalid expression")     # missing +/-, unbalanced brackets
    else:
        compute(act)

print("Bye!")
