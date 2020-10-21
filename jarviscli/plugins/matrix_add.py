from plugin import plugin
from colorama import Fore


def get_matrix(jarvis, r, c):
    matrix = []
    for i in range(r):
        row_str = jarvis.input("enter row #{:d}: ".format(i))
        cur_row = [int(n) for n in row_str.split()]
        while len(cur_row) != c:
            jarvis.say("Row length should be {:d}".format(c))
            row_str = jarvis.input("enter row #{:d}: ".format(i))
            cur_row = [int(n) for n in row_str.split()]
        matrix.append(cur_row)
    return matrix


def print_matrix(matrix, r, c):
    for i in range(r):
        print(matrix[i])


@plugin("matrix add")
def matrix_add(jarvis, s):
    jarvis.say("Sum of matrices with dimensions M x N", Fore.GREEN)

    row = int(jarvis.input_number('Enter M (rows): '))
    col = int(jarvis.input_number('Enter N (cols): '))

    initial = get_matrix(jarvis, row, col)

    while True:
        next_decision = jarvis.input("Continue with next matrix? ")
        if next_decision.lower() == 'no':
            break
        next_matrix = get_matrix(jarvis, row, col)
        for i in range(row):
            for j in range(col):
                initial[i][j] += next_matrix[i][j]
        current_decision = jarvis.input("Print current sum matrix? ")
        if current_decision.lower() != 'no':
            print_matrix(initial, row, col)

    jarvis.say('Final sum matrix:')
    print_matrix(initial, row, col)
