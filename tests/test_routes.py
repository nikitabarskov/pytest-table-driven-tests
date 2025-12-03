import difflib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

import pytest
from deepdiff import DeepDiff
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import HttpUrl, TypeAdapter
from sqlmodel import Session

from nikitabarskov.url_shortener.db import ShortenedURL
from nikitabarskov.url_shortener.routes import ShortenRequest, ShortenResponse

TA = TypeAdapter(HttpUrl)


@dataclass
class ShortenTestScenario:
    name: str
    urls: list[HttpUrl]
    expected_status_code: int
    expected_results: list[ShortenResponse | None] = field(default_factory=list)


SHORTEN_TEST_SCENARIOS: list[ShortenTestScenario] = [
    ShortenTestScenario(
        name="default",
        urls=[
            TA.validate_python("https://domain.invalid/me"),
        ],
        expected_status_code=status.HTTP_200_OK,
        expected_results=[
            ShortenResponse(
                url="http://domain.invalid/Yox6eL",
                original_url="https://domain.invalid/me",
                created_at=datetime.now(),
            )
        ],
    ),
    ShortenTestScenario(
        name="idempotency",
        urls=[
            TA.validate_python("https://domain.invalid/idempotent"),
            TA.validate_python("https://domain.invalid/idempotent"),
        ],
        expected_status_code=status.HTTP_200_OK,
        expected_results=[
            ShortenResponse(
                url="http://domain.invalid/39CVx5",
                original_url="https://domain.invalid/idempotent",
                created_at=datetime.now(),
            ),
            ShortenResponse(
                url="http://domain.invalid/39CVx5",
                original_url="https://domain.invalid/idempotent",
                created_at=datetime.now(),
            ),
        ],
    ),
]


@pytest.mark.parametrize(
    "scenario",
    SHORTEN_TEST_SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_shorten(scenario: ShortenTestScenario, client: TestClient) -> None:
    for url, expected_result in zip(
        scenario.urls, scenario.expected_results, strict=True
    ):
        response = client.post(
            "/shorten",
            json=ShortenRequest(
                url=url,
            ).model_dump(mode="json"),
        )
        assert response.status_code == scenario.expected_status_code

        actual = ShortenResponse.model_validate_json(response.content)
        diff = DeepDiff(
            actual,
            expected_result,
            exclude_paths=["created_at"],
        )
        if diff:
            if expected_result:
                assert False, "".join(
                    difflib.unified_diff(
                        actual.model_dump_json(indent=2).splitlines(keepends=True),
                        expected_result.model_dump_json(indent=2).splitlines(
                            keepends=True
                        ),
                    )
                )


def setup_db(session: Session) -> None:
    session.add_all(
        [
            ShortenedURL(
                code="ABCDEF",
                original_url="https://domain.invalid",
                created_at=datetime(2025, 12, 2, 0, 0, 0),
            ),
        ]
    )
    session.commit()
    return


@dataclass
class RedirectTestScenario:
    name: str
    setup: Callable[[Session], Any]
    code: str
    setup_url: HttpUrl | None = None
    expected_status_code: int = status.HTTP_307_TEMPORARY_REDIRECT
    expected_redirect_url: str | None = field(default=None)


REDIRECT_TEST_SCENARIOS: list[RedirectTestScenario] = [
    RedirectTestScenario(
        name="successful-redirect",
        setup=setup_db,
        code="ABCDEF",
        expected_status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        expected_redirect_url="https://domain.invalid",
    ),
    RedirectTestScenario(
        name="non-existenting-code",
        setup=lambda session: None,
        code="non-existing-code",
        expected_status_code=status.HTTP_404_NOT_FOUND,
        expected_redirect_url=None,
    ),
]


@pytest.mark.parametrize(
    "scenario",
    REDIRECT_TEST_SCENARIOS,
    ids=lambda scenario: scenario.name,
)
def test_redirect(
    scenario: RedirectTestScenario, session: Session, client: TestClient
) -> None:
    scenario.setup(session)
    response = client.get(f"/{scenario.code}", follow_redirects=False)
    assert response.status_code == scenario.expected_status_code
    if scenario.expected_redirect_url is not None:
        assert response.headers.get("location") == scenario.expected_redirect_url
