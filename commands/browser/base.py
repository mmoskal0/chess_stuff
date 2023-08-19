from commands.base import Command


class BrowserCommand(Command):
    id = None
    uses_browser = True

    # TODO Initilize the driver here, instead of passing it in main.py
    def run(self, params, driver=None, **kwargs):
        parsed_params = self._parse_params(params)
        if not parsed_params:
            return self._parsing_error_message

        return self.get_result(driver, parsed_params)
