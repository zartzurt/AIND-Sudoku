
import logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.ERROR)

assignments = []

from utils import *


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def filter_tupes(tuple, tuple_size):
    """
    Filter groups by tuple size. If tuple size is None do not filter.
    """
    if tuple_size and tuple_size != len(tuple):
        return False
    return True


def naked_locked_choices(values, tuple_size=None):
    """
    Abstraction of naked_twins to eliminate tuples of any size

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
        tuple_size(int): eliminate groups of only certain tuple_size. tuple_size=1 does not change anything,
            tuple_size=2 is same as naked_twins. A value of None means eliminate all posible naked locked choices.

    Returns:
        the values dictionary with the naked twins eliminated from peers.

    Algorithm:
        for each unit try to find naked twin boxes and eliminate the values of twins from remaning unit boxes
    """
    logging.debug('<naked_locked_choices twin searching units>')
    from collections import Counter
    for unit in unitlist:
        logging.debug('\tsearching unit:%s' %
                      {box: values[box] for box in unit})
        # count every occurance of a value filter by tuple count
        naked_occurrence = Counter([values[box]
                                    for box in unit if len(values[box]) > 1 if filter_tupes(values[box], tuple_size)])
        # if lenght of value and number of occurances of a value is same we
        # find naked locked choices
        locked_coices = [
            value for value, count in naked_occurrence.items() if len(value) == count]
        if len(locked_coices) > 0:
            logging.debug('\t\tfound locked coices:%s' % locked_coices)
        # for each naked locked choice remove digits from all other unit boxes
        for locked_choice in locked_coices:
            logging.debug('\t\tbefore elimination:%s' %
                          {box: values[box] for box in unit})
            digits_to_eliminate = str.maketrans('', '', locked_choice)
            for box in unit:
                if values[box] != locked_choice:
                    assign_value(values, box, values[
                        box].translate(digits_to_eliminate))
            logging.debug('\t\tafter elimination:%s' %
                          {box: values[box] for box in unit})
    return values


def hidden_locked_choices(values, tuple_size=None):
    """
    Abstraction of hidden_twins to eliminate tuples of any size

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
        tuple_size(int): eliminate groups of only certain tuple_size. tuple_size=1 is same as only_choice. 
            tuple_size=2 is same as hidden_twins. A value of None means eliminate all posible hidden locked choices.
    Returns:
        the values dictionary locked choice elimination.

    Algorithm:
        For each box in unit reverse the value dictionary to find every mapping of digit -> box
        Merge same digits to form digit -> [box] mappings
        Group all mappings by [box]
        For each group if the boxes of a digit mapped to and group size is same we found a hidden locked choice
            lock choices to group and eliminate options from other peers
    """
    from collections import defaultdict
    from itertools import groupby
    logging.debug(
        '<hidden_locked_choices tuple_size:%s searching units>' % tuple_size)
    for unit in unitlist:
        logging.debug('\tsearching unit:%s' %
                      {box: values[box] for box in unit})
        digit_to_boxes = defaultdict(list)
        # For each unit box reverse the value dictionary to find every mapping of digit -> box
        # Merge same digits to form digit -> [box] mappings
        for digit, box in [(digit, box) for box in unit for digit in values[box]]:
            digit_to_boxes[digit].append(box)

        # Group all mappings by [box]
        sort_by_boxes = lambda t: t[1]
        digit_to_boxes_list = sorted([(digit, boxes) for digit, boxes in digit_to_boxes.items() if filter_tupes(boxes, tuple_size)],
                                     key=sort_by_boxes)
        # for each group
        for g_boxes, g in groupby(digit_to_boxes_list, sort_by_boxes):
            g_list = list(g)
            # If number of boxes a digit mapped to and group size is same we
            # found a hidden locked choice
            if(len(g_list) == len(g_boxes)):
                logging.debug('\t\tbefore elimination:%s' %
                              {box: values[box] for box in unit})
                locked_choice = ''.join([g[0] for g in g_list])
                digits_to_eliminate = str.maketrans('', '', locked_choice)
                logging.debug('\t\tfound group_boxes:%s, locked_choice:%s' % (
                    g_boxes, locked_choice))
                # lock choices to group and eliminate options from other
                # peers
                for box in unit:
                    if box in g_boxes:
                        assign_value(values, box, locked_choice)
                    else:
                        assign_value(
                            values, box, values[box].translate(digits_to_eliminate))
                logging.debug('\t\tafter elimination:%s' %
                              {box: values[box] for box in unit})
    return values


def naked_twins(values):
    """
    Eliminate values using the naked twins strategy.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.

    Algorithm:
        for each unit try to find naked twin boxes and eliminate the values of twins from remaning unit boxes
    """
    logging.debug('<naked twin searching units>')
    from collections import Counter
    for unit in unitlist:
        logging.debug('\tsearching unit:%s' %
                      {box: values[box] for box in unit})
        # get count of each unique solution with size 2
        two_option_values = Counter([values[box]
                                     for box in unit if len(values[box]) == 2])
        # if there is more than one occurence of the solution, it is a naked
        # twin.
        naked_twins = [
            value for value, count in two_option_values.items() if count == 2]
        if len(naked_twins) > 0:
            logging.debug('\t\tfound naked_twins:%s' % naked_twins)
        # for each naked twin remove digits from all other unit boxes
        for naked_twin in naked_twins:
            logging.debug('\t\tbefore elimination:%s' %
                          {box: values[box] for box in unit})
            digits_to_eliminate = str.maketrans('', '', naked_twin)
            for box in unit:
                if values[box] != naked_twin:
                    assign_value(values, box, values[
                        box].translate(digits_to_eliminate))
            logging.debug('\t\tafter elimination:%s' %
                          {box: values[box] for box in unit})
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    sudoku = dict(zip(boxes, grid))
    for box, value in sudoku.items():
        if value == '.':
            sudoku[box] = '123456789'
    return sudoku


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    return


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    logging.debug('<eliminate>')
    single_value_boxes = {
        box: value for box, value in values.items() if len(value) == 1}
    for box, value in single_value_boxes.items():
        logging.debug('\tbefore eliminating value:%s from peers:%s' %
                      (value, {peer_box: values[peer_box] for peer_box in peers[box]}))
        for peer_box in peers[box]:
            assign_value(values, peer_box, values[peer_box].replace(value, ''))
        logging.debug('\tafter elimination:%s' %
                      {peer_box: values[peer_box] for peer_box in peers[box]})
    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    new_values = values
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(new_values, dplaces[0], digit)
    return new_values


def reduce_puzzle(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len(
            [box for box in values.keys() if len(values[box]) == 1])
        eliminate(values)
        only_choice(values)
        naked_twins(values)
        hidden_locked_choices(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len(
            [box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available
        # values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        return None
    if all(len(values[box]) == 1 for box in boxes):
        return values  # Solved!

    count, box = min((len(values[box]), box)
                     for box in boxes if len(values[box]) > 1)
    for value in values[box]:
        assign_value(values, box, value)
        result = search(values.copy())
        if result:
            return result
    return None


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print(
            'We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
