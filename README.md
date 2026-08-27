# calendar-busy-feed

Takes Mark's existing public iCloud calendar link (already set up via
Calendar.app -> Share Calendar -> Public Calendar) and republishes it every
4 hours as a stripped-down feed containing only "Busy" blocks: no titles,
no locations, no descriptions, no attendees. Runs entirely on GitHub's free
infrastructure via GitHub Actions -- nothing needs to stay running on
Mark's own Mac.

## One-time setup

1. **Create the repository.**
   On github.com, click "New repository". Name it something like
   `calendar-busy-feed`. Leave it **Public** (this keeps GitHub Actions
   free and unlimited -- the code and the redacted output are harmless to
   have visible; the real calendar link never appears in either).

2. **Upload these four files**, keeping the folder structure exactly as
   given:
   - `redact_calendar.py`
   - `requirements.txt`
   - `.github/workflows/update.yml`
   - `README.md` (this file)

   Easiest way: on the repository's main page, click "Add file" ->
   "Upload files", and drag all four in at once (GitHub preserves the
   `.github/workflows/` folder path automatically).

3. **Add the secret.**
   Go to the repository's Settings tab -> "Secrets and variables" ->
   "Actions" -> "New repository secret".
   - Name: `ICLOUD_ICS_URL`
   - Value: paste your existing iCloud public calendar link (the one
     starting `https://p30-caldav.icloud.com/published/...`, with
     `webcal://` swapped for `https://` if needed -- the same link
     that's currently feeding the "Home" calendar in Google Calendar).

   This value is never visible in the code, in commit history, or to
   anyone browsing the repository -- only the workflow can read it while
   it's running.

4. **Run it once by hand.**
   Go to the Actions tab -> "Update busy calendar feed" (on the left) ->
   "Run workflow" button -> Run workflow. After it finishes (about
   30 seconds), a new file called `busy.ics` should appear in the
   repository's file list.

5. **Get the feed URL.**
   Click on `busy.ics` in the repository, then "Raw". The address bar
   will show something like:

   `https://raw.githubusercontent.com/<your-username>/calendar-busy-feed/main/busy.ics`

   That's the URL to give to Google Calendar.

6. **Point Google Calendar at it.**
   In Google Calendar (signed in as the Palisade account), first remove
   the old direct import: hover over "Home" in the sidebar -> three-dot
   menu -> "Unsubscribe from calendar". Then: "Other calendars" (+) ->
   "From URL" -> paste the raw.githubusercontent.com URL from step 5.

From then on, the workflow re-fetches your real calendar every 4 hours and
updates `busy.ics` automatically -- no further action needed. You can
always trigger an extra run manually from the Actions tab if you want an
update sooner (e.g. after adding a same-day appointment).

## What gets kept vs. dropped

Kept: event start/end time, recurrence rules, and a unique ID (so repeated
and updated events sync correctly).

Dropped: title, location, description, attendees, organizer, any notes or
alarms. Every event's title becomes the single word "Busy".

## If something looks wrong

Check the Actions tab -> the most recent run of "Update busy calendar
feed" -> click into it to see the log. The most common issue is the
`ICLOUD_ICS_URL` secret being missing, mistyped, or pointing at a link
that's no longer public (e.g. if calendar sharing was turned off in
Calendar.app).
