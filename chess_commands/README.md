## Introduction
The goal of this project is to provide a set of commands that can be used to interact with chess.com website. There is
also a publicly accessible API that can be used to execute these commands. You can contact me for the API `base_url`.

## Command types:
- Asynchronous commands
  - These commands take a while to execute, mainly due to the cost of initializaing a Chrome browser,
  which in some cases is necessary due to chess.com API limitations. The API will return a blank response and
  when the result is ready, it will be sent to the callback URL provided by Nightbot. The implementation is Nightbot
  specific, so unfortunately it won't work with other chat bots (because I'm lazy).
  - The API url for these commands is `base_url/chess_async/command=command_name&argument1=...`
- Regular commands
  - These commands are executed immediately and the result is returned in the response. They should work with any chat bot.
  - They API url for these commands is `base_url/chess/command=command_name&argument1=...`

## Example commands:
- Current arena\
Gets a link to current/upcoming arena/tournament for a given club:
    ```
    http://base_url/chess/command=arena&club=chesscom_club_id
    ```
- Game\
Gets a link to the game the player is currently playing:
    ```
    http://base_url/chess/command=game&player=chesscom_username
    ```
- Opening\
Gets an opening name from a game the player is currently playing:
    ```
    http://base_url/chess_async/command=opening&player=chesscom_username
    ```
- Opponent\
Gets a link to current opponent's chess.com profile:
    ```
    http://base_url/chess_async/command=opponent&player=chesscom_username
    ```
- Ping\
Gets player's chess.com ping:
    ```
    http://base_url/chess_async/command=ping&player=chesscom_username
    ```
- Eval\
Gets stockfish evaluation of the current position in the game the player is currently playing:
    ```
    http://base_url/chess_async/command=eval&player=chesscom_username
    ```
