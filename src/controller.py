from src.repository import DBRInterface
from src.scraper import scrape_page
from src.parser import parse_page
from src.mapper import save_to_db
import logging, time

class ForumParserContoller:
    cooldown = 2.0
    _last_run = 0.0
    
    def __init__(self, db : DBRInterface, logger : logging.Logger):
        self.db = db
        self.logger = logger
        logger.info(f"created an instance of ForumParserController")

    def run(self, url: str) -> None:
        """calls scraper function to fetch a html page, 
        passes html into parser to get a list of Comment entities, 
        passes the list onto the mapper which saves them to DB.
        has a cooldown to prevent 403 error"""

        now = time.monotonic()
        elapsed = now - ForumParserContoller._last_run

        if elapsed < ForumParserContoller.cooldown:
            remaining = ForumParserContoller.cooldown - elapsed
            self.logger.warning(f"cooldown active. wait {remaining:.1f}s before running")
            return
        
        ForumParserContoller._last_run = now

        self.logger.info(f"running scraper for {url}")
        sco = scrape_page(url)
        if (not sco.success):
            self.logger.warning(f"failed to scrape page, {sco.contents}")
            return

        self.logger.info(f"running parser to find comments")
        comments = parse_page(sco.contents)

        if (len(comments) <= 0):
            self.logger.warning(f"couldn't find any comments")
            return

        self.logger.info(f"passing {len(comments)} objects into db")
        try:
            save_to_db(comments, self.db)
        except Exception as e:
            self.logger.error(f"ran into an exception while saving to repository, {e}")
            return

        self.logger.info(f"successfully finished the scenario for {url}")