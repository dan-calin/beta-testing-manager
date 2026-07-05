# Codebase Audit - 2026-07-05

Scope: manual review of the PyQt6 desktop app, Supabase integration, OBS worker,
export flow, dependency pins, and static checks.

Validation performed:

- `python -m compileall -q app main.py generate_assets.py` passed.
- Project venv `pip check` passed.
- Basic duration parsing smoke test passed for OBS timecodes and ISO datetimes.
- `pip list --outdated` found stale runtime packages, but this audit does not
  force broad runtime upgrades without GUI/OBS/Supabase regression testing.

## Follow-up Fixes Applied

Implemented after this audit:

- Supabase settings now ensure/store `user_id` when credentials are added later.
- Session loading and save/export work now run through the DB executor.
- Save messages distinguish local CSV export from cloud sync success/failure.
- Test item order is persisted with `sort_order` and the schema is migratable.
- Export now writes real CSV files instead of aligned text reports.
- Tray/app shutdown now stops the hotkey listener, OBS worker, and DB executor.
- A beginner-friendly `setup_and_run.bat` script was added.

## High Priority

### 1. Supabase setup after onboarding can leave `user_id` empty

Affected code:

- `app/views/settings_dialog.py` only calls `ensure_user()` when the username
  changes.
- `app/controllers/session_controller.py` creates new sessions from the stored
  `user_id`.
- `supabase_schema.sql` requires `sessions.user_id` to be `NOT NULL`.

Impact:

If a tester completes onboarding without Supabase, then later adds Supabase
credentials in Settings without changing the username, `user_id` stays empty.
Remote session loading returns nothing and remote session upserts can fail
against the schema. This makes cloud sync appear configured while writes are not
actually associated with a Supabase user.

Recommended implementation:

When Supabase credentials are saved, call `ensure_user(new_username)` whenever
there is a username and either `user_id` is empty, credentials changed, or the
username changed. Store the returned id and reload remote sessions.

Why it helps:

This fixes the most common "configure cloud later" path and prevents silent
sync failure/orphaned local sessions.

### 2. Network calls still run on the UI thread

Affected code:

- `SessionController.load_session()` calls `fetch_items_for_session()`
  synchronously.
- `save_session()` and `save_session_to_path()` call `upsert_session()`
  synchronously before returning to the UI.

Impact:

Slow or unreachable Supabase can freeze the main window while opening or saving
sessions. This is especially visible because the app is otherwise designed with
a background DB executor.

Recommended implementation:

Move session item fetches and save writes fully onto the existing executor.
Emit completion/error signals back to the UI, disable relevant actions while an
operation is in flight, and show explicit progress/failure messages.

Why it helps:

The app stays responsive even when Supabase is slow, offline, or misconfigured.

### 3. Save success messages do not verify cloud persistence

Affected code:

- `save_session()` and `save_session_to_path()` ignore the boolean result from
  `upsert_session()`.
- Batch item writes are submitted fire-and-forget through `_async()`.
- `_safe_run()` logs failures but does not feed them into `save_complete`.

Impact:

The UI can report "Saved" or "DB saved" even when Supabase is disconnected or a
write failed. CSV/text export may succeed while cloud sync failed, but the user
is not told that distinction.

Recommended implementation:

Track save results separately: local export success, session upsert success,
and item batch upsert success. Surface partial success states such as "Exported
locally; cloud sync failed: <reason>".

Why it helps:

Testers can trust save feedback and will know when data is local-only.

### 4. Manual item ordering is not persisted

Affected code:

- `SessionController.move_item()` changes only the in-memory list.
- `SupabaseService.fetch_items_for_session()` orders by `created_at`.
- `supabase_schema.sql` has no item ordering field.

Impact:

Moving items up/down works for the current view, but reopening the session from
Supabase restores creation order. Exports can also revert to the wrong order
after reload.

Recommended implementation:

Add a `sort_order` integer to `TestItem` and `test_items`. Update all affected
items after a reorder and fetch with `order("sort_order")`, falling back to
`created_at` for old rows.

Why it helps:

The tester's chosen workflow order survives reloads and sync.

## Medium Priority

### 5. Application shutdown lacks explicit cleanup

Affected code:

- `MainWindow.closeEvent()` hides to tray.
- Tray Quit calls `QApplication.quit`.
- OBS worker, global hotkey listener, and DB executor have no coordinated
  app-level shutdown path.

Impact:

The app can leave background hooks/workers running longer than necessary or
exit inconsistently during pending DB/OBS work.

Recommended implementation:

