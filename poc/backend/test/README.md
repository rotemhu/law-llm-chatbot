# Unit Tests

This directory contains unit tests for the law-agent backend modules.

## Test Files

- `test_fetchers.py` - Tests for `fetchers.py`
- `test_parsers.py` - Tests for `parsers.py` 
- `test_storers.py` - Tests for `storers.py`
- `test_model_connectors.py` - Tests for `model_connectors.py`

## Running Tests

### Run All Tests
```bash
cd poc/backend
python -m pytest test/ -v
```

Or using the test runner:
```bash
cd poc/backend/test
python run_tests.py
```

### Run Individual Test Files
```bash
cd poc/backend
python -m unittest test.test_fetchers -v
python -m unittest test.test_parsers -v
python -m unittest test.test_storers -v  
python -m unittest test.test_model_connectors -v
```

## Test Coverage

The tests cover:
- **Fetchers**: WikiFetcher methods, error handling, network failures
- **Parsers**: Line type detection, section parsing, document structure parsing
- **Storers**: PineconeStorer initialization, storage operations, PostgreSQL storer
- **Model Connectors**: Embedding adapters (Google, HuggingFace, Local), factory patterns

## Dependencies

Make sure you have the required testing dependencies:
```bash
pip install pytest requests beautifulsoup4
```

The tests use mocking extensively to avoid external API calls and dependencies.