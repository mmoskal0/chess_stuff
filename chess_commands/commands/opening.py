import json
import os
import random

import chess

from chess_commands.commands.base import Command
from chess_commands.crawlers.websockets import WebsocketCrawler


class Opening(Command):
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

    def get_silly_opening_name(self):
        choices = [
            "The Goose Opening: Beak Attack, King's Knight Development",
            "The Goose Opening: Beak Attack, Queen's Rook Activation",
            "The Goose Opening: Beak Attack, Central Pawn Push",
            "The Goose Opening: Feathered Defense, Early Pawn Push",
            "The Goose Opening: Feathered Defense, Pin Variation",
            "The Goose Opening: Feathered Defense, Retreat Line",
            "The Goose Opening: Flight Formation, Central Pawn Control",
            "The Goose Opening: Flight Formation, Long Castling Strategy",
            "The Goose Opening: Flight Formation, Pawn Storm Tactics",
            "The Goose Opening: Gaggle Gambit, Declined",
            "The Goose Opening: Gaggle Gambit, Accepted",
            "The Goose Opening: Gaggle Gambit, Knight Maneuver",
            "The Goose Opening: Gander Gambit, Gambit Accepted",
            "The Goose Opening: Gander Gambit, Gambit Declined",
            "The Goose Opening: Gander Gambit, King's Rook Defense",
            "The Goose Opening: Honk Gambit, Aggressive Line",
            "The Goose Opening: Honk Gambit, Quiet Line",
            "The Goose Opening: Honk Gambit, Sacrificial Attack",
            "The Goose Opening: Goose Chase Variation, Early Castling",
            "The Goose Opening: Goose Chase Variation, Pawn Storm Tactics",
            "The Goose Opening: Goose Chase Variation, Sacrificial Line",
            "The Goose Opening: Migratory Line, Central Control",
            "The Goose Opening: Migratory Line, Double Pawn Push",
            "The Goose Opening: Migratory Line, Long Castling",
            "The Goose Opening: Pondside Gambit, Counterattack Formation",
            "The Goose Opening: Pondside Gambit, Early Queen's Bishop Maneuver",
            "The Goose Opening: Pondside Gambit, Sacrificial Attack",
            "The Goose Opening: Poultry Gambit, Aggressive Line",
            "The Goose Opening: Poultry Gambit, King's Knight Development",
            "The Goose Opening: Poultry Gambit, Solid Line",
            "The Goose Opening: Preening Variation, Counterattack Line",
            "The Goose Opening: Preening Variation, Pawn Chain Formation",
            "The Goose Opening: Preening Variation, Queen's Bishop Maneuver",
            "The Goose Opening: Snow Goose Formation, Long Castling Strategy",
            "The Goose Opening: Snow Goose Formation, Pawn Chain Defense",
            "The Goose Opening: Snow Goose Formation, Queen's Bishop Maneuver",
        ]
        return random.choice(choices)

    def get_silly_defense_name(self):
        choices = [
            "The Goose Defense: Cygnet Formation, Main Line",
            "The Goose Defense: Cygnet Formation, Closed Variation",
            "The Goose Defense: Cygnet Formation, Gosling Gambit",
            "The Goose Defense: Downy Line, Old Main Line",
            "The Goose Defense: Downy Line, Counterattacking Variation",
            "The Goose Defense: Downy Line, Quiet Defense",
            "The Goose Defense: Gosling Formation, Fianchetto Variation",
            "The Goose Defense: Gosling Formation, Pawn Storm Line",
            "The Goose Defense: Gosling Formation, Double Knight Maneuver",
            "The Goose Defense: Puddle Line, Counter-Gambit",
            "The Goose Defense: Puddle Line, Aggressive Line",
            "The Goose Defense: Puddle Line, Pawn Tension Variation",
            "The Goose Defense: Quack Formation, Central Pawn Push",
            "The Goose Defense: Quack Formation, Double Pawn Sacrifice",
            "The Goose Defense: Quack Formation, Early Castling",
            "The Goose Defense: Waddle Gambit, King's Rook Defense",
            "The Goose Defense: Waddle Gambit, Sharp Line",
            "The Goose Defense: Waddle Gambit, Solid Line",
            "The Goose Defense: Webbed Variation, Knight Outpost",
            "The Goose Defense: Webbed Variation, Pawn Chain Setup",
            "The Goose Defense: Webbed Variation, Solid Line",
            "The Goose Defense: Wetland Variation, Central Pawn Control",
            "The Goose Defense: Wetland Variation, Double Pawn Push",
            "The Goose Defense: Wetland Variation, Queen's Rook Activation",
            "The Goose Defense: Splash Gambit, Accepted",
            "The Goose Defense: Splash Gambit, Declined",
            "The Goose Defense: Splash Gambit, Central Pawn Attack",
        ]

        return random.choice(choices)

    def get_result(self, params):
        player = params["player"]
        game_id = self.get_current_game(player)

        crawler = WebsocketCrawler(init=True)
        moves = crawler.get_game_moves(game_id)
        uci_list = self.tcn_to_uci(moves)

        # Temporary, because I'm too lazy to actually add the fens to the database
        if uci_list[0] == "g2g4":
            return self.get_silly_opening_name()
        elif "g7g5" in uci_list[1:4]:
            return self.get_silly_defense_name()

        fens = self.uci_list_to_fens(uci_list)
        fens = self.format_fens_for_eco_lookup(fens)
        opening = self.get_opening_name(fens)

        return opening
