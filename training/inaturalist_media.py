#!/usr/bin/env python3
"""Safe iNaturalist image-variant selection for research review.

iNaturalist photo URLs commonly point at square/thumbnail derivatives.  The
original derivative is the largest published iNaturalist variant (up to
2048 px on the longest edge); it is not necessarily the camera's full source.
"""
from urllib.parse import urlsplit, urlunsplit
import re

ALLOWED_HOSTS = {
    "static.inaturalist.org",
    "inaturalist-open-data.s3.amazonaws.com",
    "inaturalist-open-data.s3.us-west-2.amazonaws.com",
}
VARIANTS = {"square", "thumb", "small", "medium", "large", "original"}
PHOTO_PATH = re.compile(r"^/photos/([0-9]+)/(square|thumb|small|medium|large|original)\.(jpe?g|png|webp)$", re.IGNORECASE)


def original_image_url(url: str, photo_id: str | int | None = None) -> str:
    """Return the iNaturalist original derivative URL, rejecting ambiguous URLs."""
    if not isinstance(url, str) or not url:
        raise ValueError("iNaturalist photo URL required")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.username or parsed.password
            or parsed.port not in (None, 443) or parsed.fragment
            or (parsed.hostname or "").lower() not in ALLOWED_HOSTS):
        raise ValueError("unsupported or unsafe iNaturalist image URL")
    match = PHOTO_PATH.fullmatch(parsed.path)
    if not match:
        raise ValueError("unsupported iNaturalist photo URL path or image extension")
    found_id, _variant, extension = match.groups()
    if photo_id is not None and str(photo_id) != found_id:
        raise ValueError("photo ID does not match image URL")
    path = f"/photos/{found_id}/original.{extension.lower()}"
    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, ""))


def is_original_image_url(url: str, photo_id: str | int | None = None) -> bool:
    try:
        return original_image_url(url, photo_id) == url
    except (TypeError, ValueError):
        return False


def normalize_if_inaturalist(url: str, photo_id: str | int | None = None) -> str:
    """Upgrade known iNaturalist URLs; leave other HTTPS sources untouched."""
    parsed = urlsplit(url or "")
    if (parsed.scheme == "https"
            and (parsed.hostname or "").lower() in ALLOWED_HOSTS):
        return original_image_url(url, photo_id)
    return url
