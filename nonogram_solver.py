"""A class for solving nonograms by domain reduction.

    Author: Drew Hughlett

    Typical usage example:

    solver = NonogramSolver('filename')
    solver.solve()
    solver.print_board()
"""

import time
import sys
import os
import psutil
import numpy as np
from ast import literal_eval


class NonogramSolver:
    """Nonogram solving class

    Attributes:
        row_domains: A list of all domain values for rows.
        col_domains: A list of all domain values for columns.
        known_rows: A set of indexes of known rows.
        known_cols: A set of indexes of known columns.
        known_intersects: A set of tuples of known intersections.
        size: The number of rows/columns.
        rows: A list of arrays of row values.
        cols: A list of array of column values.
        is_searching_rows: A boolean indicating if the solver is currently searching rows or columns.
    """

    def __init__(self, filename) -> None:
        """Inits Nonogram solver with size, rows, and columns, and is_searching_rows to True."""
        self.row_domains, self.col_domains = list(), list()
        self.known_rows, self.known_cols, self.known_intersects = set(), set(), set()
        self.size, self.rows, self.cols = self.read_file(filename)
        self.is_searching_rows = True

    def generateDomainHelper(self, nums, domain, row, last_start, last_num, index, sum):
        """Recursively generates domain values for nums

        Args:
            nums: list of all cell groups.
            domain: list of all possible domain values for the given row/column.
            row: domain value for nums.
            last_start: the starting index of the last group of cells.
            last_num: the amount of cells in the last group of cells.
            index: the index of the current number in nums.
            sum: the sum of the numbers left to process in nums.

        Returns:
            A list of arrays that represent the possible domain values for nums.
        """
        if sum == 0:
            return domain.append(row)
        sum -= nums[index]

        # Calculate the first index that the number could start with
        start = 0 if last_start == -1 else last_start + last_num + 1

        # Calculate the last index that the number could start with
        end = self.size - sum - len(nums) + index - nums[index] + 2
        if start == end:
            end += 1

        # Create all possible row configurations given the current number
        # and the range of valid cells that it can possess, then recurse
        for i in range(start, end):
            row_copy = row.copy()
            for j in range(nums[index]):
                row_copy[i + j] = True
            self.generateDomainHelper(nums, domain, row_copy,
                                      i, nums[index], index + 1, sum)

    def generateDomain(self, nums):
        """Generates domain values for nums.

        Args:
            nums: list of all cell groups.

        Returns:
            A list of arrays that represent the possible domain values for nums.
        """
        domain = list()
        self.generateDomainHelper(nums, domain, np.full(
            self.size, False), -1, -1, 0, np.sum(nums))
        return domain

    def reduceNeighborDomains(self, known_domain, unknown_domains, index):
        """Reduces a list of domains given a known neighboring domain.

        Args:
            known_domain: a domain that is known and neighbors all domains in unknown_domains.
            unknown_domains: a list of unknown domains that neighbors known_domain.
            index: the index of known_domain from the list of domains that it came from.
        """
        for i, value in enumerate(known_domain):
            if not value and len(unknown_domains[i]) > 1 and (self.is_searching_rows, index, i) not in self.known_intersects:
                for j, domain in reversed(list(enumerate(unknown_domains[i]))):
                    if domain[index]:
                        del unknown_domains[i][j]

    def reduceDomain(self, domain, index, value):
        """Reduces a domain given a known index and value within that domain.

        From the domain values in domain, removes all domain values whose value
        at index is not equal to value.

        Args:
            domain: a list of domain values.
            index: the index of the known value.
            value: the value of the known index.
        """
        if len(domain) == 1:
            return
        for i in reversed(range(len(domain))):
            if domain[i][index] != value:
                del domain[i]

    def getDomainIntersects(self, domain, index):
        """Returns a list of intersections/known values within a domain.

        Args:
            domain: the domain to search through.
            index: the index of domain from the list of domains that it came from.

        Returns:
            A list of tuples where each tuple contains the index and value
            of a known index and value in domain.
        """
        intersects = list()
        for i in range(len(domain[0])):
            if (self.is_searching_rows, index, i) not in self.known_intersects:
                all_true = all_false = True
                for j in domain:
                    if not all_true and not all_false:
                        break
                    if not j[i]:
                        all_true = False
                    else:
                        all_false = False
                if all_true:
                    intersects.append((i, True))
                if all_false:
                    intersects.append((i, False))
        return intersects

    def reduceDomains(self, domains_a, known_domains_a, domains_b):
        """Reduces a domain given the domain's neighboring domains.

        Args:
            domains_a: a list of domain values
            known_domains_a: a list of known domains for domains_a
            domains_b: a list of domain values
        """
        for i, domain in enumerate(domains_a):
            if i not in known_domains_a:
                if len(domain) == 1:
                    self.reduceNeighborDomains(domain[0], domains_b, i)
                    known_domains_a.add(i)

                intersects = self.getDomainIntersects(domain, i)
                for intersect in intersects:
                    self.reduceDomain(
                        domains_b[intersect[0]], i, intersect[1])
                    self.known_intersects.add(
                        (self.is_searching_rows, i, intersect[0]))

    def solve(self):
        """Solves a nonogram.

        First, domains are generated given a list of row and column values.
        Domains are then reduced by process of elimination by finding
        intersections/known values in a row or column domain and
        removing neighboring domains who do not possess the known value.
        """
        for row in self.rows:
            self.row_domains.append(self.generateDomain(row))
        for col in self.cols:
            self.col_domains.append(self.generateDomain(col))

        while len(self.known_rows) != self.size and len(self.known_cols) != self.size:
            self.reduceDomains(
                self.row_domains, self.known_rows, self.col_domains)
            self.is_searching_rows = not self.is_searching_rows
            if len(self.known_rows) != self.size:
                self.reduceDomains(
                    self.col_domains, self.known_cols, self.row_domains)
                self.is_searching_rows = not self.is_searching_rows
        return

    def read_file(self, filename):
        """Reads a nonogram file.

        Args:
            filename: the name of the file to read.

        Returns:
            The size of the puzzle and the row and column values as arrays.
        """
        try:
            with open(filename, 'r') as f:
                return literal_eval(f.readline()), literal_eval(f.readline()), literal_eval(f.readline())
        except IOError as e:
            print("Cannot open file " + str(filename) + ".")
            sys.exit()

    def print_board(self):
        """Prints the solved nonogram.

        Prints an ASCII representation of the solved nonogram, or
        prints an error message if the nonogram has not been solved yet.
        """
        solved_domains = None
        rows = False
        if len(self.known_rows) == self.size:
            solved_domains = self.row_domains
            rows = True
        elif len(self.known_cols) == self.size:
            solved_domains = self.col_domains
        else:
            return print("Solve the puzzle first!")

        for i in range(len(solved_domains)):
            for j in range(len(solved_domains)):
                if (rows and solved_domains[i][0][j]) or (not rows and solved_domains[j][0][i]):
                    print('▯', end='')
                else:
                    print('▮', end='')
            print()


def main():
    if len(sys.argv) != 2:
        print("Someone didn't read the documentation...")
        print("Usage: python3 ./nonogram_solver.py ./test-inputs/input_25_03.txt")
        sys.exit()

    process = psutil.Process(os.getpid())
    solver = NonogramSolver(sys.argv[1])
    now = time.time()
    solver.solve()
    total_time = time.time() - now
    print(f"Time to solve: {total_time:.6f} seconds")
    print(f"Total memory used: {process.memory_info().rss} bytes")
    solver.print_board()


if __name__ == "__main__":
    main()
