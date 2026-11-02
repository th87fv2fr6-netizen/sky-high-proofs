# Sky High proofs

Client proofing galleries served at https://proofs.skyhighphotography.com.au

- `shoots/<slug>.json`: one file per shoot (title, address, AutoHDR shoot id, photo list)
- `template.html`: gallery page design
- `build.py`: run `python3 build.py` to regenerate `site/`
- `site/`: what Netlify publishes (see `netlify.toml`)

Photos are shown straight from AutoHDR's preview server, so a shoot's gallery stops
showing photos if that shoot is deleted or archived in AutoHDR.

Client selections arrive through Netlify Forms (form name `proof-selection`).

## Automation
- `scrape_autohdr.js`: run in the logged-in browser pane on autohdr.com/listings; returns every active listing's shoot id and photos.
- `add_shoot.py listings.json`: adds new listings to `shoots/` (once a listing's photo list is stable across two runs) and updates changed ones. State for listings still settling is kept in `state.json`.
- Then `python3 build.py`, commit and push; Netlify deploys automatically.
