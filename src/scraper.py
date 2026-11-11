#import requests
from curl_cffi import requests
from curl_cffi.requests import RequestsError
from dataclasses import dataclass

@dataclass
class HTMLScraperOutput:
    success: bool
    contents: str

def scrape_page(
    url: str 
    #agent_name: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
) -> HTMLScraperOutput:
    """returns a HTMLScraperOutput with success:True and the result of the request in contents.
    in case of an error, HTMLScraperOutput will have success:false and the exception details in contents"""
    
    try:
        r = requests.get(url, impersonate="chrome", timeout=10)
        r.raise_for_status() #catch error statuses
        
    except RequestsError as e:
        # invalid URL formats, DNS failures, timeouts, and 404/500 errors
        return HTMLScraperOutput(
            success=False,
            contents=f"Failed to fetch {url}: {e}"
        )

    return HTMLScraperOutput(
        success=True,
        contents=r.text
    )
