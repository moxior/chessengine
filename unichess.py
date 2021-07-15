import time, random, pickle, string
from string import ascii_lowercase as abc
import requests

import rch

'''
MADE BY ANDREW HERRERA

idk what i was doing at this point




'''


def map_difficulty(n: int):
    difficulty = {
        1: "basic",
        2: "easy",
        3: "intermiediate",
        4: "hard",
    }
    return difficulty[n]


toMatrix = lambda x: [x[0] - 1, 8 - x[1]]  # converts cartasian cordinates to proper matrix indexing
toCartesian = lambda x: [x[0] + 1, abs(x[1] - 8)]
WHITE = {
    "KING": "♔",
    "QUEEN": "♕",
    "ROOK": "♖",
    "BISHOP": "♗",
    "KNIGHT": "♘",
    "PAWN": "♙",
    "NONE": " ",
    "TEST": "*"
}

BRD = [
    ["rook", "knight", "bishop", "king", "queen", "bishop", "knight", "rook"],
    ["pawn"] * 8
]


def inBounds(x, y):
    return 0 <= x <= 7 and 0 <= y <= 7


def rGet(arr):
    intMax = len(arr) - 1
    return arr[random.randint(0, intMax)]


class Piece:
    def __init__(self, tpiece, plr):
        self.piece = WHITE[tpiece.upper()]
        self.ID = plr

    def __repr__(self):
        return self.piece


class Tile:
    def __init__(self):
        self.piece = None

    def __repr__(self):
        return self.piece.piece if self.piece else " "


class Board:
    def __init__(self):
        self.board = [[Tile() for i in range(8)] for j in range(8)]
        '''
        We setup the 8x8 board with empty tiles, now we will occupy the tiles with traditional chess order
        '''

        # this is first initallizing black pieces
        for i, order in enumerate(BRD):
            for j, tpiece in enumerate(order):
                tile_piece = Piece(tpiece, "BLACK")
                ctile = self.board[i][j]
                ctile.piece = tile_piece
        # then initializing white pieces
        for i, order in enumerate(reversed(BRD)):
            for j, tpiece in enumerate(order):
                tile_piece = Piece(tpiece, "WHITE")
                ctile = self.board[i + 6][j]
                ctile.piece = tile_piece

    def shw(self):
        for i, row in enumerate(self.board):
            print(8 - i, *row)

    def fetch(self, x, y):
        return self.board[y][x]

    def fetchPieces(self, side, ignore=None):

        if not ignore: ignore = []
        pieces = []
        for y, row in enumerate(self.board):
            for x, tile in enumerate(row):
                if tile.piece and tile.piece.ID == side:
                    pieces.append([tile.piece, (x, y)])

        return pieces


