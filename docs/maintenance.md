# Maintaining the website

## Add or correct a work

1. Verify the final publication, complete authors, publication type/status,
   available dates, and links. Reconcile career facts in their authorized source
   workspace when needed. Preserve an existing work ID when a title/status changes.
2. Prepare the proposed public bundle outside this checkout. The generic export
   adapter accepts an explicit private profile and external selection file:

   ```powershell
   python tools/site.py export --profile $profilePath --selection $selectionPath --output $candidatePath
   ```

   The selection allowlists upstream work IDs and public IDs, kinds/statuses,
   public sources, links and editorial additions. It supplies reviewed author
   mappings when an ordered upstream string is ambiguous. Unknown source fields
   are never copied. First-author disagreement blocks export. Education and
   appointments, when included, contain only reviewed title/organization/dates.
3. Review the external bundle for facts and disclosure, then import it:

   ```powershell
   python tools/site.py import --bundle $candidatePath --reviewed
   .\tools\site.ps1 -Action Build
   .\tools\site.ps1 -Action Preview
   ```

4. Inspect authors, classification, dates, the PDF, homepage selection and links.
   Review the Git diff before committing or releasing.

The public JSON itself can receive a reviewed correction; generated bibliography
files are never separate editable masters. The existing CV is maintained separately. No private profile writeback
or document-generation pipeline is invoked.

## Check known identifiers

Set an external output directory and use the chosen public contact email:

```powershell
python tools/site.py refresh --output $refreshPath --email justin.do@students.jefferson.edu
```

This calls exact DOI/PMID endpoints in Crossref and PubMed, caches responses for
seven days, uses sequential conservative request rates, 20-second timeouts, and
at most three attempts. Redirects are refused before requesting their target;
the CLI uses exact provider endpoints. A long Retry-After stops a lookup rather than retrying
too soon. `metadata-proposals.json` retains approved/candidate values, meaningful
field changes, authorship alerts, and correction/retraction relationships.
Missing/incomplete records and errors do not delete or overwrite approved works.
Supplement DOIs are not used to replace individual abstract metadata.

Review results against final publication evidence, update the approved public
snapshot, and rebuild. Never publish private candidate diffs in issues or PRs.
No paid API, Scholar scraper, or scheduled workflow is required.

ACAD's automatic Scholar integration uses the third-party `scholarly` scraper
and a scheduled GitHub Action, rather than an official Scholar API. This site
uses a direct profile button and reviewed, dated Scholar metrics. Crossref's
per-DOI counts cover a different citation network, so they must not be relabeled
as Scholar totals or used to silently replace the Scholar h-index/i10-index.
See [ACAD's crawler](https://github.com/RayeRen/acad-homepage.github.io/blob/main/google_scholar_crawler/main.py)
and [Crossref's coverage explanation](https://www.crossref.org/documentation/cited-by/).

## Biography, featured work, and metrics

Edit the two Markdown pages for narrative changes, checking contributions and
findings against controlling sources. Change `_data/featured.yml` to select
homepage works. Never turn an accepted presentation into a delivered one solely
because its date has passed.

For conference outputs, store verified program codes in `abstract_number`,
presentation format in `subtype`, and city/region in `location`. A meeting date
range uses `date` plus `end_date`; do not invent a specific presentation day.
Keep journal page numbers in `pages`. Submission IDs, URL database IDs, screen
numbers and presentation slots are not interchangeable with abstract numbers.
Unknown or unassigned abstract numbers remain omitted until verified.

Verify the intended Google Scholar profile before updating totals, h-index and
i10-index in `identity.metrics`; record the source URL and verification date.
Per-work citation snapshots identify Crossref and their own check date. Counts
from these sources need not agree. Unavailable metrics are omitted, not set to zero.

## Browser and PDF QA

To update the CV, replace `assets/pdf/Justin_Do_CV.pdf` with the owner's chosen
PDF and update `content/cv.json` with its version, page count and SHA-256 after
review. Use `Get-FileHash -Algorithm SHA256 assets/pdf/Justin_Do_CV.pdf` to obtain
the hash. `python tools/site.py cv` checks the manifest and PDF without changing
either file. The current file is the November 8, 2026 residency CV, with the owner-approved
MACCE ePoster status corrected to presented. Review its contact/application details
before release.

Capture About, Research and Publications at desktop and 320 px widths. Check
navigation, keyboard focus, Summary/Related outputs disclosure, portrait sizing,
long author lists, text reflow and contrast. Render every PDF page with Poppler
and inspect it before release.

Optional pinned axe-core checks operate on a disposable copy:

```powershell
python tools/prepare_a11y.py
python -m http.server 8081 --bind 127.0.0.1 --directory .build/a11y-site
```

The first command verifies the official package archive's SHA-512. Open each
main page on port 8081 and inspect the `qa-a11y-result` JSON element. This leaves
the production `_site` artifact unchanged. Automated results supplement manual
keyboard, visual, and content review.

## Continuous integration

CircleCI's `build-and-test` pipeline uses the existing
`.github/workflows/check.yml`; there is no separate CircleCI build script.
The enabled GitHub App trigger runs on all pushes. A manual run must use the
same branch for **Config Source** and **Checkout Source** so the workflow and
tested code come from the same revision. During development, use the PR branch;
after merging, use `main`. Update any saved branch selection at that point.

In a successful run, confirm the dependency build, content validation, CV check,
unit tests, offline Jekyll build, output audit, and unchanged-input check actually
executed. CircleCI's GitHub Actions compatibility is in preview; inspect step
logs after workflow changes rather than relying only on the status badge.
The GitHub PR check is named `ci/circleci: check`.

CI does not need a CircleCI personal token. Optional local API access for
inspecting or rerunning jobs belongs in a user credential store outside this
checkout, never in source files, workflow variables, or build artifacts.

## Release and rollback

The configured URL is the intended deployment target, not a claim of a live site.
Before release, confirm the PR's current commit passes CircleCI, review the
complete source/history and artifact, and inspect all three pages and the CV.
CircleCI checks do not test the GitHub Pages deployment. The publishing account
must be able to start GitHub Actions jobs before using the manual deploy workflow;
an account-level Actions restriction must be resolved first.

After explicit first-release approval, prepare the user-site remote, enable
GitHub Pages with Actions, and run the manual deploy workflow on approved `main`
content. The private development repository cannot pass that workflow's
repository guard. Verify public HTTPS, canonical URLs, sitemap, 404 behavior,
and the hosted pages after deployment. Those checks cannot be completed locally.

For rollback, revert to the last approved content commit and rerun the same
checks and manual deployment. Do not add another deployment mechanism or a
competing gh-pages branch workflow. Scheduled checks remain off until requested.
