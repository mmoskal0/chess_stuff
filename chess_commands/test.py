from commands import AVAILABLE_COMMANDS
from dotenv import load_dotenv

load_dotenv()

task = "opponent"
player = "rachidamir"

command = AVAILABLE_COMMANDS[task]
params = {"player": player}

result = command.run(params)
print(result)