class Bot:
    def __init__(self, side, game_client, difficulty=0):
        self.side = side
        self.difficulty = difficulty
        self.game = game_client
        self.moves_made = 0

    def move(self):
        self.moves_made += 1
        board = self.game.board
        if self.difficulty == 1:
            pieces = []  # we will store the pieces that we can move
            for y, row in enumerate(board.board):
                for x, tile in enumerate(row):
                    if tile.piece and tile.piece.ID == self.side:
                        possible_moves = self.game.generatePossibleMoves(tile.piece, [x, y], self.side)
                        if possible_moves != {}:
                            pieces.append(([x, y], possible_moves))
            tomove = rGet(pieces)
            random_move = rGet(list(tomove[1].keys()))
            print(tomove[0], random_move)
            self.game.move(toCartesian(tomove[0]), toCartesian(random_move), self.side)
        elif self.difficulty == 2:
            pieces = board.fetchPieces(self.side)
            r = random.randint(1, 3)
            moves = []
            if r == 1:
                print("defending")
                to_defend = {}
                pieces = board.fetchPieces(self.side)
                for piece, position in pieces:
                    to_defend[position] = False
                for key, _ in to_defend.items():
                    for piece, position in pieces:
                        possible_moves = self.game.generatePossibleMoves(piece, position, self.side, False)
                        g = possible_moves.get(key)
                        if g != None:
                            to_defend[key] = True
                            break
                iterations = 0
                to_defend = {key: item for key, item in to_defend.items() if
                             item == False}  # we filter out the pieces we need to defend
                for key, _ in to_defend.items():
                    for piece, position in pieces:
                        possible_moves = self.game.generatePossibleMoves(piece, position, self.side)
                        for move, _ in possible_moves.items():
                            defend_squares = self.game.generatePossibleMoves(piece, move, self.side, ignore=False)
                            g = defend_squares.get(key)
                            if g and self.game.canMake(toCartesian(move), toCartesian(key), self.side):
                                self.game.move(toCartesian(move), toCartesian(key), self.side)
                                return

            if True:

                for piece, position in pieces:
                    possible_moves = self.game.generatePossibleMoves(piece, position, self.side)
                    if possible_moves == {}: continue
                    for key, _ in possible_moves.items():
                        if self.game.canMake(toCartesian(position), toCartesian(key), self.side):
                            moves.append([position, key])
                move = rGet(moves)
                move0, move1 = move[0], move[1]
                self.game.move(toCartesian(move0), toCartesian(move1), self.side)
        elif self.difficulty == 3:
            '''
            MEDIUM DIFFICULTY

            -priority of bot follows

            -priority 1: find any hanging chess pieces, and attempt to defend them. if failure to do so, move on to priority 2

            -priority 2: find and attack any pieces of the opponent. if no pieces can be attacked, then priority 3

            -priority 3: move randomly anywhere on the board.
            '''
            pieces = board.fetchPieces(self.side)
            moves = []
            to_defend = {}
            for piece, position in pieces:
                to_defend[position] = False
            for key, _ in to_defend.items():
                for piece, position in pieces:
                    possible_moves = self.game.generatePossibleMoves(piece, position, self.side, False)
                    print(f"to defend:{key}",position)
                    g = possible_moves.get(key)
                    if g != None:
                        # once we find a piece that can defend this piece, we remove this element, or set it to true
                        # so we can filter it out later on line 198
                        to_defend[key] = True
                        break
            iterations = 0
            to_defend = {key: item for key, item in to_defend.items() if item == False}  # we filter out the pieces
            # we need to defend
            possible_moves = None
            for key, _ in to_defend.items():
                for piece, position in pieces:
                    possible_moves = self.game.generatePossibleMoves(piece, position, self.side)
                    for move, _ in possible_moves.items():
                        defend_squares = self.game.generatePossibleMoves(piece, move, self.side, ignore=False)
                        g = defend_squares.get(key)
                        print(move,key)
                        if g!=None and self.game.canMake(toCartesian(move), toCartesian(key), self.side):
                            self.game.move(toCartesian(move), toCartesian(key), self.side)
                            return  # if we can move, return and break function

            # now we find every piece we can attack
            possible_moves = None
            for piece, position in pieces:
                possible_moves = self.game.generatePossibleMoves(piece, position, self.side)
                for key, item in possible_moves.items():
                    tile = self.game.board.fetch(*key)
                    if tile.piece and tile.piece.ID != self.side:
                        if self.game.canMake(toCartesian(position), toCartesian(key), self.side):
                            self.game.move(toCartesian(position), toCartesian(key), self.side)
                            return
            print('we cant attack nor defend so just random move')


            for piece, position in pieces:
                possible_moves = self.game.generatePossibleMoves(piece, position, self.side)
                if possible_moves == {}: continue
                for key, _ in possible_moves.items():
                    if self.game.canMake(toCartesian(position), toCartesian(key), self.side):
                        moves.append([position, key])
            move = rGet(moves)
            move0, move1 = move[0], move[1]
            self.game.move(toCartesian(move0), toCartesian(move1), self.side)

