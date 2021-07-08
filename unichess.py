import time, random, pickle, string
from string import ascii_lowercase as abc
import requests

import rch





'''
MADE BY ANDREW HERRERA

idk what i was doing at this point




'''
toMatrix = lambda x: [x[0] - 1, 8 - x[1]]  # converts cartasian cordinates to proper matrix indexing
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
    intMax = len(arr)-1
    return arr[random.randint(0,intMax)]
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

class Bot:
    def __init__(self,side,game_client,difficulty=0):
        self.side = side
        self.difficulty = difficulty
        self.game = game_client
    def move(self):
        board = self.game.board.board
        if self.difficulty == 1:
            pieces = []#we will store the pieces that we can move
            for y,row in enumerate(board):
                for x,tile in enumerate(row):
                    if tile.piece and tile.piece.ID == self.side:
                        possible_moves = self.game.generatePossibleMoves(tile.piece,[x,y],self.side)
                        if possible_moves != {}:
                            pieces.append(([x,y],possible_moves))
            tomove = rGet(pieces)
            random_move = rGet(list(tomove[1].keys()))
            print(tomove[0],random_move)
            self.game.move(tomove[0],random_move,True)

class Game:

    def generateBoardURL(self):
        link = rch.parseBoard(self.board.board)
        return link
    def __init__(self):
        self.board = Board()
    def bufferBoard(self):
        buffer = ""
        for i,row in enumerate(self.board.board):
            newrow = " ".join([repr(tile) for tile in row])
            buffer+="\n"+str(i+1)+" "+newrow

        return "```"+buffer+"```"
    def generatePossibleMoves(self, piece, pos, plr) -> dict:
        '''

        we return a dictonary so we can check if a position exists in O(1) time. returning an array would require
        a linear iteration, which can be expensive

        '''
        offset = lambda arr, ofs: (arr[0] + ofs[0], arr[1] + ofs[1])
        king = [(0, 1), (0, -1), (-1, 0), (1, 0)]

        brd = self.board
        hsh = {}
        if piece.piece == WHITE["KING"]:  # if piece is a king, logic follows bellow
            for pmove in king:
                gmove = offset(pos, pmove)
                if inBounds(*gmove):
                    gpiece = brd.fetch(*gmove)

                    if gpiece.piece:
                        if gpiece.piece.ID != plr:hsh[gmove] = True
                        break
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
                        if cur_tile.piece and cur_tile.piece.ID != plr:hsh[prev] = True
                        break
                    hsh[prev] = True
                    prev = offset(prev, b[i])
        elif piece.piece == WHITE["ROOK"]:
            # we can use the kings offsets, since it moves in the same fashion
            # we can make a copy to not confuse ourselves
            rook = king
            for i in range(4):
                prev = offset(pos, rook[i])
                while inBounds(*prev):
                    cur_tile = brd.fetch(*prev)
                    if cur_tile.piece:
                        if cur_tile.piece.ID != plr:hsh[prev] = True
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
                        if cur_tile.piece.ID != plr:hsh[prev] = True
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
                    elif tile.piece and tile.piece.ID != plr:hsh[gpos] = True
        elif piece.piece == WHITE["PAWN"]:
            '''
            first, pawn has many edge cases
            we need to first check what side its on, so we can evaluate whether it can move two places instead of one
            second, the pawn is unique as it can either push forward or attack diagonally
            logic is harder to implement then it sounds

            '''

            startingpos = 6 if plr == "WHITE" else 1
            offs = -1 if plr == "WHITE" else 1
            hsh[offset(pos, (0, offs))] = "PUSH"
            if pos[1] == startingpos:
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
        "1,1 2,2"

        '''
        parse = lambda a: [abc.index(a[0])+1,int(a[1])]
        m1, m2 = string.split(" ")
        m1, m2 = parse(m1), parse(m2)
        # we are returning cartesian cordinates of the arr
        return m1, m2
    def inCheck(self,brd,plr):

        #we first need to locate plr king in brd

        for i,row in enumerate(brd):
            for j, tile in enumerate(row):
                if tile.piece and tile.piece.piece == WHITE["KING"] and tile.piece.ID == plr:
                    king_pos = (j,i)
                    break

        for i,row in enumerate(brd):
            for j,tile in enumerate(row):
                if tile.piece and tile.piece.ID != plr:
                    other = "BLACK" if plr == "WHITE" else "WHITE"
                    possible_moves = self.generatePossibleMoves(tile.piece,[j,i],other)
                    #now we need to check whether any of the opposite side pieces can reach to the kings position
                    g = possible_moves.get(king_pos)
                    if g!=None:return True
        return False


    def canMake(self, start, end, plr):
        piece1 = self.board.fetch(*toMatrix(start)).piece
        piece2 = self.board.fetch(*toMatrix(end)).piece
        if not piece1:
            # this means that the player, is trying to move an empty square. break function and return none
            return None

        # operation: move piece 1 to piece 2 location

        possible_moves = self.generatePossibleMoves(piece1, toMatrix(start), plr)
        print(possible_moves)
        print(self.inCheck(self.board.board,plr))
    def markPossibleMoves(self,pos,plr):
        print("yeah this is working")
        piece = self.board.fetch(*toMatrix(pos)).piece
        print(piece)
        pmoves = self.generatePossibleMoves(piece,toMatrix(pos),plr)
        for key,_ in pmoves.items():
            print(key)
            print('this is iterating')
            tile = self.board.fetch(*key)
            tile.piece = Piece("TEST","NONE")
        return pmoves
    def move(self,pos1,pos2,convert=False):
        if not convert:
            pos1,pos2 = toMatrix(pos1),toMatrix(pos2)

        cur_tile = self.board.fetch(*pos1)
        destination = self.board.fetch(*pos2)
        destination.piece = cur_tile.piece
        cur_tile.piece = None
    def createBot(self,difficulty,side):
        bot = Bot(side,self,difficulty)
        return bot
