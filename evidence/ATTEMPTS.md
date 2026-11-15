# Beacon 001 local verification attempts

1. The first 30 unit checks passed. Construction review identified that malformed
   report fields should preserve a private hold across restart, not only in memory.
   The gate was repaired to save a minimal fallback report before surfacing the
   validation error. Two additional tests were added; all 32 pass.
2. Direct Chromium navigation to a local HTTP URL was blocked by environment
   policy (`ERR_BLOCKED_BY_ADMINISTRATOR`). Local `file:` navigation was also
   blocked. These were not application failures, and no policy bypass was used.
3. The self-contained, owner-requested HTML was rendered from already available
   bytes in an isolated Chromium page with `page.set_content`. Layout, interactions,
   downloads, permission gating, and no-JavaScript fallback were checked there.
   This verifies the rendered preview, not HTTP delivery or file navigation.
4. Desktop and mobile-sized screenshots were visually inspected. The supplied
   lamp photo remains the visual anchor. Public deployment, physical Safari,
   and actual message delivery are not claimed.

All cases are synthetic. These checks were performed by the same assistant that
authored the implementation, not by an independent reviewer.
