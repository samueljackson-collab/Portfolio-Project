# ElderPhoto

ElderPhoto is a gentle photo management experience designed for seniors. It combines clear UI patterns, high-contrast controls, and automated organization (albums, calendar, and backups) so families can share memories without friction.

## Accessibility Commitments

- **High-contrast palette:** Primary actions use #1d4ed8 on white (contrast ratio 4.65:1) which satisfies WCAG AA for large text and meets the needs documented in our usability testing. Secondary actions use dark text on pale backgrounds with ≥7:1 contrast.
- **Touch-friendly controls:** Buttons and navigation targets are at least 52×52px with generous spacing.
- **Keyboard support:** Every interactive element includes focus outlines and logical tab order.
- **Readable typography:** Base font size is 18px with scale presets that work up to 200% browser zoom without layout breakage.

## Key Workflows

1. **Upload:** Drag-and-drop or single-click upload with immediate validation feedback.
2. **Browse:** Grid view streams thumbnails through authenticated requests so protected endpoints remain secure.
3. **Calendar:** Server-side aggregation groups photos per day and exposes quick counts for each calendar tile.
4. **Albums:** Automatic location-based albums prevent duplicate creation thanks to a `(owner_id, name)` unique constraint.
5. **Backups:** The `/backup/sync` endpoint triggers asynchronous replication to secondary storage. A CLI (`backend/scripts/backup_sync.py`) provides non-interactive automation with `--yes` and `--verify` safeguards.

## Running Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd ../frontend
npm install
npm run dev
```

Visit `http://localhost:5173/photos` after logging in to explore the ElderPhoto experience.
