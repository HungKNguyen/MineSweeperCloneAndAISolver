import itertools as itt
import math
import random as rd
from solver_components import SolverAction


def isValid(proposed_sol, user_grid):
    height = len(user_grid)
    width = len(user_grid[0])
    for row in range(height):
        for col in range(width):
            if user_grid[row][col] in ["F", "H"]:
                continue
            if str(surrounding_count(proposed_sol, (row, col), 1)) != user_grid[row][col]:
                return False
    return True


def surrounding_count(grid, index, key):
    count = 0
    upper = max([0, index[0] - 1])
    lower = min([len(grid) - 1, index[0] + 1])
    left = max([0, index[1] - 1])
    right = min([len(grid[0]) - 1, index[1] + 1])
    for row in range(upper, lower + 1):
        for col in range(left, right + 1):
            if row == index[0] and col == index[1]:
                continue
            if grid[row][col] == key:
                count += 1
    return count


# Require more complex solutions to solve more difficult mode
def deduct(user_grid, mines_left, first_click):
    # Queue to return
    action_queue = set()
    # Use user_grid to get current progress
    height = len(user_grid)
    width = len(user_grid[0])
    # Create list of places to place mines
    possible_loc = set(range(height * width))
    current_grid = []
    for row in range(height):
        row_list = []
        for col in range(width):
            if user_grid[row][col] == "F":
                row_list.append(1)
                possible_loc.remove(row * width + col)
                continue
            if user_grid[row][col] == "H":
                row_list.append(0)
                continue
            row_list.append(0)
            possible_loc.remove(row * width + col)
        current_grid.append(row_list)

    # If the current grid is never updated/new game, choose corner randomly
    if first_click:
        index = rd.choice([(0, 0), (0, width - 1), (height - 1, 0), (height - 1, width - 1)])
        action = SolverAction(index, flag=False)
        action_queue.add(action)
        # print("First click")
        return action_queue

    # If there is no mine undiscovered
    if mines_left == 0:
        for loc in possible_loc:
            index = divmod(loc, width)
            action = SolverAction(index, flag=False)
            action_queue.add(action)
        # print("Clean up")
        return action_queue

    for row in range(height):
        for col in range(width):
            if user_grid[row][col] in ["F", "H", "O"]:
                continue
            # If current number same as surrounding hidden cell plus surrounding flags, flag all surrounding
            if int(user_grid[row][col]) == surrounding_count(user_grid, (row, col), "H") + surrounding_count(
                    user_grid, (row, col), "F"):
                upper = max(row - 1, 0)
                lower = min(row + 1, height - 1)
                left = max(col - 1, 0)
                right = min(col + 1, width - 1)
                for index_row in range(upper, lower + 1):
                    for index_col in range(left, right + 1):
                        if index_row == row and index_col == col:
                            continue
                        if user_grid[index_row][index_col] == "H":
                            action = SolverAction((index_row, index_col), True)
                            action_queue.add(action)
                continue
            # If current number is the same number as surrounding flags, click the hidden one
            if int(user_grid[row][col]) == surrounding_count(user_grid, (row, col), "F"):
                upper = max(row - 1, 0)
                lower = min(row + 1, height - 1)
                left = max(col - 1, 0)
                right = min(col + 1, width - 1)
                for index_row in range(upper, lower + 1):
                    for index_col in range(left, right + 1):
                        if index_row == row and index_col == col:
                            continue
                        if user_grid[index_row][index_col] == "H":
                            action = SolverAction((index_row, index_col), False)
                            action_queue.add(action)
    if len(action_queue) > 0:
        # print("Deduction")
        return action_queue

    # This part is the last resort, check threshold, if exceed, went for a random guess
    total_combinations = math.comb(len(possible_loc), mines_left)
    if total_combinations > 100000:
        random_loc = rd.choice(list(possible_loc))
        action = SolverAction(divmod(random_loc, width), False)
        action_queue.add(action)
        # print("Random Guess")
        return list(action_queue)

    # Create combination of all possible arrangement of mines
    # print(total_combinations)
    possible_combinations = list(itt.combinations(possible_loc, mines_left))
    valid_combination = 0
    # Create a dictionary to keep scoring of each mines
    mine_dict = {}
    for combination in possible_combinations:
        # Create proposed solution given the combination
        proposed_grid = current_grid.copy()
        for index in combination:
            row_col = divmod(index, width)
            proposed_grid[row_col[0]][row_col[1]] = 1
        # Test proposed solution and update score
        if isValid(proposed_grid, user_grid):
            valid_combination += 1
            for index in combination:
                mine_dict[index] = mine_dict.get(index, 0) + 1
    # Extract key with 0 and max, append in queue
    for pair in mine_dict.items():
        if pair[1] == 0:
            action = SolverAction(divmod(pair[0], width), False)
            action_queue.add(action)
        elif pair[1] == valid_combination:
            action = SolverAction(divmod(pair[0], width), True)
            action_queue.add(action)
    # If queue is still empty, then click on the single best option
    if len(action_queue) == 0:
        min_index = min(list(possible_loc), key=lambda k: mine_dict.get(k, 0))
        action = SolverAction(divmod(min_index, width), False)
        action_queue.add(action)
    # Return queue
    # print("Probability")
    return list(action_queue)


def solver_func(current_view):
    return deduct(current_view.board_view, current_view.bombs_unflagged, current_view.first_click)
