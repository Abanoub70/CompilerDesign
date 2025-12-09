from collections import deque

terminals = set('=+-*/%|\\&^!#(){}[]\'";:,."~`_')
st = deque()
idx = 0
input_str = ""
grammar = [('', '') for _ in range(4)]

def is_terminal(n):
    return n.islower() or n.isdigit() or n in terminals

def is_simple_grammar():
    for i in grammar:
        if is_terminal(i[0]) or not is_terminal(i[1][0]):
            return False
    if grammar[0][1][0] == grammar[1][1][0] or grammar[2][1][0] == grammar[3][1][0]:
        return False
    return True

def solve():
    global idx
    while st:
        top = st[-1]
        if is_terminal(top):
            if idx < len(input_str) and top == input_str[idx]:
                st.pop()
                idx += 1
            else:
                return False
        else:
            non_terminal = -1
            if top == 'S':
                non_terminal = 0
            elif top == 'B':
                non_terminal = 2
            else:
                return False
            
            rule = -1
            if idx < len(input_str) and input_str[idx] == grammar[non_terminal][1][0]:
                rule = 0
            elif idx + 1 < len(input_str) and input_str[idx] == grammar[non_terminal + 1][1][0]:
                rule = 1
            else:
                return False
            
            st.pop()
            for char in reversed(grammar[non_terminal + rule][1]):
                st.append(char)
    return idx == len(input_str)

def main():
    global idx, input_str, st, grammar
    while True:
        grammar[0] = ('S', '')
        grammar[1] = ('S', '')
        grammar[2] = ('B', '')
        grammar[3] = ('B', '')

        for i in range(4):
            non_terminal = 'S' if i < 2 else 'B'
            grammar[i] = (non_terminal, input(f"Enter rule number {i + 1} for non-terminal '{non_terminal}': "))

        if not is_simple_grammar():
            print("Not a simple grammar")
            continue
        
        while True:
            input_str = input("Enter the string to be checked: ")
            print("The input string: ", [f"'{char}'" for char in input_str])
            st.clear()
            idx = 0
            st.append('S')

            f = solve()
            print("Stack after checking: ", [f"'{char}'" for char in reversed(st)])
            print("The rest of the unchecked string: ", [f"'{char}'" for char in input_str[idx:]])
            if f:
                print("The input string is Accepted.\n")
            else:
                print("The input string is Rejected.\n")
            
            print("1- Another grammar.")
            print("2- Another string.")
            print("3- Exit.")
            t = int(input())
            if t == 1:
                break
            if t == 3:
                return

if __name__ == "__main__":
    main()