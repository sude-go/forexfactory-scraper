import pytest

from src.forexfactory.normalizer import is_all_day_label, normalize_event


@pytest.mark.parametrize("label", ["All Day", "Day 1", "Day 2", "Tentative"])
def test_all_day_labels(label):
    assert is_all_day_label(label)


@pytest.mark.parametrize("label", ["", None, "3:50pm", "12:30am", "07:10", "19:10:00", "9pm"])
def test_clock_times_are_not_all_day(label):
    assert not is_all_day_label(label)


def _raw(time, **kw):
    return {"date": "2026-10-12", "time": time, "currency": "CAD", "impact": "Non-Economic",
            "event": "Bank Holiday", **kw}


def test_all_day_event_is_kept_at_midnight_utc_with_its_label():
    # Sayfa saat dilimi ne olursa olsun tüm gün olay listelendiği günün 00:00 UTC'sidir
    for tz in ("UTC", "Europe/Istanbul", "America/New_York"):
        event = normalize_event(_raw("All Day"), tz)
        assert event["datetime_utc"] == "2026-10-12T00:00:00+00:00"
        assert event["date"] == "2026-10-12"
        assert event["time"] == "All Day"


def test_day_n_label_is_all_day_too():
    event = normalize_event(_raw("Day 1", currency="ALL", event="IMF Meetings", impact="Low"), "Europe/Istanbul")
    assert event["datetime_utc"] == "2026-10-12T00:00:00+00:00"
    assert event["time"] == "Day 1"


def test_timed_event_is_unchanged():
    event = normalize_event(_raw("3:50pm", impact="Low", event="MPC Member Mann Speaks"), "Europe/Istanbul")
    assert event["datetime_utc"] == "2026-10-12T12:50:00+00:00"
    assert event["time"] == "15:50:00"
