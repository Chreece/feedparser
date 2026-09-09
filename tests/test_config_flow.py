"""Tests for the Feedparser config flow helpers."""

from datetime import time, timedelta

import pytest
import voluptuous as vol
from homeassistant.config_entries import OptionsFlowWithReload

from custom_components.feedparser.config_flow import (
    FeedparserOptionsFlow,
    _daily_update_time_from_input,
    _scan_interval_from_input,
)
from custom_components.feedparser.const import (
    CONF_DAILY_UPDATE_TIME,
    CONF_SCAN_INTERVAL,
)


def test_options_flow_reloads_config_entry() -> None:
    """Test that saving options uses Home Assistant automatic reload support."""
    assert issubclass(FeedparserOptionsFlow, OptionsFlowWithReload)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({"hours": 0, "minutes": 1}, {"hours": 0, "minutes": 1}),
        ({"hours": 1, "minutes": 30}, {"hours": 1, "minutes": 30}),
        (timedelta(hours=2), {"hours": 2, "minutes": 0}),
    ],
)
def test_scan_interval_normalization(value: object, expected: dict[str, int]) -> None:
    """Test refresh interval normalization."""
    assert _scan_interval_from_input({CONF_SCAN_INTERVAL: value}) == expected


def test_scan_interval_rejects_zero() -> None:
    """Test that a zero refresh interval is rejected instead of silently changed."""
    with pytest.raises(vol.Invalid):
        _scan_interval_from_input(
            {CONF_SCAN_INTERVAL: {"hours": 0, "minutes": 0}},
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("06:30:00", "06:30:00"),
        ("22:15", "22:15:00"),
        (time(4, 5, 6), "04:05:06"),
        ("", None),
        (None, None),
    ],
)
def test_daily_update_time_normalization(value: object, expected: str | None) -> None:
    """Test optional daily update time normalization."""
    assert _daily_update_time_from_input({CONF_DAILY_UPDATE_TIME: value}) == expected


def test_daily_update_time_rejects_invalid_value() -> None:
    """Test invalid daily update times are rejected by the config flow helper."""
    with pytest.raises(vol.Invalid):
        _daily_update_time_from_input({CONF_DAILY_UPDATE_TIME: "25:00"})
