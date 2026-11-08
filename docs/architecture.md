# Architecture

The public snapshot owns released professional facts and citations. Markdown
owns website prose; the featured ID list owns selection. These inputs are
independent of the private system from which a reviewed subset may be exported.
No private source inventory or machine-specific path belongs in this repository.

The content CLI validates a strict JSON Schema and semantic constraints, then
deterministically generates BibTeX, public display data and citation downloads.
The existing CV PDF is versioned independently and checked against its reviewed
SHA-256 and page count; builds do not rewrite it. Native al-folio default/page
layouts, navigation, styles and scripts remain in the pinned theme gem. The
homepage uses a local layout with profile/credentials beside biography/publications,
informed by ACAD and Minimal Light. Other local overrides cover the bibliography
display, a Sass extension, theme-asset cache resolution and a skip link.
The four gem-owned overrides are acknowledged in `.al-folio-overrides.yml`.
The head and script includes load only the styles and navigation used here;
code-copy buttons, notebooks, tooltips, blog and teaching styles are omitted.
The browser policy permits same-origin scripts and assets, blocks inline
scripts, network API calls, embeds and form submissions, and retains inline
styles for the native theme. Metadata and canonical URLs still use al-folio.
The upgrade audit's optional icon-plugin notice is intentional: the site uses
text links and native navigation rather than an icon library.

Each work has a stable ID and distinct kind/status. Ordered authors and an
explicit owner-author index control highlighting. Article DOI uniqueness does
not apply to supplement DOIs shared by separate conference abstracts. Relations
connect the article/preprint/abstract/presentation records without merging them.
Online and issue dates retain their available precision.

The Docker build image contains only dependency inputs. Runtime mounts only the
website checkout and disables network access. An explicit static-file boundary
and output audit reject unintended pages/assets. Reviewed images and the
existing CV are the only permitted binary assets.

Export and refresh are local-only operations with explicit external staging
paths. They never write to the private career system. CI never runs them.
Provider outages produce review reports while preserving known-good content.
Refresh refuses HTTP redirects and caps both downloaded and cached payloads.
Google Scholar totals are a dated, verified snapshot; Crossref per-work counts
are labeled separately. Neither metric source determines authorship or status.
