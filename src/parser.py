from bs4 import BeautifulSoup
from src.comment import Comment
from src.logger import logger
import re

def parse_page(page: str) -> list[Comment]:
    soup = BeautifulSoup(page, 'html.parser')
    messages = soup.findAll("td", class_="msg")
    logger.info(f"parser found {len(messages)} messages")

    parsed = []
    for m in messages:
        #the message id is contained in the parent td as id="message_1111111"
        id = int(re.sub(r"\D", "", m['id'])) #re only leaves digits
        username = m.find("a", class_="name").get_text()
        message = m.find("div", class_="msg_text").get_text()
        signature = m.find("div", class_="signature")
        if (signature):
            message += f"\nSignature: {signature.get_text()}"
        if (id and username and message):
            parsed.append(Comment(name=username, message=message, id=id))
        else:
            logger.error(f"failed to parse id={id}, username={username}, message={message}")
    return parsed
