from commands.base import Command
from crawlers.browser import ChesscomCrawler
from crawlers.websockets import WebsocketCrawler


class Opponent(Command):
    id = "opponent"

    @staticmethod
    def get_opponent(player, players):
        if players[0]["uid"].lower() == player.lower():
            return players[0], players[1]
        else:
            return players[1], players[0]

    def get_stats(self, player, opponent):
        crawler = ChesscomCrawler()
        stats = crawler.get_player_stats(opponent["uid"])
        parsed_stats = {}
        stat_keys = ["lightning", "bullet", "rapid", "tactics", "tactics_challenge"]
        for stat in stats["stats"]:
            key = stat["key"]
            if key not in stat_keys:
                continue
            s = stat["stats"]

            if key == "tactics_challenge":
                p = s["modes"]
                three_min = p.get("three_minutes", "0")
                five_min = p.get("five_minutes", "0")
                survival = p.get("three_check", "0")
                parsed_stats[
                    "puzzle_rush"
                ] = f"{three_min}/{five_min}/{survival} (3min/5min/Survival)"
            else:
                if key == "lightning":
                    key = "blitz"
                parsed_stats[key] = f"{s['rating']}/{s['highest_rating']}"

        score = crawler.get_score(opponent["id"], player["id"])
        parsed_stats[
            "lifetime_score"
        ] = f"{score['win']}/{score['draw']}/{score['lose']} (W/D/L)"

        return parsed_stats

    def format_result(self, player, opponent, stats):
        crawler = ChesscomCrawler()

        result = {}
        profile = crawler.get_member_url(opponent["uid"])
        name = opponent.get("fullname", "").strip()
        if name:
            result["Name"] = name
        result["Ping"] = f"{opponent['lagms']} ms"
        if "blitz" in stats:
            result["Blitz"] = stats["blitz"]
        if "bullet" in stats:
            result["Bullet"] = stats["bullet"]
        if "rapid" in stats:
            result["Rapid"] = stats["rapid"]
        if "tactics" in stats:
            result["Tactics"] = stats["tactics"]
        if "puzzle_rush" in stats:
            result["Puzzle Rush"] = stats["puzzle_rush"]
        result[f"Record vs {player['uid']}"] = stats["lifetime_score"]

        return profile + "       " + ", ".join([f"{k}: {v}" for k, v in result.items()])

    def get_result(self, params):
        player = params["player"]
        game_id = self.get_current_game(player)

        crawler = WebsocketCrawler(init=True)
        game = crawler.get_game(game_id)
        player, opponent = self.get_opponent(player, game["players"])
        stats = self.get_stats(player, opponent)
        player_ping = f"{player['uid']}: Ping: {player['lagms']}, Lag: {player['lag']}"
        return [self.format_result(player, opponent, stats), player_ping]
