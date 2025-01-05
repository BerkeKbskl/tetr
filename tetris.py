import random
import copy

score = 0
lines = 0
level = 1
wTile = 10
hTile = 20

speed = 0
lastTime = 0
lastLineCleared = 0
lineStreak = 0
isSoftLocked = False

gameArray = [[None] * 10 for _ in range(22)]
bag = []

currentTetro = None
nextTetro = None
heldTetro = None

tetrominos = [
    {"name": "i", "tl": [0, 0], "positions": [[0, 1], [1, 1], [2, 1], [3, 1]], "color": "cyan", "orientation": 0},
    {"name": "l", "tl": [0, 0], "positions": [[2, 0], [0, 1], [1, 1], [2, 1]], "color": "orange", "orientation": 0},
    {"name": "j", "tl": [0, 0], "positions": [[0, 0], [0, 1], [1, 1], [2, 1]], "color": "blue", "orientation": 0},
    {"name": "o", "tl": [0, 0], "positions": [[1, 0], [2, 0], [1, 1], [2, 1]], "color": "yellow", "orientation": 0},
    {"name": "z", "tl": [0, 0], "positions": [[0, 0], [1, 0], [1, 1], [2, 1]], "color": "red", "orientation": 0},
    {"name": "t", "tl": [0, 0], "positions": [[1, 0], [0, 1], [1, 1], [2, 1]], "color": "purple", "orientation": 0},
    {"name": "s", "tl": [0, 0], "positions": [[2, 0], [0, 1], [1, 1], [1, 0]], "color": "green", "orientation": 0}
]


def startGame():
    global isSoftLocked
    isSoftLocked = False
    resetSoftLock()
    popQueue()


def lock():
    global isSoftLocked, score
    occupiedCorners = 0
    if currentTetro["name"] == "t":
        if checkCollision(currentTetro, 0, 1) and checkCollision(currentTetro, 0, -1) and checkCollision(
                currentTetro, 1, 0) and checkCollision(currentTetro, -1, 0):
            occupiedCorners = 3

    resetSoftLock()
    isSoftLocked = False

    for i in range(0, len(currentTetro["positions"])):
        x, y = currentTetro["positions"][i]
        gameArray[y + currentTetro["tl"][1]][x + currentTetro["tl"][0]] = {"name": "standalone",
                                                                              "color": currentTetro["color"]}

    if not popQueue():
        return

    clearLine()
    resetSoftLock()

    if occupiedCorners >= 3:
        messageCh("T-Spin", 400 * level)
        score += 400 * level


def drop():
    global isSoftLocked
    if checkCollision(currentTetro, 0, 1):
        if not isSoftLocked:
            isSoftLocked = True
            soft = 1
    else:
        currentTetro["tl"][1] += 1
        resetSoftLock()


def moveRight():
    if not checkCollision(currentTetro, 1, 0):
        currentTetro["tl"][0] += 1
        resetSoftLock()


def moveLeft():
    if not checkCollision(currentTetro, -1, 0):
        currentTetro["tl"][0] -= 1
        resetSoftLock()


def clearLine():
    global score, lines, level, lastLineCleared
    clearedLineCount = 0
    linesToClear = []  # To store the indices of lines to clear

    # Check which lines need to be cleared
    for i in range(hTile):
        allBlock = all(gameArray[i][j] is not None for j in range(wTile))
        if allBlock:
            linesToClear.append(i)
            clearedLineCount += 1

    if linesToClear:
        # Handle clearing the lines and shifting the array
        for lineIndex in linesToClear:
            for j in range(wTile):
                gameArray[lineIndex][j] = None

            for i in range(lineIndex, 0, -1):
                for j in range(wTile):
                    gameArray[i][j] = gameArray[i - 1][j]

            for j in range(wTile):
                gameArray[0][j] = None

        updateGameParameters(clearedLineCount)
    else:
        lastLineCleared = 0


