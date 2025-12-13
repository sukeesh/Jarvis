from plugin import plugin


@plugin("sudoku")
class SudokuSolver:
    """
    Solves sudoko puzzle. Save the puzzle in a file (space separated)
    and pass the file name as parameter.
    The missing digits has to be marked `0`

    Sample input :
    3 0 6 5 0 8 4 0 0
    5 2 0 0 0 0 0 0 0
    0 8 7 0 0 0 0 3 1
    0 0 3 0 1 0 0 8 0
    9 0 0 8 6 3 0 0 5
    0 5 0 0 9 0 6 0 0
    1 3 0 0 0 0 2 5 0
    0 0 0 0 0 0 0 7 4
    0 0 5 2 0 6 3 0 0

    ~> Hi, what can I do for you?
    sudoku /home/ws/pranav/sudoku_input
    3 1 6 5 2 8 4 9 7
    5 2 1 3 4 7 8 6 9
    2 8 7 6 5 4 9 3 1
    6 4 3 9 1 5 7 8 2
    9 7 2 8 6 3 1 4 5
    7 5 8 4 9 1 6 2 3
    1 3 4 7 8 9 2 5 6
    8 6 9 1 3 2 5 7 4
    4 9 5 2 7 6 3 1 8

    """
    def __call__(self, jarvis, sudoku):
        self.sudoku = []
        with open(sudoku, 'r') as fp:
            data = fp.readlines()
        for line in data:
            self.sudoku.append([int(i) for i in line.split(" ")])
        self.row = len(self.sudoku)
        self.col = len(self.sudoku[0])
        if self.solve():
            self.print_solution()
        else:
            print("Failed to complete the sudoku")

    def solve(self, row=0, col=0):
        # If reached last row's last col, complete the process
        if row == self.row - 1 and col == self.col:
            return True
        # If current row's last col reached, proceed with next row
        if col == self.col:
            row += 1
            col = 0

        # If the current position has a value other than `0`, proceed to next
        if self.sudoku[row][col] > 0:
            return self.solve(row, col + 1)

        for num in range(1, self.row + 1):
            # Check whether the current pos is valid with num
            if self._is_valid(row, col, num):
                self.sudoku[row][col] = num

                # Now that the current position is filled, verify it is
                # valid for complete col
                if self.solve(row, col + 1):
                    return True
            # Otherwise, keep it as 0
            self.sudoku[row][col] = 0
        return False

    def print_solution(self):
        # Print the solution identified
        for i in range(0, self.row):
            for j in range(0, self.col):
                print(self.sudoku[i][j], end=" ")
            print("\n")

    def _is_valid(self, row, col, num):
        """
        At a given point of time, validate the given combination for the
        specified row and col
        """
        # Check across the row
        for i in range(0, self.row):
            if self.sudoku[row][i] == num:
                return False

        # Check across column
        for i in range(0, self.col):
            if self.sudoku[i][col] == num:
                return False

        # If not found, return True
        return True
