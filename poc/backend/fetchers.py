from queue import Queue
import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
import time

class FetcherError(Exception):
    """Base exception for fetcher operations"""
    pass

class NetworkError(FetcherError):
    """Exception for network-related errors"""
    pass

class ParseError(FetcherError):
    """Exception for parsing-related errors"""
    pass

class Fetcher:
    #TODO: Maybe add tasks in queues, maybe do it on superclass: PipelineObject ?
    def __init__(self):
        pass
    def fetch_one(self, resource: str):
        pass
    def fetch_all(self):
        pass

class WikiFetcher(Fetcher):
    @staticmethod
    def fetch_one(resource: str, timeout: int = 30, retries: int = 3) -> Optional[str]:
        '''
        Fetches the law content from WikiText(ספר החוקים הפתוח) by law name(in hebrew).

        Args:
        - resource(string) - law name to fetch
        - timeout(int) - request timeout in seconds
        - retries(int) - number of retry attempts
        Returns:
            The law content as a string, or None if not found
        Raises:
            ValueError: If resource is empty or None
            NetworkError: If network request fails after all retries
            ParseError: If HTML parsing fails
        '''
        if not resource or not resource.strip():
            raise ValueError("Resource name cannot be empty or None")
        
        #Set the endpoint
        url = 'https://he.wikisource.org/w/index.php?title=מקור:{law_name}&action=edit'
        formatted_url = url.format(law_name=resource).replace(' ', '_')
        
        #Set the request
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Scraper/1.0)"}
        
        for attempt in range(retries):
            try:
                response = requests.get(formatted_url, headers=headers, timeout=timeout)
                response.raise_for_status()  # Raise an exception for HTTP errors
                
                # Parse HTML
                try:
                    soup = BeautifulSoup(response.text, "lxml")
                except Exception as e:
                    raise ParseError(f"Failed to parse HTML content: {e}")

                #Get the content
                law_content = soup.find(id='wpTextbox1')
                if law_content:
                    content = law_content.get_text(strip=True)
                    if not content:
                        return None
                    return content
                else:
                    return None
                    
            except requests.RequestException as e:
                if attempt == retries - 1:  # Last attempt
                    raise NetworkError(f"Failed to fetch resource '{resource}' after {retries} attempts: {e}")
                time.sleep(1)  # Brief pause before retry
                
            except Exception as e:
                if attempt == retries - 1:
                    raise FetcherError(f"Unexpected error fetching resource '{resource}': {e}")
                time.sleep(1)
        
        return None
    @staticmethod
    def fetch_all(timeout: int = 30, retries: int = 3, max_laws: Optional[int] = None) -> List[Dict[str, Any]]:
        '''
        Fetches all available laws from WikiSource.
        
        Args:
        - timeout(int) - request timeout in seconds
        - retries(int) - number of retry attempts
        - max_laws(int) - maximum number of laws to fetch (None for all)
        Returns:
            List of dictionaries containing law names and content
        Raises:
            NetworkError: If network request fails
            ParseError: If HTML parsing fails
            FetcherError: If other unexpected errors occur
        '''
        url = "https://he.wikisource.org/wiki/%D7%A1%D7%A4%D7%A8_%D7%94%D7%97%D7%95%D7%A7%D7%99%D7%9D_%D7%94%D7%A4%D7%AA%D7%95%D7%97"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Scraper/1.0)"}
        
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            raise NetworkError(f"Failed to fetch law list page: {e}")

        # Parse HTML
        try:
            soup = BeautifulSoup(response.text, "lxml")
        except Exception as e:
            raise ParseError(f"Failed to parse law list HTML: {e}")

        #Get law names and links
        root_url = 'https://he.wikisource.org'
        law_html_elements = soup.select("dd a")
        
        if not law_html_elements:
            raise ParseError("No law links found on the page")
        
        law_items = []
        for l in law_html_elements:
            try:
                if 'href' not in l.attrs:
                    continue
                url = root_url + l['href']
                law_name = l.text.strip()
                if law_name:  # Skip empty law names
                    law_items.append({'law_name': law_name, 'url': url})
            except Exception as e:
                # Log and skip problematic elements rather than failing completely
                continue
        
        if not law_items:
            raise ParseError("No valid law items found")
        
        # Limit number of laws if specified
        if max_laws is not None and max_laws > 0:
            law_items = law_items[:max_laws]

        law_contents = []
        failed_laws = []
        
        for l in law_items:
            try:
                content = WikiFetcher.fetch_one(l['law_name'], timeout=timeout, retries=retries)
                name_and_content = {
                    'law_name': l['law_name'],
                    'content': content
                }
                law_contents.append(name_and_content)
            except Exception as e:
                # Log failed laws but continue processing others
                failed_laws.append({'law_name': l['law_name'], 'error': str(e)})
                continue
        
        if not law_contents and failed_laws:
            raise FetcherError(f"Failed to fetch any laws. Sample errors: {failed_laws[:3]}")
        
        return law_contents
    @staticmethod
    def test_fetch_all():
        url = "https://he.wikisource.org/wiki/%D7%A1%D7%A4%D7%A8_%D7%94%D7%97%D7%95%D7%A7%D7%99%D7%9D_%D7%94%D7%A4%D7%AA%D7%95%D7%97"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Scraper/1.0)"}
        response = requests.get(url, headers=headers)

        # Parse HTML
        soup = BeautifulSoup(response.text, "lxml")


        #Maybe optinize to one loop
        #Get law names and links
        root_url = 'https://he.wikisource.org'
        law_html_elements = soup.select("dd a")
        law_items = []
        for l in law_html_elements[:50]:
            url = root_url + l['href']
            law_name = l.text
            law_items.append({'law_name': law_name, 'url': url})

        law_contents = []
        for l in law_items:
            name_and_content = {
                'law_name': l['law_name'],
                'content': WikiFetcher.fetch_one(l['law_name'])
            }
            law_contents.append(name_and_content)
        
        return law_contents