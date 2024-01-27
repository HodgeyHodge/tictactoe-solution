import json



def idifier(grid):
    """Represent a grid as a unique id."""
    return sum(v*(3**k) for k, v in enumerate(grid))

def plyifier(grid):
    """Return how far the game has progressed by counting empty points in grid."""
    return 9 - sum(1 for g in grid if g == 0)

def canonifier(grid):
    """Given a grid, rotate and reflect to find its smallest id."""
    return min([
        idifier(grid),
        idifier([grid[0], grid[3], grid[6], grid[1], grid[4], grid[7], grid[2], grid[5], grid[8]]),
        idifier([grid[2], grid[1], grid[0], grid[5], grid[4], grid[3], grid[8], grid[7], grid[6]]),
        idifier([grid[6], grid[3], grid[0], grid[7], grid[4], grid[1], grid[8], grid[5], grid[2]]),
        idifier([grid[6], grid[7], grid[8], grid[3], grid[4], grid[5], grid[0], grid[1], grid[2]]),
        idifier([grid[2], grid[5], grid[8], grid[1], grid[4], grid[7], grid[0], grid[3], grid[6]]),
        idifier([grid[8], grid[7], grid[6], grid[5], grid[4], grid[3], grid[2], grid[1], grid[0]]),
        idifier([grid[8], grid[5], grid[2], grid[7], grid[4], grid[1], grid[6], grid[3], grid[0]])
    ])

def gridifier(id):
    """Given an id, turn it back into a grid."""
    out = []
    for j in range(0,9):
        out.append(id % 3)
        id = id // 3
    return out



class Position:
    def __init__(self, id, ancestors):
        self.id = id
        self.grid = gridifier(id)
        self.ply = plyifier(self.grid)
        self.ancestors = ancestors
        self.analysis = (set(), set(), set()) #W/D/L

    def __repr__(self):
        def ugly_string(grid):
            def glyph(cell):
                return "O" if cell == 1 else "X" if cell == 2 else "_"

            return f"{glyph(grid[0])}{glyph(grid[1])}{glyph(grid[2])}{glyph(grid[3])}{glyph(grid[4])}{glyph(grid[5])}{glyph(grid[6])}{glyph(grid[7])}{glyph(grid[8])}"

        return f"<Position id={self.id} ply={self.ply}, grid={ugly_string(self.grid)}, state={self.state()}, ancestors={self.ancestors}, analysis={self.analysis}>"

    def __lt__(self, other):
        return self.id < other.id

    def children(self):
        """A list of grids representing each possible next move for a given grid."""
        out = []
        if self.state() == "ongoing":
            for k, v in enumerate(self.grid):
                if v == 0:
                    child = self.grid[:]
                    child[k] = self._whoseMove()
                    out.append((k, child))
        return out

    def _whoseMove(self):
        """Since O=1 goes first, calculate who moves next from how many blank spaces remain."""
        return 2 - (sum(1 for g in self.grid if g == 0) % 2)

    def _parity(self):
        """Parity is how many of each glyph are on the grid.
        0: 5 O, 4 X (hence game is over)
        1: same number of each (hence O to move)
        2: one more O than X (hence X to move)
        -1: anything else (hence invalid grid)
        """
        p1 = sum(1 for g in self.grid if g == 1)
        p2 = sum(1 for g in self.grid if g == 2)
        if p1 == p2:
            return 1
        if p1 == p2 + 1:
            if p1 == 5:
                return 0
            else:
                return 2
        return -1

    def _hasWin(self, player):
        """Whether there is a winning three-in-a-row on the grid for the given player."""
        return (
            (self.grid[0] == player and self.grid[1] == player and self.grid[2] == player) or
            (self.grid[3] == player and self.grid[4] == player and self.grid[5] == player) or
            (self.grid[6] == player and self.grid[7] == player and self.grid[8] == player) or
            (self.grid[0] == player and self.grid[3] == player and self.grid[6] == player) or
            (self.grid[1] == player and self.grid[4] == player and self.grid[7] == player) or
            (self.grid[2] == player and self.grid[5] == player and self.grid[8] == player) or
            (self.grid[0] == player and self.grid[4] == player and self.grid[8] == player) or
            (self.grid[2] == player and self.grid[4] == player and self.grid[6] == player)
        )
    
    def state(self):
        """The state of the game, based on the parity plus looking for wins for both players."""
        parity = self._parity()
        if parity == -1:
            return "invalid"
        wins = int(self._hasWin(1)) + int(self._hasWin(2))
        if wins == 2:
            return "invalid"
        elif wins == 1:
            return "won"
        if parity == 0:
            return "drawn"
        return "ongoing"



def main():
    root = Position(0, set())
    almanac = {0: root}
    
    # build game tree forwards
    for i in range(0, 9):
        current_gen = set((v for v in almanac.values() if v.ply == i))
        for position in current_gen:
            for child in position.children():
                child_id = canonifier(child[1])
                if child_id in almanac.keys():
                    almanac[child_id].ancestors.add((position.id, child[0]))
                else:
                    almanac[child_id] = Position(child_id, set([(position.id, child[0])]))
    
    # populate analysis backwards
    for i in range(8, -1, -1):
        for p in (p for p in almanac.values() if p.ply == i):
            for child in (c for c in almanac.values() if c.ply == i + 1 and any(map(lambda x: x[0] == p.id, c.ancestors))):
                directions = [(a[1], child.id) for a in child.ancestors if a[0] == p.id]
                if child.state() == "won":
                    p.analysis[0].update(directions)
                elif child.state() == "drawn":
                    p.analysis[1].update(directions)
                else:
                    if not child.analysis[0]:
                        if not child.analysis[1]:
                            p.analysis[0].update(directions)
                        else:
                            p.analysis[1].update(directions)
                    else:
                        p.analysis[2].update(directions)

    output = {i: {p.id: {"w": dict(sorted(p.analysis[0])), "d": dict(sorted(p.analysis[1])), "l": dict(sorted(p.analysis[2]))} for p in sorted(almanac.values()) if p.ply == i} for i in range(0, 9)}

    with open('output/data.json', 'w') as f:
        json.dump(output, f)

    print("enjoy ~")



if __name__ == "__main__":
    main()