class Game:

    def generateBoardURL(self):
        link = rch.parseBoard(self.board.board)
        return link

    def __init__(self):
        self.board = Board()

    def bufferBoard(self):
        buffer = ""
        for i, row in enumerate(self.board.board):
            newrow = " ".join([repr(tile) for tile in row])
            buffer += "\n" + str(i + 1) + " " + newrow

        return "```" + buffer + "```"

    def generatePossibleMoves(self, piece, pos, plr, ignore=True) -> dict:
        '''

        we return a dictonary so we can check if a position exists in O(1) time. returning an array would require
        a linear iteration, which can be expensive

        '''
        offset = lambda arr, ofs: (arr[0] + ofs[0], arr[1] + ofs[1])

        brd = self.board
        hsh = {}
        if piece.piece == WHITE["KING"]:  # if piece is a king, logic follows bellow
            king = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]

            for i in range(8):
                gmove = offset(pos, king[i])
                if inBounds(*gmove):

                    gpiece = brd.fetch(*gmove)

                    if gpiece.piece:
                        if not ignore:
                            hsh[gmove] = True
                        elif gpiece.piece.ID != plr:
                            hsh[gmove] = True
                        continue
                    hsh[gmove] = True
        elif piece.piece == WHITE["QUEEN"]:
            b = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]
            # b is all the directions the queen can go to
            # we iterate and offset cords by b[i] for i in range(8)

            for i in range(8):
                prev = offset(pos, b[i])
                while inBounds(*prev):
                    cur_tile = brd.fetch(*prev)
                    if cur_tile.piece:
                        if not ignore:
                            hsh[prev] = True
                        elif cur_tile.piece and cur_tile.piece.ID != plr:
                            hsh[prev] = True
                        break
                    hsh[prev] = True
                    prev = offset(prev, b[i])
        elif piece.piece == WHITE["ROOK"]:
            # we can use the kings offsets, since it moves in the same fashion
            # we can make a copy to not confuse ourselves
            rook = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for i in range(4):
                prev = offset(pos, rook[i])
                while inBounds(*prev):
                    cur_tile = brd.fetch(*prev)
                    if cur_tile.piece:
                        if not ignore:
                            hsh[prev] = True

                        elif cur_tile.piece.ID != plr:
                            hsh[prev] = True
                        break
                    hsh[prev] = True
                    prev = offset(prev, rook[i])
        elif piece.piece == WHITE["BISHOP"]:
            bishop = [(-1, 1), (-1, -1), (1, -1), (1, 1)]
            for i in range(4):
                prev = offset(pos, bishop[i])

                while inBounds(*prev):
                    cur_tile = brd.fetch(*prev)
                    if cur_tile.piece:
                        if not ignore:
                            hsh[prev] = True

                        elif cur_tile.piece.ID != plr:
                            hsh[prev] = True
                        break
                    hsh[prev] = True
                    prev = offset(prev, bishop[i])
        elif piece.piece == WHITE["KNIGHT"]:
            knight = [
                (1, 2),
                (-1, 2),
                (1, -2),
                (-1, -2),
                (-2, 1),
                (-2, -1),
                (2, -1),
                (2, 1),
            ]
            for move in knight:
                gpos = offset(pos, move)
                if inBounds(*gpos):
                    tile = brd.fetch(*gpos)
                    if not tile.piece:
                        hsh[gpos] = True
                    elif tile.piece:
                        if not ignore:
                            hsh[gpos] = True

                        elif tile.piece.ID != plr:
                            hsh[gpos] = True
        elif piece.piece == WHITE["PAWN"]:
            '''
            first, pawn has many edge cases
            we need to first check what side its on, so we can evaluate whether it can move two places instead of one
            second, the pawn is unique as it can either push forward or attack diagonally
            logic is harder to implement then it sounds

            '''

            startingpos = 6 if plr == "WHITE" else 1
            offs = -1 if plr == "WHITE" else 1

            tile = self.board.fetch(*offset(pos, (0, offs)))
            if tile.piece == None: hsh[offset(pos, (0, offs))] = "PUSH"
            second_tile = self.board.fetch(*offset(pos, (0, offs +offs)))
            if pos[1] == startingpos and second_tile.piece == None and tile.piece == None:
                # this means that the pawn is at its starting position, so we can push y+2
                hsh[offset(pos, (0, offs + offs))] = "PUSH"

            diag1, diag2 = offset(pos, (1, offs)), offset(pos, (-1, offs))
            if inBounds(*diag1):
                tile = brd.fetch(*diag1)
                if tile.piece and tile.piece.ID != plr: hsh[diag1] = "ATTACK"
            if inBounds(*diag2):
                tile = brd.fetch(*diag2)
                if tile.piece and tile.piece.ID != plr: hsh[diag2] = "ATTACK"

        return hsh

    def parseMoves(self, string):
        '''

        We will use cartesian cordinates for this function, where we input a singular string

        input will look something like this
        "a1b1"

        '''
        split = lambda x: [x[:2], x[2:]]
        parse = lambda a: [abc.index(a[0]) + 1, int(a[1])]
        m1, m2 = split(string)
        m1, m2 = parse(m1), parse(m2)
        # we are returning cartesian cordinates of the arr
        return m1, m2

    def inCheck(self, brd, plr):

        # we first need to locate plr king in brd

        for i, row in enumerate(brd):
            for j, tile in enumerate(row):
                if tile.piece and tile.piece.piece == WHITE["KING"] and tile.piece.ID == plr:
                    king_pos = (j, i)
                    break

        for y, row in enumerate(brd):
            for x, tile in enumerate(row):
                if tile.piece and tile.piece.ID != plr:
                    # print(tile.piece.piece,tile.piece.ID)
                    other = "BLACK" if plr == "WHITE" else "WHITE"
                    possible_moves = self.generatePossibleMoves(tile.piece, [x, y], other)
                    # now we need to check whether any of the opposite side pieces can reach to the kings position
                    g = possible_moves.get(king_pos)
                    if g != None:
                        return True
        return False

    def canMake(self, start, end, plr):
        start, end = toMatrix(start), toMatrix(end)
        piece1 = self.board.fetch(*start).piece
        piece2 = self.board.fetch(*end).piece

        if not piece1:
            # this means that the player, is trying to move an empty square. break function and return none
            return False

        # operation: move piece 1 to piece 2 location

        possible_moves = self.generatePossibleMoves(piece1, start, plr)
        key = end
        key = (key[0], key[1])
        g = possible_moves.get(key)
        if piece1.piece == WHITE["PAWN"]:
            if g == None: return False
            if piece2 == None and g == "PUSH":
                pass
            elif piece2 == None and g == "ATTACK":
                return False
            elif piece2.piece != None and g == "ATTACK":
                pass
        # print(self.inCheck(self.board.board,plr))
        if g == None:
            return False

        self.board.fetch(*end).piece = piece1
        self.board.fetch(*start).piece = None

        can_move = False
        if not self.inCheck(self.board.board, plr):
            can_move = True
        self.board.fetch(*end).piece = piece2
        self.board.fetch(*start).piece = piece1

        return can_move

    def markPossibleMoves(self, pos, plr):
        piece = self.board.fetch(*toMatrix(pos)).piece
        pmoves = self.generatePossibleMoves(piece, toMatrix(pos), plr)
        for key, _ in pmoves.items():
            tile = self.board.fetch(*key)
            tile.piece = Piece("TEST", "NONE")
        return pmoves

    def move(self, pos1, pos2, plr, convert=False):

        if self.canMake(pos1, pos2, plr):
            pos1, pos2 = toMatrix(pos1), toMatrix(pos2)
            cur_tile = self.board.fetch(*pos1)
            destination = self.board.fetch(*pos2)
            destination.piece = cur_tile.piece
            cur_tile.piece = None
            return True

        return False

    def createBot(self, difficulty, side):
        bot = Bot(side, self, difficulty)
        return bot

    def abort(self):
        self.board = Board()
