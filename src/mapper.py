from src.comment import Comment
from src.repository import DBRInterface
from src.logger import logger

def save_to_db(parsed_data : list[Comment], repository : DBRInterface):
    for c in parsed_data:
        if (isinstance(c, Comment)):
            repository.add(c.id, c.name, c.message)
        else:
            logger.warning(f"recieved non-Comment object while mapping, skipping: {c}")