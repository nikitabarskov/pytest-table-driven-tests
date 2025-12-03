# URL Shortener

A FastAPI-based URL shortening service that demonstrates table-driven testing patterns with pytest.

## Features

- Shorten URLs using SHA-256 hash-based codes
- Redirect short codes to original URLs
- Idempotent URL shortening (same URL always generates the same code)
- SQLite database for persistence

## Requirements

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- [just](https://github.com/casey/just) command runner

## Installation

Install dependencies:

```bash
just configure
```

## Usage

Run the development server:

```bash
python main.py
```

The API will be available at `http://localhost:8080`.

### API Endpoints

**Shorten a URL**

```bash
POST /shorten
Content-Type: application/json

{
  "url": "https://example.com/some/long/url"
}
```

Response:

```json
{
  "url": "http://domain.invalid/Yox6eL",
  "original_url": "https://example.com/some/long/url",
  "created_at": "2025-12-03T10:30:00"
}
```

**Redirect to original URL**

```bash
GET /{code}
```

Returns a 307 redirect to the original URL or 404 if the code is not found.

## Development

### Running Tests

Run all tests:

```bash
just test
```

### Code Quality

Fix code formatting and linting issues:

```bash
just fix
```

Validate code without making changes:

```bash
just validate
```

### Project Structure

```
src/nikitabarskov/url_shortener/
├── app.py          # FastAPI application setup
├── routes.py       # API endpoint handlers
├── shortener.py    # URL shortening logic
└── db.py          # Database models and connection

tests/
├── test_shortener.py  # Table-driven tests for short code generation
└── test_routes.py     # Table-driven tests for API endpoints
```

## Testing Patterns

This project demonstrates table-driven testing with pytest. Tests are organized using dataclasses to define test scenarios:

```python
@dataclass
class GenerateShortCodeTestScenario:
    name: str
    url: HttpUrl
    expected_code: str

SCENARIOS = [
    GenerateShortCodeTestScenario(
        name="default",
        url=TA.validate_python("https://domain.invalid/me"),
        expected_code="Yox6eL",
    ),
    # More scenarios...
]

@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda s: s.name)
def test_generate_short_code(scenario):
    actual = shortener.generate_short_code(scenario.url)
    assert actual == scenario.expected_code
```

This approach provides:

- Clear test case organization
- Easy addition of new test cases
- Descriptive test names in output
- Type-safe test data structures
