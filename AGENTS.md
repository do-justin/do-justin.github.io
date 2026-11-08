# Website working rules

- `content/public-profile.json` owns the reviewed public citation snapshot. Markdown pages own narrative prose. Never edit generated bibliography or display data.
- Validate with `python tools/site.py validate`; generate with `python tools/site.py generate`; test with `python -m unittest discover -s tests -v`.
- Build and preview through `tools/site.ps1` on Windows or Docker Compose on Linux. See README and `docs/maintenance.md`.
- Private inputs are read-only and external. Export proposals and metadata caches must stay outside this checkout. Never copy raw profiles, source inventories, private notes, machine paths, or credentials here, including fixtures and logs.
- A local draft is not approval for public disclosure. First public push, repository visibility/name changes, and first deployment require explicit user approval.
- Keep publication types/status distinct, all authors ordered, and only the explicit owner-author token bold. Preserve date precision. Do not infer delivery of a presentation from its date.
- Done means schema/tests/build pass, emitted artifact is inspected, and all three pages receive mobile/desktop visual and keyboard checks. Report unperformed checks.
