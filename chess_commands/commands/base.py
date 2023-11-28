from urllib.parse import unquote

from crawlers.browser import ChesscomCrawler

AVAILABLE_COMMANDS = {}


class CommandError(Exception):
    pass


class Command:
    uses_browser = False

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, "id"):
            raise SyntaxError(f"{cls.__name__} must define an id")
        command_id = getattr(cls, "id")
        if command_id is None:
            # This is a base class, don't register it
            return
        if command_id in AVAILABLE_COMMANDS:
            raise SyntaxError(f"{cls.__name__} must have a unique id")
        if not hasattr(cls, "run"):
            raise SyntaxError(f"{cls.__name__} must implement get_result() method")

        AVAILABLE_COMMANDS[cls.id] = cls()

    @staticmethod
    def _clean_params(params):
        for k, v in params.items():
            # for whatever reason, Nightbot sometimes sends this unassigned unicode character
            v = v.replace("\U000E0000", "")
            params[k] = unquote(v).strip()
        return params

    def _parse_params(self, params):
        player = params.get("player", "")
        default_player = params.get("default", "")
        screenshot = bool(params.get("screenshot", ""))

        if not player and not default_player:
            raise CommandError("Either player or default player needs to be specified.")
        if not player and default_player:
            player = default_player

        crawler = ChesscomCrawler()
        if not crawler.is_valid_username(player):
            raise CommandError(f"Invalid chess.com username: {player}")

        return {
            "player": player,
            "screenshot": screenshot,
        }

    def get_user_activity_status(self, player):
        crawler = ChesscomCrawler()
        activity = crawler.get_user_activity(player)
        return crawler.get_activity_status(activity)

    def get_game_id(self, player):
        status, game_id, stream_url = self.get_user_activity_status(player)
        if game_id:
            return game_id
        else:
            raise CommandError(f"{player} is {status}")

    def run(self, params, **kwargs):
        try:
            params = self._clean_params(params)
            parsed_params = self._parse_params(params)
            return self.get_result(parsed_params)
        except CommandError as e:
            return str(e)
