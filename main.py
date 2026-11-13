from src.repository import DatabaseRepository
from src.logger import logger
from src.controller import ForumParserContoller

#a sample showcase
db = DatabaseRepository()
parser = ForumParserContoller(db, logger)
parser.run("https://gamefaqs.gamespot.com/boards/920607-devil-may-cry-3-dantes-awakening/80234849")