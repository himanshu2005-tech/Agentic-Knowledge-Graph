# Auto-generated Code Vault for 'NQueensSolver' [Python]

class NQueensSolver:
    def __init__(self, n=8):
        """
        Initialize the NQueensSolver with a board size of n x n.
        
        Args:
            n (int): The size of the chessboard. Defaults to 8.
        """
        self.n = n
        self.board = [['.' for _ in range(n)] for _ in range(n)]

    def is_safe(self, row, col):
        """
        Check if it is safe to place a queen at the given position on the board.
        
        Args:
            row (int): The row index of the position.
            col (int): The column index of the position.
        
        Returns:
            bool: True if it is safe to place a queen, False otherwise.
        """
        # Check this row on left side
        for i in range(col):
            if self.board[row][i] == 'Q':
                return False

        # Check upper diagonal on left side
        for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
            if self.board[i][j] == 'Q':
                return False

        # Check lower diagonal on left side
        for i, j in zip(range(row, self.n, 1), range(col, -1, -1)):
            if self.board[i][j] == 'Q':
                return False

        return True

    def solve_n_queens(self, col):
        """
        Solve the N-Queens problem using a recursive backtracking algorithm.
        
        Args:
            col (int): The current column index.
        
        Returns:
            bool: True if a solution is found, False otherwise.
        """
        # base case: If all queens are placed then return true
        if col >= self.n:
            return True

        # Consider this column and try placing this queen in all rows one by one
        for i in range(self.n):
            if self.is_safe(i, col):
                # Place this queen in board[i][col]
                self.board[i][col] = 'Q'

                # recur to place rest of the queens
                if self.solve_n_queens(col + 1) == True:
                    return True

                # If placing queen in board[i][col] doesn't lead to a solution then
                # remove queen from board[i][col]
                self.board[i][col] = '.'

        # If the queen cannot be placed in any row in this column col then return false
        return False

    def print_board(self):
        """
        Print the current state of the board.
        """
        for row in self.board:
            print(' '.join(row))


def main():
    solver = NQueensSolver()
    if solver.solve_n_queens(0):
        solver.print_board()
    else:
        print("Solution does not exist")


if __name__ == "__main__":
    main()
