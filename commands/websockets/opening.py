import json
import os

import chess

from commands.websockets.base import WebsocketCommand
from crawlers.browser import ChesscomCrawler
from crawlers.websockets import WebsocketCrawler


class Opening(WebsocketCommand):
    id = "opening"

    def tcn_to_uci(self, tcn):
        # I have no idea what this is doing, I copied it from a JS file

        symbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?{~}(^)[_]@#$,./&-*++="
        pieces = "qnrbkp"

        i = 0
        uci_list = []
        while i < len(tcn):
            promotion = ""
            x = symbols.index(tcn[i])
            y = symbols.index(tcn[i + 1])
            if y > 63:
                promotion = pieces[(y - 64) // 3]
                # ICANT xD
                y = x + (-8 if x < 16 else 8) + (y - 1) % 3 - 1
            move_from = f"{symbols[x % 8]}{x // 8 + 1}"
            move_to = f"{symbols[y % 8]}{y // 8 + 1}"
            uci_list.append(f"{move_from}{move_to}{promotion}")
            i += 2

        return uci_list

    def uci_list_to_fens(self, uci_list):
        board = chess.Board()
        fens = []
        for uci in uci_list:
            board.push_uci(uci)
            fens.append(board.fen())
        return fens

    def format_fens_for_eco_lookup(self, fens):
        return [" ".join(fen.split(" ")[:3]) for fen in reversed(fens)]

    def get_opening_name(self, fens_history):
        with open(f"{os.environ['LAMBDA_TASK_ROOT']}/eco_formatted.json") as f:
            eco_db = json.load(f)
            for fen in fens_history:
                try:
                    return eco_db[fen][0]
                except KeyError:
                    pass
        return "Unknown opening"

    def get_result(self, params):
        player = params["player"]
        crawler = ChesscomCrawler()
        activity = crawler.get_user_activity(player)
        try:
            status, game_id = crawler.get_activity_status(activity)
        except KeyError:
            return f"{player} is a new account, utilizing chess.com's new websocket API. Do not blame Slomka that the command stopped working, he tried his best PepeHands"
        if not game_id:
            return f"{player} is {status}"

        crawler = WebsocketCrawler()
        crawler.connect(self.ws)
        crawler.handshake(self.ws)
        moves = crawler.get_game_moves(self.ws, game_id)
        uci_list = self.tcn_to_uci(moves)
        fens = self.uci_list_to_fens(uci_list)
        fens = self.format_fens_for_eco_lookup(fens)
        return self.get_opening_name(fens)
