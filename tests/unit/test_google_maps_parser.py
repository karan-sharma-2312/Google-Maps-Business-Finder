"""Unit tests for Google Maps parser helpers."""

from app.scrapers.google_maps.parser import (
    extract_coordinates_from_maps_url,
    parse_rating,
    parse_reviews_count,
)


def test_extract_coordinates_from_maps_url_success() -> None:
    url = "https://www.google.com/maps/place/Test/@40.7128,-74.0060,17z/data=!3m1!4b1"
    latitude, longitude = extract_coordinates_from_maps_url(url)

    assert latitude == 40.7128
    assert longitude == -74.0060


def test_extract_coordinates_from_maps_url_missing() -> None:
    latitude, longitude = extract_coordinates_from_maps_url("https://www.google.com/maps/place/Test")

    assert latitude is None
    assert longitude is None


def test_parse_rating() -> None:
    assert parse_rating("4.7 stars") == 4.7
    assert parse_rating("Rated 4,3") == 4.3
    assert parse_rating(None) is None


def test_parse_reviews_count() -> None:
    assert parse_reviews_count("(1,234)") == 1234
    assert parse_reviews_count("1.234 reviews") == 1234
    assert parse_reviews_count("No reviews") is None
