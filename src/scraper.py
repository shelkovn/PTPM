import requests
from dataclasses import dataclass

@dataclass
class HTMLScraperOutput:
    success: bool
    contents: str

def scrape_page(
        url: str, 
        agent_name: str = "towa's college assignment"
    ) -> HTMLScraperOutput:
    """returns a HTMLScraperOutput with success:True and the result of the request in contents.
    in case of an error, HTMLScraperOutput will have success:false and the exception details in contents"""

    headers = {'User-Agent': agent_name}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status() #catch error statuses
        
    except requests.RequestException as e:
        # invalid URL formats, DNS failures, timeouts, and 404/500 errors
        return HTMLScraperOutput(
            success=False,
            contents=f"Failed to fetch {url}: {e}"
        )

    return r.text
