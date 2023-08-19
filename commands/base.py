from crawlers.browser import ChesscomCrawler

AVAILABLE_COMMANDS = {}


class Command:
    uses_browser = False
    _parsing_error_message = "Invalid paramaters"

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

    def _parse_params(self, params):
        player = params.get("player", "").strip()
        default_player = params.get("default", "").strip()
        screenshot = bool(params.get("screenshot", "").strip())

        if not player and not default_player:
            self._parsing_error_message = (
                "Either player or default player needs to be specified."
            )
            return None
        if not player and default_player:
            player = default_player

        crawler = ChesscomCrawler()
        if not crawler.is_valid_username(player):
            self._parsing_error_message = f"Invalid chess.com username: {player}"
            return None

        return {
            "player": player,
            "screenshot": screenshot,
        }

    def run(self, params, **kwargs):
        parsed_params = self._parse_params(params)
        if not parsed_params:
            return self._parsing_error_message

        return self.get_result(parsed_params)
