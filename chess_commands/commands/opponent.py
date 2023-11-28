import flag

from commands.base import Command
from commands.emojis import Emoji
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
                three_min = p.get("three_minutes", 0)
                five_min = p.get("five_minutes", 0)
                survival = p.get("three_check", 0)
                if three_min or five_min or survival:
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

        opponent_uid = opponent["uid"]
        opponent_details = crawler.get_user_details(opponent_uid)
        country_code = opponent["country"]
        user_flag = (
            flag.flag(country_code) if country_code != "XX" else Emoji.white_flag
        )
        country = opponent_details["countryName"]
        join_date = opponent_details["joinDate"]
        profile = crawler.get_member_url(opponent["uid"])
        name = opponent.get("fullname", "").strip()
        result_profile = f"Opponent is {name} from {country} {user_flag}. Joined: {join_date} {Emoji.calendar}. Ping: {opponent['lagms']} ms {Emoji.bars}. Profile: {profile}"

        ratings = {}
        if "blitz" in stats:
            ratings["Blitz"] = stats["blitz"]
        if "bullet" in stats:
            ratings["Bullet"] = stats["bullet"]
        if "rapid" in stats:
            ratings["Rapid"] = stats["rapid"]
        if "tactics" in stats:
            ratings["Tactics"] = stats["tactics"]
        if "puzzle_rush" in stats:
            ratings["Puzzle Rush"] = stats["puzzle_rush"]
        ratings[f"Record vs {player['uid']}"] = stats["lifetime_score"]
        result_stats = "Stats Nerdge " + ", ".join(
            [f"{k}: {v}" for k, v in ratings.items()]
        )

        result = [
            result_profile,
            result_stats,
        ]

        stream_url = crawler.get_stream_url(opponent_uid)
        if stream_url:
            result.append(f"{opponent_uid} is streaming at {stream_url}")

        return result

    def get_result(self, params):
        player = params["player"]
        game_id = self.get_game_id(player)

        crawler = WebsocketCrawler(init=True)
        game = crawler.get_game(game_id)
        player, opponent = self.get_opponent(player, game["players"])
        stats = self.get_stats(player, opponent)
        result = self.format_result(player, opponent, stats)
        return result
