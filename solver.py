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
            if surrounding_count(proposed_sol, (row, col), 1) != int(user_grid[row][col]):
                return False
    return True


def surrounding_set(grid, index):
    surrounding = set()
    upper = max([0, index[0] - 1])
    lower = min([len(grid) - 1, index[0] + 1])
    left = max([0, index[1] - 1])
    right = min([len(grid[0]) - 1, index[1] + 1])
    for row in range(upper, lower + 1):
        for col in range(left, right + 1):
            if row == index[0] and col == index[1]:
                continue
            surrounding.add((row, col))
    return surrounding


def set_count(grid, set, key):
    count = 0
    for index in set:
        if grid[index[0]][index[1]] == key:
            count += 1
    return count


def surrounding_count(grid, index, key):
    neighbor_set = surrounding_set(grid, index)
    return set_count(grid, neighbor_set, key)


def deduce(user_grid, mines_left, first_click):
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

    # One cell deduction
    for row in range(height):
        for col in range(width):
            if user_grid[row][col] in ["F", "H", "O"]:
                continue
            action_queue.update(
                single_cell_deduction_helper((row, col), user_grid, surrounding_set(user_grid, (row, col))))

    # Two cells deduction
    for row in range(height):
        for col in range(width):
            if user_grid[row][col] in ["F", "H", "0"]:
                continue
            left_index = (row, col)
            left_set = surrounding_set(user_grid, left_index)
            left_number = int(user_grid[left_index[0]][left_index[1]])
            pairing_cells = [(row, col + 1), (row + 1, col), (row + 1, col + 1), (row + 2, col), (row, col + 2)]
            pairing_cells = [index for index in pairing_cells if index in left_set]
            for right_index in pairing_cells:
                if user_grid[right_index[0]][right_index[1]] in ["F", "H", "0"]:
                    continue
                right_set = surrounding_set(user_grid, right_index)
                right_number = int(user_grid[right_index[0]][right_index[1]])
                intersection_set = left_set.intersection(right_set)
                left_diff_set = left_set - right_set
                right_diff_set = right_set - left_set
                intersection_at_most = min([left_number, right_number,
                                            (set_count(user_grid, intersection_set, "H") + set_count(user_grid, intersection_set, "F"))])
                left_diff_at_least = left_number - intersection_at_most
                left_diff_at_most = set_count(user_grid, left_diff_set, "H") + set_count(user_grid, left_diff_set, "F")
                right_diff_at_least = right_number - intersection_at_most
                right_diff_at_most = set_count(user_grid, right_diff_set, "H") + \
                                     set_count(user_grid, right_diff_set, "F")

                if left_diff_at_most == left_diff_at_least:
                    first_group = (left_number, left_diff_at_most, left_diff_set)
                    second_group = (right_number, right_diff_set)
                    action_queue.update(
                        two_cells_deduction_helper(first_group, second_group, user_grid, intersection_set))

                if right_diff_at_most == right_diff_at_least:
                    first_group = (right_number, right_diff_at_most, right_diff_set)
                    second_group = (left_number, left_diff_set)
                    action_queue.update(
                        two_cells_deduction_helper(first_group, second_group, user_grid, intersection_set))

    if len(action_queue) > 0:
        # print("Deduction")
        return action_queue

    # This part is the last resort, check threshold, if exceed, went for a random guess
    total_combinations = math.comb(len(possible_loc), mines_left)
    if total_combinations > 10000:
        random_loc = rd.choice(list(possible_loc))
        action = SolverAction(divmod(random_loc, width), False)
        action_queue.add(action)
        # print("Random Guess")
        return action_queue

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
        elif pair[1] == valid_combination and valid_combination > 0:
            action = SolverAction(divmod(pair[0], width), True)
            action_queue.add(action)
    # If queue is still empty, then click on the single best option
    if len(action_queue) == 0:
        min_index = min(list(possible_loc), key=lambda k: mine_dict.get(k, 0))
        action = SolverAction(divmod(min_index, width), False)
        action_queue.add(action)
    # Return queue
    # print("Probability")
    return action_queue


def single_cell_deduction_helper(index, grid, relevant_set):
    set_of_found_moves = set()
    # If current number same as surrounding hidden cell plus surrounding flags, flag all surrounding
    if int(grid[index[0]][index[1]]) == set_count(grid, relevant_set, "H") + set_count(grid, relevant_set, "F"):
        for location in relevant_set:
            if grid[location[0]][location[1]] == "H":
                action = SolverAction(location, True)
                set_of_found_moves.add(action)
    # If current number is the same number as surrounding flags, click the hidden one
    if int(grid[index[0]][index[1]]) == set_count(grid, relevant_set, "F"):
        for location in relevant_set:
            if grid[location[0]][location[1]] == "H":
                action = SolverAction(location, False)
                set_of_found_moves.add(action)
    return set_of_found_moves


def two_cells_deduction_helper(first_group, second_group, grid, intersection_set):
    set_of_found_moves = set()
    for index in first_group[2]:
        if grid[index[0]][index[1]] == "H":
            action = SolverAction(index, True)
            set_of_found_moves.add(action)
    intersection_actual = first_group[0] - first_group[1]
    if intersection_actual == set_count(grid, intersection_set, "H") + \
            set_count(grid, intersection_set, "F"):
        for index in intersection_set:
            if grid[index[0]][index[1]] == "H":
                action = SolverAction(index, True)
                set_of_found_moves.add(action)
    right_diff_actual = second_group[0] - intersection_actual
    if right_diff_actual == set_count(grid, second_group[1], "H") + \
            set_count(grid, second_group[1], "F"):
        for index in second_group[1]:
            if grid[index[0]][index[1]] == "H":
                action = SolverAction(index, True)
                set_of_found_moves.add(action)
    if right_diff_actual == set_count(grid, second_group[1], "F"):
        for index in second_group[1]:
            if grid[index[0]][index[1]] == "H":
                action = SolverAction(index, False)
                set_of_found_moves.add(action)
    return set_of_found_moves


def solver_func(current_view):
    return deduce(current_view.board_view, current_view.bombs_unflagged, current_view.first_click)
