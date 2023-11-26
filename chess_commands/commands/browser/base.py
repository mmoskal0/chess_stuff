from chess_commands.commands.base import Command


class BrowserCommand(Command):
    id = None
    uses_browser = True

    # TODO Initilize the driver here, instead of passing it in main.py
    def run(self, params, driver=None, **kwargs):
        parsed_params = self._parse_params(params)

        return self.get_result(driver, parsed_params)
