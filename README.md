# family_chess_tournament
Christmas 2016 I am competing with my brother and my mum to see who can produce the best chess AI

# rules
The AI will work by reading in a file called “game state.txt”
looking at the last game state then appending a new game state to the file.
The programs of the players will be run alternately.
The players are required to increment their timer by 2 minus the length of time it took them to move.

A player loses if:
    - they make an illegal move
    - their time remaining hits 0
    - their king is taken

Human players have no time limit on their moves as long as they are actively working on the game.
