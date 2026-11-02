# Sky High proofs

Client proofing galleries served at https://proofs.skyhighphotography.com.au

- `shoots/<slug>.json`: one file per shoot (title, address, AutoHDR shoot id, photo list)
- `template.html`: gallery page design
- `build.py`: run `python3 build.py` to regenerate `site/`
- `site/`: what Netlify publishes (see `netlify.toml`)

Photos are shown straight from AutoHDR's preview server, so a shoot's gallery stops
showing photos if that shoot is deleted or archived in AutoHDR.

Client selections arrive through Netlify Forms (form name `proof-selection`).
