from commands.base import Command


class BrowserCommand(Command):
    id = None
    uses_browser = True

    def run(self, params, driver=None, **kwargs):
        parsed_params = self._parse_params(params)
        if not parsed_params:
            return self.usage

        return self.get_result(driver, parsed_params)