Add `shutdown()` methods on `MainWindow`, `OBSController`, and
`SessionController`. Stop the hotkey listener, stop OBS, and call
`ThreadPoolExecutor.shutdown(wait=False, cancel_futures=True)` from
`QApplication.aboutToQuit`.

Why it helps:

Quitting from the tray becomes deterministic and less likely to hang.

### 6. Export format and docs disagree

Affected code:

- `README.md` describes CSV export and `.csv` filenames.
- `Session.csv_filename()` returns `.txt`.
- `ExportController` writes a human-readable aligned text table.
- `CSV_COLUMNS` and `TestItem.to_csv_row()` are unused CSV-era code.

Impact:

Users expecting CSV import into Excel/Sheets receive a text report instead.
Unused CSV helpers make it unclear whether the current behavior is intended.

Recommended implementation:

Choose one path:

1. Restore true CSV export using Python's `csv` module and `CSV_COLUMNS`.
2. Keep the text report, rename UI/docs to "text report", and delete unused CSV
   helpers.

Why it helps:

Export behavior becomes predictable and the code stops carrying two competing
formats.

### 7. README claims overlay edge resizing, but the overlay only implements drag

Affected code:

- `README.md` says the overlay can be resized by dragging edges.
- `OverlayWindow` implements moving via title bar/body drag and saves geometry,
  but no edge-resize or `QSizeGrip` behavior is present.

Impact:

Users may try to resize the overlay and assume the feature is broken.

Recommended implementation:

Either add a resize affordance (`QSizeGrip` or custom edge hit-testing for the
frameless window) or update the README to describe only supported movement and
opacity controls.

Why it helps:

Documentation and UI behavior line up.

### 8. Runtime dependency pins are stale

Affected files:

- `requirements.txt`

Observed current pins versus available versions from `pip list --outdated`:

- `PyQt6` 6.7.1 -> 6.11.0
- `supabase` 2.7.4 -> 2.31.0
- `obsws-python` 1.6.1 -> 1.8.0
- `pynput` 1.7.7 -> 1.8.2
- `python-dateutil` 2.9.0 -> 2.9.0.post0

Impact:

Older pins can miss bug fixes, compatibility improvements, and security fixes
in transitive dependencies. Supabase especially has many transitive packages
that have moved forward.

Recommended implementation:

Upgrade in a branch, one integration area at a time:

- First patch-only `python-dateutil` to `2.9.0.post0` (done in this audit).
- Then test OBS with `obsws-python` 1.8.x.
- Then test hotkeys with `pynput` 1.8.x.
- Treat `PyQt6` and `supabase` as larger compatibility upgrades and test the
  full GUI/cloud flows.

Why it helps:

Keeps the app maintainable without mixing a broad dependency jump into an audit.

## Low Priority / Cleanup

### 9. Unused code and imports

Observed unused or likely unused items:

- `app/constants.py`: `CSV_COLUMNS`
- `app/models/test_item.py`: `CSV_COLUMNS` import and `to_csv_row()`
- `app/models/test_list.py`: `reorder()`
- `app/models/session.py`: `Optional` import
- `app/views/onboarding_dialog.py`: `QWidget` import
- `app/views/settings_dialog.py`: `QGroupBox`, `QMessageBox` imports
- `app/views/test_item_row.py`: `QAction` import
- `main.py`: `Qt` import
- `app/styles/dark_theme.py` and `light_theme.py`: `QWidget#toolbar` legacy QSS

Impact:

Small individually, but together they make it harder to tell what behavior is
current versus leftover.

Recommended implementation:

Run `ruff check` and remove unused imports. Decide whether `reorder()` and CSV
helpers are future-facing or stale; delete or cover them with tests.

Why it helps:

Reduces maintenance noise and keeps future audits focused on real behavior.

### 10. No automated test suite

Affected area:

- There is no `tests/` directory or configured test command.

Impact:

Core behaviors like duration calculation, export shape, hotkey formatting,
config loading, and Supabase sync edge cases rely on manual testing.

Recommended implementation:

Add `pytest` tests for:

- `TestItem.duration_formatted` with OBS and ISO timestamps.
- Export output shape and filename sanitization.
- Settings save behavior when Supabase credentials are added after onboarding.
- Reorder persistence once `sort_order` exists.

Why it helps:

Makes future cleanup and dependency upgrades less risky.

## Requirements Update Made

`requirements.txt` now separates runtime dependencies from audit/development
tools, updates `python-dateutil` to the current patch/post release, and adds:

- `ruff` for lint/static cleanup.
- `pytest` for the future test suite.
- `pip-audit` for dependency vulnerability checks.

The larger runtime upgrades above should be handled in a follow-up branch with
GUI, OBS, and Supabase regression testing.
