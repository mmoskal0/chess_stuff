from dotenv import load_dotenv
from chrome import Chrome
from crawler import ChesscomCrawler


load_dotenv()

if __name__ == "__main__":
    crawler = ChesscomCrawler()
    with Chrome() as chrome:
        arena_url = crawler.create_arena(chrome.driver, "TestArena1")
    print(arena_url)
