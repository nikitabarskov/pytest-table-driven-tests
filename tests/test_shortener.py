from dataclasses import dataclass

import pytest
from pydantic import HttpUrl, TypeAdapter

from nikitabarskov.url_shortener import shortener

TA = TypeAdapter(HttpUrl)


@dataclass
class GenerateShortCodeTestScenario:
    name: str
    url: HttpUrl
    expected_code: str


GENERATE_SHORT_CODE_TEST_SCENARIOS: list[GenerateShortCodeTestScenario] = [
    GenerateShortCodeTestScenario(
        name="default",
        url=TA.validate_python("https://domain.invalid/me"),
        expected_code="Yox6eL",
    ),
    GenerateShortCodeTestScenario(
        name="with_query_params",
        url=TA.validate_python("https://example.com/search?q=pytest&lang=en"),
        expected_code="RhtMxd",
    ),
    GenerateShortCodeTestScenario(
        name="with_fragment",
        url=TA.validate_python("https://example.com/docs#section"),
        expected_code="QNA5MP",
    ),
    GenerateShortCodeTestScenario(
        name="with_port",
        url=TA.validate_python("https://example.com:8080/api"),
        expected_code="OCBa3v",
    ),
    GenerateShortCodeTestScenario(
        name="with_subdomain",
        url=TA.validate_python("https://api.example.com/v1/users"),
        expected_code="sWu2mM",
    ),
    GenerateShortCodeTestScenario(
        name="with_encoded_chars",
        url=TA.validate_python("https://example.com/search?q=hello%20world"),
        expected_code="UFEDiJ",
    ),
]


@pytest.mark.parametrize(
    "scenario",
    GENERATE_SHORT_CODE_TEST_SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_generate_short_code(
    scenario: GenerateShortCodeTestScenario,
) -> None:
    actual = shortener.generate_short_code(scenario.url)
    assert actual == scenario.expected_code
