from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlmodel import Session

from nikitabarskov.url_shortener import shortener
from nikitabarskov.url_shortener.db import ShortenedURL, get_session

router = APIRouter()


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    url: str
    original_url: str
    created_at: datetime


@router.post("/shorten")
def get(
    request: ShortenRequest,
    session: Session = Depends(get_session),
) -> ShortenResponse:
    created_at = datetime.now()
    url = request.url.unicode_string()
    code = shortener.generate_short_code(request.url)
    shortened_url = session.get(
        ShortenedURL,
        code,
    )

    if shortened_url and shortened_url.original_url == url:
        return ShortenResponse(
            url=f"http://domain.invalid/{shortened_url.code}",
            original_url=shortened_url.original_url,
            created_at=shortened_url.created_at,
        )

    shortened_url = ShortenedURL(
        code=code,
        original_url=url,
        created_at=created_at,
    )

    session.add(shortened_url)
    session.commit()
    session.refresh(shortened_url)
    return ShortenResponse(
        url=f"http://domain.invalid/{code}",
        original_url=url,
        created_at=created_at,
    )


@router.get(
    "/{code}",
    response_model=None,
)
def redirect_to_original(
    code: str,
    session: Session = Depends(get_session),
) -> RedirectResponse:
    shortened_url = session.get(
        ShortenedURL,
        code,
    )

    if not shortened_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short URL 'https://domain.invalid/{code}' is not found",
        )

    return RedirectResponse(
        url=shortened_url.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
