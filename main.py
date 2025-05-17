#jiamu Tang
#jtang41
#csc242

import itertools
import sys

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]

squares = cross(rows, cols)

#all units: rows, columns, and 3x3 boxes.
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
#square- list of units it belongs to.
units = { s: [u for u in unitlist if s in u] for s in squares }
#square- the set of peer squares.
peers = { s: set(sum(units[s], [])) - {s} for s in squares }

def parse_grid(grid):
    """
    Convert grid into a dict of possible values {square: digits}. Raises ValueError if grid length is not 81.
    """
    values = { s: '123456789' for s in squares }
    grid = grid.replace('0', '.').replace(' ', '').replace('\n', '')
    if len(grid) != 81:
        raise ValueError("Input grid must be 81 characters long.")
    for s, d in zip(squares, grid):
        if d in '123456789':
            if not assign(values, s, d):
                return False
    return values

def assign(values, s, d):
    """
    get rid of all other digits from values[s] except d and propagate.
    return the updated values or False if a contradiction is detected.
    """
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    return False

def eliminate(values, s, d):
    """
    Eliminate digit d from values and propagate constraints.
    """
    if d not in values[s]:
        return values  # already eliminated
    values[s] = values[s].replace(d, '')
    if len(values[s]) == 0:
        return False  # Contradiction: no values left
    if len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, peer, d2) for peer in peers[s]):
            return False
    for u in units[s]:
        dplaces = [sq for sq in u if d in values[sq]]
        if len(dplaces) == 0:
            return False  # Contradiction: no place for d
        elif len(dplaces) == 1:
            if not assign(values, dplaces[0], d):
                return False
    return values

def only_choice(values):
    "Finalize squares where a digit can only go in one place in a unit."
    for u in unitlist:
        for d in '123456789':
            dplaces = [s for s in u if d in values[s]]
            if len(dplaces) == 1:
                if not assign(values, dplaces[0], d):
                    return False
    return values


# implement ddvanced techniques such as naked pair and x wings for sudoku 

def naked_pairs(values):
    """
    In any unit, if exactly two squares share the same two candidates,
    remove those digits from the other squares in that unit.
    """
    for u in unitlist:
        two_candidate_squares = [s for s in u if len(values[s]) == 2]
        pairs = {}
        for s in two_candidate_squares:
            pair = values[s]
            pairs.setdefault(pair, []).append(s)
        for pair, squares_with_pair in pairs.items():
            if len(squares_with_pair) == 2:
                for s in u:
                    if s not in squares_with_pair:
                        for d in pair:
                            if d in values[s]:
                                values[s] = values[s].replace(d, '')
                                if len(values[s]) == 0:
                                    return False
                                # propagate if reduced to a singleton.
                                if len(values[s]) == 1:
                                    if not assign(values, s, values[s]):
                                        return False
    return values

def hidden_pairs(values):
    """
    For each unit, if a pair of digits appears only in the same two squares,
    restrict those squares to just that pair.
    """
    for u in unitlist:
        for d1, d2 in itertools.combinations('123456789', 2):
            cells = [s for s in u if d1 in values[s] or d2 in values[s]]
            if len(cells) == 2:
                #check that both digits appear in both cells
                if all(d in values[s] for s in cells for d in (d1, d2)):
                    for s in cells:
                        new_val = ''.join([d for d in values[s] if d in (d1 + d2)])
                        if new_val != values[s]:
                            values[s] = new_val
                            if len(values[s]) == 0:
                                return False
                            if len(values[s]) == 1:
                                if not assign(values, s, values[s]):
                                    return False
    return values

def x_wing(values):
    """
    X-wing for each candidate digit.
    """
    # X-wing for rows
    for d in '123456789':
        row_candidates = {}
        for r in rows:
            cols_with_d = [c for c in cols if d in values[r+c]]
            if len(cols_with_d) == 2:
                row_candidates[r] = cols_with_d
        for r1, r2 in itertools.combinations(row_candidates.keys(), 2):
            if row_candidates[r1] == row_candidates[r2]:
                cols_pair = row_candidates[r1]
                for r in rows:
                    if r != r1 and r != r2:
                        for c in cols_pair:
                            cell = r + c
                            if d in values[cell]:
                                values[cell] = values[cell].replace(d, '')
                                if len(values[cell]) == 0:
                                    return False
                                if len(values[cell]) == 1:
                                    if not assign(values, cell, values[cell]):
                                        return False
    # X-wing for columns
    for d in '123456789':
        col_candidates = {}
        for c in cols:
            rows_with_d = [r for r in rows if d in values[r+c]]
            if len(rows_with_d) == 2:
                col_candidates[c] = rows_with_d
        for c1, c2 in itertools.combinations(col_candidates.keys(), 2):
            if col_candidates[c1] == col_candidates[c2]:
                rows_pair = col_candidates[c1]
                for c in cols:
                    if c != c1 and c != c2:
                        for r in rows_pair:
                            cell = r + c
                            if d in values[cell]:
                                values[cell] = values[cell].replace(d, '')
                                if len(values[cell]) == 0:
                                    return False
                                if len(values[cell]) == 1:
                                    if not assign(values, cell, values[cell]):
                                        return False
    return values

def reduce_puzzle(values):
#iteratively apply strategies until no further progress is made
    stalled = False
    while not stalled:
        solved_before = len([s for s in squares if len(values[s]) == 1])
        values = only_choice(values)
        if not values:
            return False
        values = naked_pairs(values)
        if not values:
            return False
        values = hidden_pairs(values)
        if not values:
            return False
        values = x_wing(values)
        if not values:
            return False
        solved_after = len([s for s in squares if len(values[s]) == 1])
        stalled = (solved_before == solved_after)
        if any(len(values[s]) == 0 for s in squares):
            return False
    return values


#  Backtracking search

def search(values):
    "Using depth-first search and constraint propagation, try all possible assignments."
    values = reduce_puzzle(values)
    if values is False:
        return False  # Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values  # Solved!
    n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    for d in values[s]:
        new_values = values.copy()
        attempt = assign(new_values, s, d)
        if attempt:
            result = search(attempt)
            if result:
                return result
    return False

def solve(grid):
    """
    Solve a Sudoku puzzle given as a string of 81 characters.
    Returns a dictionary of the solved puzzle {square: digit} or False if unsolvable.
    """
    return search(parse_grid(grid))

# Main I/O: Read Puzzle from Standard Input and Output the Solution

def main():
    # Read exactly 9 lines from standard input
    puzzle_lines = []
    for _ in range(9):
        line = sys.stdin.readline().strip()
        if not line:
            print("Invalid input: Expected 9 lines of input.")
            return
        tokens = line.split()
        if len(tokens) != 9:
            print("Invalid input: Each line must contain 9 space-separated tokens.")
            return
        puzzle_lines.append("".join(tokens))
    puzzle = "".join(puzzle_lines)
    
    try:
        solution = solve(puzzle)
    except Exception as e:
        print("Error solving the puzzle:", e)
        return

    if solution:
        for r in rows:
            print(" ".join(solution[r+c] for c in cols))
    else:
        print("No solution.")

if __name__ == '__main__':
    main()
