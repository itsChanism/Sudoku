import tkinter as tk
from tkinter import messagebox

# --- Sudoku Solver Core ---
import itertools

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    return [a + b for a in A for b in B]

squares = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
units = { s: [u for u in unitlist if s in u] for s in squares }
peers = { s: set(sum(units[s], [])) - {s} for s in squares }

def parse_grid(grid):
    values = { s: '123456789' for s in squares }
    grid = grid.replace('0', '.').replace(' ', '').replace('\n', '')
    if len(grid) != 81:
        raise ValueError("Input grid must be 81 characters.")
    for s, d in zip(squares, grid):
        if d in '123456789' and not assign(values, s, d):
            return False
    return values

def assign(values, s, d):
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False

def eliminate(values, s, d):
    if d not in values[s]:
        return values
    values[s] = values[s].replace(d, '')
    if len(values[s]) == 0:
        return False
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False
        elif len(dplaces) == 1:
            if not assign(values, dplaces[0], d):
                return False
    return values

def solve(grid):
    return search(parse_grid(grid))

def search(values):
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in squares):
        return values
    _, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d)) for d in values[s])

def some(seq):
    for e in seq:
        if e: return e
    return False

# --- UI ---
def display_solution(values):
    if not values:
        messagebox.showerror("Error", "Invalid puzzle or no solution.")
        return
    for i, s in enumerate(squares):
        val = values[s]
        entries[i].delete(0, tk.END)
        entries[i].insert(0, val if len(val) == 1 else '.')

def on_solve():
    grid = ''.join(entry.get() or '.' for entry in entries)
    try:
        result = solve(grid)
        display_solution(result)
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Sudoku Solver")
entries = []

for r in range(9):
    for c in range(9):
        e = tk.Entry(root, width=2, font=('Arial', 18), justify='center')
        e.grid(row=r, column=c, padx=2, pady=2)
        entries.append(e)

tk.Button(root, text="Solve", command=on_solve, font=('Arial', 14)).grid(row=9, column=0, columnspan=9, pady=10)
root.mainloop()
