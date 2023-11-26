from commands.base import Command
from crawlers.browser import ChesscomCrawler


class CurrentArena(Command):
    id = "arena"

    def _parse_params(self, params):
        hannah_club = "298133"
        return {"club_id": params.get("club", hannah_club).strip()}

    def get_result(self, params):
        club_id = params["club_id"]
        crawler = ChesscomCrawler()
        arenas, tournaments = crawler.upcoming_tournaments(club_id)
        if not arenas and not tournaments:
            arenas, tournaments = crawler.current_tournaments(club_id)

        if not arenas and not tournaments:
            return "<no tournament in progress>"
        if arenas:
            arena_id = arenas[0]["id"]
            return f"https://www.chess.com/play/arena/{arena_id}"
        if tournaments:
            tournament_id = tournaments[0]["id"]
            return f"https://www.chess.com/play/tournament/{tournament_id}"