def updateGameParameters(clearedLineCount):
    global score, level, lines, lastLineCleared

    # Update score
    score += {1: 100, 2: 300, 3: 500, 4: 800}.get(clearedLineCount, 0) * level

    # Update level
    if (clearedLineCount + lines) // 10 != (level - 1):
        level += 1
        messageCh(f"Level Up! {level}", "")

    lines += clearedLineCount

    if lastLineCleared != 0:
        combo = 1
    else:
        combo = 0

    lastLineCleared = clearedLineCount

    # Update combo score
    if combo > 0:
        score += (combo + 1) * 50 * level
        messageCh(f"{combo + 1}x Combo!", (combo - 1) * 50 * level)


def messageCh(message, points):
    # Display message or update the UI
    pass


def dropButton():
    global isSoftLocked, score
    if isSoftLocked:
        resetSoftLock()
        hardDrop()
    else:
        drop()
        score += 1


def resetSoftLock():
    global isSoftLocked
    if isSoftLocked:
        isSoftLocked = False


def hardDrop():
    global score
    resetSoftLock()

    cells = 0
    while not checkCollision(currentTetro, 0, 1):
        currentTetro["tl"][1] += 1
        cells += 1

    lock()
    score += 2 * cells


def calcGhost(tetro):
    while not checkCollision(tetro, 0, 1):
        tetro["tl"][1] += 1


def holdTetro():
    global currentTetro, heldTetro
    resetSoftLock()

    if heldTetro is None:
        popQueue()
    else:
        currentTetro, heldTetro = heldTetro, currentTetro

    currentTetro["tl"] = overlayPosition()


def popQueue():
    global currentTetro, nextTetro, bag

    resetSoftLock()

    if len(bag) == 0:
        bag = tetrominos.copy()
        random.shuffle(bag)

    currentTetro = nextTetro
    nextTetro = bag.pop()

    # First iteration
    if currentTetro is None:
        currentTetro = nextTetro
        nextTetro = bag.pop()

    if checkCollision(currentTetro, 4, 0):
        endGame()
        return False
    else:
        currentTetro["tl"] = overlayPosition()

    return True


def overlayPosition():
    if currentTetro["name"] == "i":
        return [3, -1]
    return [3, 0]


def checkCollision(tetro, x, y):
    for position in tetro["positions"]:
        newX = position[0] + tetro["tl"][0] + x
        newY = position[1] + tetro["tl"][1] + y

        if (newY >= hTile or newX < 0 or newX >= wTile or
                (newY >= 0 and gameArray[newY][newX] is not None)):
            return True  # Collision with something other than a wall

    return False

