# Nonogram Solver

## What is a nonogram?

A nonogram is a grid based puzzle game where the goal is to fill in the correct tiles to reveal a picture. Nonograms designed for human players can be solved without any guessing using only logic, but there do exist some maliciously designed puzzles that require the player to guess-and-check in order to solve the puzzle.

The player begins the game with an empty grid with no known tiles. Each row and column has an ordered list of numbers representing how many clusters of filled tiles are in each row or column and in what order. For example, if a row has the list of numbers (2, 3) we know that somewhere in the row there is a cluster of two tiles followed by a cluster of three tiles. The only other rule is that two clusters must have at least one empty space between them so that they cannot be touching.

### Example of a monogram before and after being solved

![Example of a monogram before and after being solved](/media/nonogram-before-after.png)

### Example of a nonogram being solved by a human player

![Example of a nonogram being solved by a human player](/media/nonogram-solving.gif)

## The solution approach

### High-level overview

The technique begins by first generating all possible domains for each row and column. For a row with a size of 5 and the values of [2, 1] the domain values would be:

- [▮▮▯▮▯]
- [▮▮▯▯▮]
- [▯▮▮▯▮]

Once all of the domains have been generated, we begin iterating over the row domains. For each row domain, we find the indexes where the value at the index is the same across every domain value and label that index as a domain intersection. Using the above example of the row with a size of 5 and the values of [2, 1], we can see that there is a domain intersection at index 1.

- [▮▮▯▮▯]
- [▮▮▯▯▮]
- [▯▮▮▯▮]

After we find every intersection in the row’s domain, we use these intersections/known values as constraints to reduce the domain of the corresponding column with the same index as the domain intersection. We call the column domain that has the same index as a domain intersection the neighboring domain. Continuing with the above example, the neighboring domain would be the domain for the column at index 1.

We then iterate over the domain values in the neighboring domain and remove any domain values whose value at the domain intersection does not match the known value. For example, if the domain values for the neighboring domain of the above example are:

- [▮▯▮▯▯]
- [▮▯▯▮▯]
- [▮▯▯▯▮]
- [▯▮▯▯▮]

We could now eliminate the first three domain values because the values at index 1 are not equal to the value at the domain intersection.

Lastly, when iterating over the row domains, if a row domain has a length of 1 (meaning that row has been solved), we can use the indexes and values of the cells that are not colored in as constraints to reduce the neighboring domains even further in the same way that we did above.

After we are done iterating over the row domains, we then iterate over the column domains and perform the same actions that we did with the row domains. The algorithm stops looping over these steps once either the rows or columns have been solved, as we only need one of them to be solved for the puzzle to be completed.

### Limitations

This approach has one limitation and that is it cannot solve nonograms that require guess-and-check to solve. However it is because of this limitation that allows the algorithm to function. Because we can assume that the puzzles do not require guess-and-check, we know that there will always be a domain intersection somewhere in the puzzle until it is solved.

## Using the program

### Input format

The program expects an input file with three lines of text.

1. The number of rows and columns the puzzle has.
2. An array of arrays where each array represents the values for each row.
3. An array of arrays where each array represents the values for each column.

### Steps to run nonogram_solver.py

1. `git clone https://github.com/drewrh/nonogram-solver.git`
2. `cd ./nonogram-solver`
3. `pip install -r requirements.txt`
4. `python3 ./nonogram_solver.py ./test-inputs/input_25_03.txt`

### Program output

The program prints the solved puzzle and the total time and memory it took to solve the puzzle.
