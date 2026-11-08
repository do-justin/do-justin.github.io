# Justin Do - research website

A compact academic site using al-folio v1.2, with About, Publications, Research,
and the owner's current CV PDF. Public citation data are reviewed snapshots;
the build does not contact bibliographic services or read private career files.

## Local workflow

On Windows, use Ubuntu WSL 2 with Docker Engine and Compose. From this checkout:

```powershell
.\tools\site.ps1 -Action Setup
.\tools\site.ps1 -Action Validate
.\tools\site.ps1 -Action Build
.\tools\site.ps1 -Action Preview
```

Preview serves `http://127.0.0.1:8080`; Ctrl+C stops it. Setup installs dependencies
into a local Docker image. Build runs with container networking disabled and
generates `_site/`. Python on Windows is used for the preview server and optional
content commands; validation requires jsonschema and the optional CV check
requires pypdf. Both are installed in the Docker image.

The same Linux/CI workflow is:

```bash
docker compose build
docker compose run --rm site
```

The image is pinned by digest; Ruby dependencies are locked in `Gemfile.lock`.
Python requirements include pinned transitive dependencies. Docker does not need access to private
sources, OneDrive, API credentials, or a publication service during rendering.

## What to edit

| Input | Purpose | Generated output |
|---|---|---|
| `content/public-profile.json` | Reviewed public identity, education, honors, appointments, citations, links and dated metrics | Bibliography, display data and BibTeX downloads |
| `_pages/about.md`, `_pages/research.md` | Biography and research prose | Website pages |
| `_data/featured.yml` | Stable IDs selected for the homepage | Selected publication list |
| `_sass/_site.scss` | Small style adjustments to the native theme | Main stylesheet |
| `_layouts/academic-home.liquid` | Compact homepage: profile/credentials beside biography/publications | Homepage structure |
| `assets/pdf/Justin_Do_CV.pdf`, `content/cv.json` | Existing CV and reviewed file hash/version | Copied unchanged into the site |

Do not hand-edit `_bibliography/papers.bib`, `_data/publications.json`,
`assets/bib/`, or `_site/`.

```powershell
python tools/site.py validate
python tools/site.py generate
python -m unittest discover -s tests -v
python tools/site.py audit
```

The container build checks the existing PDF without rewriting it. See
[maintenance](docs/maintenance.md) for reviewed imports and metadata proposals,
and [architecture](docs/architecture.md) for source and privacy boundaries.

## Verification and publication

CircleCI runs `.github/workflows/check.yml` through its GitHub Actions workflow
support. Each push validates content, runs tests, builds offline, audits output,
and requires unchanged tracked inputs. CI needs no publication API credentials
or private career files. See [maintenance](docs/maintenance.md#continuous-integration)
for manual runs and branch selection.

Publication is manual. `tools/publish.ps1` reruns the build and audit, then
prepares the static files for the separate public user-site repository. Add
`-Publish` to upload them to its `gh-pages` branch. GitHub's managed Pages workflow
serves that branch without rebuilding Jekyll; CircleCI runs checks only.
Publication requires the owner's approval. See the maintenance release steps.

No blog, news feed, teaching directory, people directory, analytics, or automatic
publication acceptance is enabled. See [third-party notices](THIRD_PARTY.md).