wallKickData = {
                "0>>1": [[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]],
                "1>>0": [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
                "1>>2": [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
                "2>>1": [[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]],
                "2>>3": [[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]],
                "3>>2": [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
                "3>>0": [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
                "0>>3": [[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]],
            }

wallKickDataI = {
                "0>>1": [[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]],
                "1>>0": [[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]],
                "1>>2": [[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]],
                "2>>1": [[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]],
                "2>>3": [[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]],
                "3>>2": [[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]],
                "3>>0": [[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]],
                "0>>3": [[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]]
}

def rotate(mode="cw"):
    global currentTetro

    if currentTetro['name'] == "o":
        return

    # Save the current positions before rotating
    oldPos = copy.deepcopy(currentTetro['positions'])
    oldTl = copy.deepcopy(currentTetro['tl'])
    oldOrientation = currentTetro['orientation']

    # Rotate the tetromino points
    rotatePointsCw(mode)

    currentRotate = oldOrientation
    nextRotate = currentTetro['orientation']

    identifier = f"{currentRotate}>>{nextRotate}"
    # Wall kicks
    kickApplied = False

    # Redundant for 0...
    for i in range(5):
        if currentTetro['name'] == "i":
            kickX, kickY = wallKickDataI[identifier][i]
        else:
            kickX, kickY = wallKickData[identifier][i]

        if not checkCollision(currentTetro, kickX, kickY):
            currentTetro['tl'][0] += kickX
            currentTetro['tl'][1] += kickY
            kickApplied = True
            break

    if not kickApplied:
        # Revert to original position and orientation if no kicks work
        currentTetro['positions'] = oldPos
        currentTetro['tl'] = oldTl
        currentTetro['orientation'] = oldOrientation

    resetSoftLock()

def rotatePointsCw(mode):
    centerX, centerY = 0, 0

    if currentTetro['name'] in ["j", "l", "s", "z", "t"]:
        centerX, centerY = 1, 1
    elif currentTetro['name'] == "i":
        centerX, centerY = 1.5, 1.5

    for i in range(len(currentTetro['positions'])):
        x = currentTetro['positions'][i][0] - centerX
        y = currentTetro['positions'][i][1] - centerY

        if mode == "cw":
            x2 = -y
            y2 = x
        else:
            x2 = y
            y2 = -x

        currentTetro['positions'][i][0] = round(x2 + centerX)
        currentTetro['positions'][i][1] = round(y2 + centerY)

    if mode == "cw":
        currentTetro['orientation'] = (currentTetro['orientation'] + 1) % 4
    else:
        currentTetro['orientation'] = (currentTetro['orientation'] + 3) % 4

        
        
def messageCh(m, p):
    return False

def endGame():
    startGame()

def muteGame():
    startGame()

def pauseGame():
    startGame()
            
speedTable = {
                0: 860, # 799
                1: 715,
                2: 632,
                3: 549,
                4: 466,
                5: 383,
                6: 300,
                7: 216,
                8: 133,
                9: 100,
                10: 83,
                11: 83,
                12: 83,
                13: 67,
                14: 67,
                15: 67,
                16: 50,
                17: 50,
                18: 50,
                19: 33,
                20: 33,
                21: 33,
                22: 33,
                23: 33,
                24: 33,
                25: 33,
                26: 33,
                27: 33,
                28: 33,
                29: 20
            }

speedTable[0]

def keyDownHandler(key):
    key = key.lower()

    if key == "right":
        moveRight()
    elif key == "left":
        moveLeft()
    elif key == "down":
        dropButton()
    elif key == "up":
        rotate()
    elif key == "space":
        hardDrop()
    elif key == "c":
        holdTetro()
    elif key == "x":
        rotate()
    elif key == "z":
        rotate("ccw")
    elif key == "a":
        startGame()
    elif key == "esc":
        pauseGame()
    elif key == "m":
        muteGame()

import curses

def drawGame(stdscr):
    # Clear the screen
    stdscr.clear()

    # Draw the game board
    stdscr.addstr(0, 0, "+" + "-" * wTile + "+")
    for i, row in enumerate(gameArray[2:], start=1):
        stdscr.addstr(i, 0, "|")
        for cell in row:
            if cell:
                stdscr.addstr(i, 1 + row.index(cell), cell['color'][0])
            else:
                stdscr.addstr(i, 1 + row.index(cell), " ")
        stdscr.addstr(i, wTile + 1, "|")
    
    stdscr.addstr(hTile + 2, 0, "+" + "-" * wTile + "+")

    # Draw the held tetromino
    if heldTetro:
        stdscr.addstr(hTile + 4, 0, "Held Tetromino:")
        drawTetromino(stdscr, heldTetro)


def drawTetromino(stdscr, tetro):
    for y in range(4):
        for x in range(4):
            if [x, y] in tetro["positions"]:
                stdscr.addstr(hTile + 6 + y, x * 2, tetro['color'][0])
            else:
                stdscr.addstr(hTile + 6 + y, x * 2, " ")

def main(stdscr):
    # Initialize the game
    startGame()

    # Game loop
    while True:
        # Draw the game
        drawGame(stdscr)
        stdscr.refresh()

        # Check for user input
        key = stdscr.getch()
        keyDownHandler(key)

        # Update the game state
        if time.time() - lastTime >= speed:
            lastTime = time.time()
            if isSoftLocked:
                drop()
            else:
                lock()

        # Check for game over condition
        if currentTetro is None:
            endGame()
            break

# Call the main function to start the game
curses.wrapper(main)