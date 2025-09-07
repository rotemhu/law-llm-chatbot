import unittest
from unittest.mock import patch, Mock, MagicMock
import requests
from bs4 import BeautifulSoup
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fetchers import WikiFetcher, FetcherError, NetworkError, ParseError


class TestWikiFetcher(unittest.TestCase):

    def setUp(self):
        self.sample_law_name = "חוק הבטיחות"
        self.sample_url = "https://he.wikisource.org/w/index.php?title=מקור:חוק_הבטיחות&action=edit"
        
        self.sample_html = '''
        <html>
            <body>
                <textarea id="wpTextbox1">
                <שם>חוק הבטיחות</שם>
                <מקור>ספר החוקים הפתוח</מקור>
                = חלק א' =
                @ 1. כל אדם זכאי לבטיחות.
                @ 2. המדינה תדאג לבטיחות הציבור.
                </textarea>
            </body>
        </html>
        '''
        
        self.sample_law_list_html = '''
        <html>
            <body>
                <dd><a href="/wiki/מקור:חוק_הבטיחות">חוק הבטיחות</a></dd>
                <dd><a href="/wiki/מקור:חוק_השכר">חוק השכר</a></dd>
                <dd><a href="/wiki/מקור:חוק_הבחירות">חוק הבחירות</a></dd>
            </body>
        </html>
        '''

    @patch('fetchers.requests.get')
    def test_fetch_one_success(self, mock_get):
        mock_response = Mock()
        mock_response.text = self.sample_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = WikiFetcher.fetch_one(self.sample_law_name)
        
        self.assertIsNotNone(result)
        self.assertIn("חוק הבטיחות", result)
        self.assertIn("@ 1. כל אדם זכאי לבטיחות.", result)
        mock_get.assert_called_once()

    @patch('fetchers.requests.get')
    def test_fetch_one_empty_resource(self, mock_get):
        with self.assertRaises(ValueError) as context:
            WikiFetcher.fetch_one("")
        
        self.assertIn("Resource name cannot be empty", str(context.exception))
        mock_get.assert_not_called()

    @patch('fetchers.requests.get')
    def test_fetch_one_none_resource(self, mock_get):
        with self.assertRaises(ValueError) as context:
            WikiFetcher.fetch_one(None)
        
        self.assertIn("Resource name cannot be empty", str(context.exception))
        mock_get.assert_not_called()

    @patch('fetchers.requests.get')
    def test_fetch_one_network_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Network error")
        
        with self.assertRaises(NetworkError) as context:
            WikiFetcher.fetch_one(self.sample_law_name)
        
        self.assertIn("Failed to fetch resource", str(context.exception))
        self.assertEqual(mock_get.call_count, 3)  # Default retries

    @patch('fetchers.requests.get')
    def test_fetch_one_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with self.assertRaises(NetworkError):
            WikiFetcher.fetch_one(self.sample_law_name)

    @patch('fetchers.requests.get')
    def test_fetch_one_parse_error(self, mock_get):
        mock_response = Mock()
        mock_response.text = "invalid html <>"
        mock_response.raise_for_status.return_value = None
        
        with patch('fetchers.BeautifulSoup') as mock_soup:
            mock_soup.side_effect = Exception("Parse error")
            mock_get.return_value = mock_response
            
            with self.assertRaises(ParseError) as context:
                WikiFetcher.fetch_one(self.sample_law_name)
            
            self.assertIn("Failed to parse HTML content", str(context.exception))

    @patch('fetchers.requests.get')
    def test_fetch_one_no_content_found(self, mock_get):
        html_no_content = '''
        <html>
            <body>
                <div>No textarea found</div>
            </body>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.text = html_no_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = WikiFetcher.fetch_one(self.sample_law_name)
        
        self.assertIsNone(result)

    @patch('fetchers.requests.get')
    def test_fetch_one_empty_content(self, mock_get):
        html_empty_content = '''
        <html>
            <body>
                <textarea id="wpTextbox1"></textarea>
            </body>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.text = html_empty_content
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = WikiFetcher.fetch_one(self.sample_law_name)
        
        self.assertIsNone(result)

    @patch('fetchers.requests.get')
    def test_fetch_one_with_custom_timeout_retries(self, mock_get):
        mock_response = Mock()
        mock_response.text = self.sample_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        WikiFetcher.fetch_one(self.sample_law_name, timeout=60, retries=5)
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['timeout'], 60)

    @patch('fetchers.requests.get')
    def test_fetch_all_success(self, mock_get):
        def mock_get_side_effect(url, **kwargs):
            if "ספר_החוקים_הפתוח" in url:
                mock_response = Mock()
                mock_response.text = self.sample_law_list_html
                mock_response.raise_for_status.return_value = None
                return mock_response
            else:
                mock_response = Mock()
                mock_response.text = self.sample_html
                mock_response.raise_for_status.return_value = None
                return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        result = WikiFetcher.fetch_all(max_laws=2)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('law_name', result[0])
        self.assertIn('content', result[0])

    @patch('fetchers.requests.get')
    def test_fetch_all_network_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Network error")
        
        with self.assertRaises(NetworkError) as context:
            WikiFetcher.fetch_all()
        
        self.assertIn("Failed to fetch law list page", str(context.exception))

    @patch('fetchers.requests.get')
    def test_fetch_all_parse_error(self, mock_get):
        with patch('fetchers.BeautifulSoup') as mock_soup:
            mock_response = Mock()
            mock_response.text = "html"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            mock_soup.side_effect = Exception("Parse error")
            
            with self.assertRaises(ParseError) as context:
                WikiFetcher.fetch_all()
            
            self.assertIn("Failed to parse law list HTML", str(context.exception))

    @patch('fetchers.requests.get')
    def test_fetch_all_no_law_links(self, mock_get):
        html_no_links = '''
        <html>
            <body>
                <div>No law links found</div>
            </body>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.text = html_no_links
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with self.assertRaises(ParseError) as context:
            WikiFetcher.fetch_all()
        
        self.assertIn("No law links found on the page", str(context.exception))

    @patch('fetchers.requests.get')
    def test_fetch_all_max_laws_limit(self, mock_get):
        def mock_get_side_effect(url, **kwargs):
            if "ספר_החוקים_הפתוח" in url:
                mock_response = Mock()
                mock_response.text = self.sample_law_list_html
                mock_response.raise_for_status.return_value = None
                return mock_response
            else:
                mock_response = Mock()
                mock_response.text = self.sample_html
                mock_response.raise_for_status.return_value = None
                return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        result = WikiFetcher.fetch_all(max_laws=1)
        
        self.assertEqual(len(result), 1)

    @patch('fetchers.WikiFetcher.fetch_one')
    @patch('fetchers.requests.get')
    def test_fetch_all_partial_failure(self, mock_get, mock_fetch_one):
        mock_response = Mock()
        mock_response.text = self.sample_law_list_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        def mock_fetch_side_effect(law_name, **kwargs):
            if law_name == "חוק הבטיחות":
                return "Law content"
            else:
                raise Exception("Fetch failed")
        
        mock_fetch_one.side_effect = mock_fetch_side_effect
        
        result = WikiFetcher.fetch_all()
        
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]['law_name'], "חוק הבטיחות")

    @patch('fetchers.WikiFetcher.fetch_one')
    @patch('fetchers.requests.get')
    def test_fetch_all_complete_failure(self, mock_get, mock_fetch_one):
        mock_response = Mock()
        mock_response.text = self.sample_law_list_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        mock_fetch_one.side_effect = Exception("All fetch failed")
        
        with self.assertRaises(FetcherError) as context:
            WikiFetcher.fetch_all()
        
        self.assertIn("Failed to fetch any laws", str(context.exception))


if __name__ == '__main__':
    unittest.main()