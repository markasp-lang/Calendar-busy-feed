"""
Fetches Mark's existing public iCloud calendar feed (already published via
Calendar.app -> Share Calendar -> Public Calendar) and writes out a
stripped-down version that keeps only timing information.

Every event's title, location, description and attendees are dropped and
replaced with the single word "Busy". Only start/end time, recurrence rules
and the event's unique ID are kept, so the output tells you WHEN Mark is
busy without saying WHAT he's doing.

The source URL is read from the ICLOUD_ICS_URL environment variable (set as
a GitHub Actions secret) so it never appears in the code or commit history.
"""

import os
import sys
from datetime import datetime, timezone

import requests
from icalendar import Calendar, Event

OUTPUT_PATH = "busy.ics"

# Only these fields are carried over from the original event.
# Anything not in this list (title, location, description, attendees,
# organizer, URL, notes, alarms, ...) is dropped.
ALLOWED_KEYS = [
    "UID",
    "DTSTART",
    "DTEND",
    "DURATION",
    "RRULE",
    "EXDATE",
    "RECURRENCE-ID",
    "SEQUENCE",
    "TRANSP",
]


def fetch_source(url: str) -> bytes:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content


def redact(raw_ics: bytes) -> bytes:
    source_cal = Calendar.from_ical(raw_ics)

    out_cal = Calendar()
    out_cal.add("prodid", "-//calendar-busy-feed//redacted//EN")
    out_cal.add("version", "2.0")
    out_cal.add("calscale", "GREGORIAN")
    out_cal.add("x-wr-calname", "Busy")

    count = 0
    for component in source_cal.walk():
        if component.name != "VEVENT":
            continue

        new_event = Event()
        for key in ALLOWED_KEYS:
            if key in component:
                new_event[key] = component[key]

        new_event["SUMMARY"] = "Busy"
        new_event["STATUS"] = "CONFIRMED"
        new_event.add("dtstamp", datetime.now(timezone.utc))

        out_cal.add_component(new_event)
        count += 1

    print(f"Redacted {count} event(s)")
    return out_cal.to_ical()


def main() -> None:
    source_url = os.environ.get("ICLOUD_ICS_URL")
    if not source_url:
        print("ICLOUD_ICS_URL is not set", file=sys.stderr)
        sys.exit(1)

    raw = fetch_source(source_url)
    redacted = redact(raw)

    with open(OUTPUT_PATH, "wb") as f:
        f.write(redacted)

    print(f"Wrote {OUTPUT_PATH} ({len(redacted)} bytes)")


if __name__ == "__main__":
    main()
