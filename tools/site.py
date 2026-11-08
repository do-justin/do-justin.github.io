"""Small public-content pipeline. Network access is confined to refresh."""
from __future__ import annotations

import argparse
import calendar
import copy
from datetime import date, datetime
import hashlib
from html import escape
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
from email.utils import parsedate_to_datetime
from datetime import timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit, unquote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "content/public-profile.json"
GROUPS = [("article", "Journal articles"), ("preprint", "Preprints"),
          ("published_abstract", "Published conference abstracts"), ("presentation", "Selected presentations")]
STATUS = {"published": "Published", "preprint": "Preprint · not peer reviewed",
          "accepted": "Accepted", "in_press": "In press", "presented": "Presented"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def external_path(path):
    path = Path(path).resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError("Private staging/input must be outside the website checkout")
    return path


def valid_date(value):
    parts = value.split("-")
    date(int(parts[0]), int(parts[1]) if len(parts) > 1 else 1,
         int(parts[2]) if len(parts) > 2 else 1)


def normalize_doi(value):
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I).lower()


def validate(data, today=None):
    validator = Draft202012Validator(read_json(ROOT / "schemas/public-profile.schema.json"), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda e: str(list(e.path)))
    if errors:
        raise ValueError("Schema: " + "; ".join(f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors))
    ids, dois = set(), set()
    today = today or date.today()
    metrics = data['identity'].get('metrics')
    if metrics and date.fromisoformat(metrics['as_of']) > today:
        raise ValueError('Citation metrics cannot have a future verification date')
    for w in data["works"]:
        if w.get('citations') and date.fromisoformat(w['citations']['as_of']) > today:
            raise ValueError('Citation count cannot have a future verification date')
        if w["id"] in ids:
            raise ValueError("Duplicate work ID: " + w["id"])
        ids.add(w["id"])
        for key in ("date", "online_date", "issue_date"):
            if key in w:
                valid_date(w[key])
        idx = w["owner_author_index"]
        if idx >= len(w["authors"]) or w["authors"][idx]["display"] not in data["identity"]["author_aliases"]:
            raise ValueError("Invalid owner author: " + w["id"])
        for a in w["authors"]:
            if any(c in a["display"] + a["bibtex"] for c in "<>\\\n\r"):
                raise ValueError("Author tokens must be plain text")
            if " and " in a["bibtex"] and not (a["bibtex"].startswith("{") and a["bibtex"].endswith("}")):
                raise ValueError("Group authors require an explicit literal BibTeX token")
        allowed = {"article": {"published", "accepted", "in_press"}, "preprint": {"preprint"},
                   "published_abstract": {"published"}, "presentation": {"accepted", "presented"}}
        if w["status"] not in allowed[w["kind"]]:
            raise ValueError("Incompatible work type/status: " + w["id"])
        if w["status"] == "presented" and date.fromisoformat(w["date"] + "-01" * (2 - w["date"].count("-"))) > today:
            raise ValueError("A future event cannot be presented")
        if w.get("doi_scope") == "supplement" and w["kind"] != "published_abstract":
            raise ValueError("Supplement DOI is only valid on a published abstract")
        if w["kind"] == "article" and w.get("doi"):
            key = normalize_doi(w["doi"])
            if key in dois:
                raise ValueError("Duplicate article DOI")
            dois.add(key)
    for w in data["works"]:
        if any(r not in ids or r == w["id"] for r in w["related_ids"]):
            raise ValueError("Unknown/self related work: " + w["id"])
    serialized = json.dumps(data, ensure_ascii=False)
    if re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]|/home/|/Users/|(?:api[_-]?key|password|access_token)\s*[\"']?\s*:", serialized, re.I):
        raise ValueError("Private path or credential marker in public data")
    return data


def bib_escape(value):
    # Unicode is preserved; brace syntax and comment characters are escaped.
    return str(value).replace("\\", r"\textbackslash{}").replace("{", r"\{").replace("}", r"\}").replace("%", r"\%").replace("&", r"\&").replace("#", r"\#").replace("_", r"\_")


def bibliography(data):
    entries = []
    for w in sorted(data["works"], key=lambda w: w["id"]):
        if w["kind"] == "presentation":
            continue
        fields = {"title": bib_escape(w["title"]),
                  "author": " and ".join(a["bibtex"] for a in w["authors"]),
                  "year": w["date"][:4], "journal": bib_escape(w["venue"])}
        for source, target in (("volume", "volume"), ("issue", "number"), ("pages", "pages"), ("doi", "doi"), ("pmid", "pmid")):
            if w.get(source):
                fields[target] = bib_escape(w[source])
        fields["note"] = bib_escape(w.get("subtype", STATUS[w["status"]]))
        if w["links"]:
            fields["url"] = w["links"][0]["url"]
        entries.append("@article{" + w["id"] + ",\n" + ",\n".join(f"  {k} = {{{v}}}" for k, v in fields.items()) + "\n}")
    return "\n\n".join(entries) + "\n"


def generate(data, root=ROOT):
    validate(data)
    root = Path(root)
    (root / "_bibliography").mkdir(parents=True, exist_ok=True)
    (root / "_bibliography/papers.bib").write_text(bibliography(data), encoding="utf-8")
    display = copy.deepcopy(data)
    for w in display["works"]:
        w["status_label"] = STATUS[w["status"]]
        year, *rest = w["date"].split("-")
        w["date_label"] = (calendar.month_abbr[int(rest[0])] + " " if rest else "") + (str(int(rest[1])) + ", " if len(rest) > 1 else "") + year
    display["works"].sort(key=lambda w: (w["date"], w["id"]), reverse=True)
    display["groups"] = [{"kind": k, "title": title} for k, title in GROUPS if any(w["kind"] == k for w in data["works"])]
    write_json(root / "_data/publications.json", display)
    bib_dir = root / "assets/bib"
    if bib_dir.is_dir():
        expected = {w['id'] + '.bib' for w in data['works'] if w['kind'] != 'presentation'}
        for old in bib_dir.glob('*.bib'):
            if old.name not in expected:
                old.unlink()
    for w in data["works"]:
        if w["kind"] != "presentation":
            (root / "assets/bib").mkdir(parents=True, exist_ok=True)
            (root / "assets/bib" / (w["id"] + ".bib")).write_text(bibliography({"works": [w]}), encoding="utf-8")


def parse_upstream_date(value):
    value = value.strip()
    for fmt, size in (("%b %d, %Y", 10), ("%B %d, %Y", 10), ("%b %Y", 7), ("%B %Y", 7), ("%Y", 4), ("%Y-%m-%d", 10), ("%Y-%m", 7)):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")[:size]
        except ValueError:
            pass
    raise ValueError("Unresolved upstream date; review required")


def author_from_token(token):
    # Do not guess multiword surnames, suffixes, or corporate authors.
    match = re.fullmatch(r"([^\W\d_][\w’'\-]+) ([A-Z]{1,5})", token, re.UNICODE)
    if not match:
        raise ValueError("Unresolved author conversion; supply reviewed public-author mapping")
    return {"display": token, "bibtex": match[1] + ", " + ". ".join(match[2]) + "."}


def export_profile(profile, selection):
    # The selection is external review metadata, never a copy of the raw profile.
    records = {w["work_id"]: w for w in profile["scholarly_works"]["entries"] if "work_id" in w}
    works = []
    for pick in selection["records"]:
        raw = records[pick["work_id"]]
        if "first_author" in raw and raw["first_author"] != (raw["authors"][0] in selection["identity"]["author_aliases"]):
            raise ValueError("Upstream first-author disagreement")
        w = {"id": pick["id"], "kind": pick["kind"], "status": pick["status"], "title": raw["title"],
             "authors": pick.get("authors") or [author_from_token(a) for a in raw["authors"]],
             "owner_author_index": raw["authors"].index(pick.get("owner_token", "Do J")),
             "venue": raw.get("name") or pick["venue"],
             "date": parse_upstream_date(pick.get("date") or raw["publication_date"]),
             "links": pick.get("links", []), "related_ids": pick.get("related_ids", []), "sources": pick["sources"]}
        for src, dst in (("volume", "volume"), ("issue_number", "issue"), ("pages", "pages"), ("pmid", "pmid")):
            if raw.get(src):
                w[dst] = str(raw[src])
        for key in ("doi", "doi_scope", "subtype", "summary", "online_date", "issue_date", "citations"):
            if key in pick:
                w[key] = pick[key]
        works.append(w)
    # Explicit, reviewed additions cover public outputs outside an upstream category.
    works.extend(selection.get("additional_works", []))
    bundle = {"schema_version": 1, "identity": selection["identity"], "works": works}
    for key in ("education", "appointments", "honors"):
        if key in selection:
            bundle[key] = selection[key]
    return validate(bundle)


def cached_request(url, cache, user_agent, accept, interval, opener=urlopen, sleeper=time.sleep):
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    key = cache / (hashlib.sha256(url.encode()).hexdigest() + ".cache")
    if key.exists() and time.time() - key.stat().st_mtime < 7 * 86400:
        return key.read_bytes()
    for attempt in range(3):
        sleeper(interval if attempt == 0 else 2 ** attempt)
        try:
            with opener(Request(url, headers={"User-Agent": user_agent, "Accept": accept}), timeout=20) as response:
                payload = response.read(5_000_001)
                if len(payload) > 5_000_000:
                    raise ValueError("Metadata response too large")
            key.write_bytes(payload)
            return payload
        except HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
            retry = e.headers.get("Retry-After", "0") if e.headers else "0"
            try:
                delay = int(retry) if retry.isdigit() else max(0, (parsedate_to_datetime(retry) - datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError):
                delay = 0
            if delay > 60:
                raise  # Preserve the snapshot; don't retry sooner than the provider permits.
            sleeper(delay)
        except (TimeoutError, URLError):
            if attempt == 2:
                raise


def crossref_metadata(payload):
    body = json.loads(payload)
    if not isinstance(body, dict) or not isinstance(body.get('message'), dict):
        raise ValueError('Malformed Crossref metadata structure')
    message = body['message']
    result = {}
    for source, target in (("title", "title"), ("container-title", "venue")):
        if isinstance(message.get(source), list) and message[source] and isinstance(message[source][0], str):
            result[target] = message[source][0]
    if isinstance(message.get('author'), list) and all(isinstance(a, dict) for a in message['author']):
        result["authors"] = [{k: a[k] for k in ("given", "family", "name") if k in a} for a in message["author"]]
    for key in ("volume", "issue", "page", "published-online", "published-print", "update-to"):
        if key in message:
            result[key] = message[key]
    if "is-referenced-by-count" in message:
        result["crossref_citations"] = message["is-referenced-by-count"]
    if message.get('DOI'):
        result['doi'] = normalize_doi(message['DOI'])
    return result


def pubmed_metadata(payload):
    tree = ET.fromstring(payload)
    article = tree.find(".//PubmedArticle")
    if article is None:
        return {}
    def txt(path):
        el = article.find(path)
        return "" if el is None else "".join(el.itertext())
    result = {"title": txt(".//ArticleTitle"), "venue": txt(".//Journal/Title")}
    if txt('.//PMID'):
        result['pmid'] = txt('.//PMID')
    authors = []
    for a in article.findall(".//AuthorList/Author"):
        authors.append({"family": a.findtext("LastName", ""), "given": a.findtext("ForeName", ""), "name": a.findtext("CollectiveName", "")})
    if authors:
        result["authors"] = authors
    publication_types = [el.text for el in article.findall(".//PublicationType")]
    if publication_types:
        result["publication_types"] = publication_types
    result["corrections"] = [e.attrib for e in article.findall(".//CommentsCorrections")]
    return {k: v for k, v in result.items() if v}


def refresh(data, output, email, fetch=cached_request):
    output = external_path(output)
    proposals = []
    for w in data["works"]:
        for provider in ("crossref", "pubmed"):
            if provider == "crossref" and (not w.get("doi") or w.get("doi_scope") == "supplement"):
                continue
            if provider == "pubmed" and not w.get("pmid"):
                continue
            if provider == "crossref":
                url = "https://api.crossref.org/works/" + quote(w["doi"], safe="") + "?mailto=" + quote(email)
                parser, interval, accept = crossref_metadata, 1.0, "application/json"
            else:
                url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=" + w["pmid"] + "&tool=research-website&email=" + quote(email)
                parser, interval, accept = pubmed_metadata, 0.4, "application/xml"
            item = {"id": w["id"], "provider": provider}
            try:
                proposed = parser(fetch(url, output / "cache", "ResearchWebsite/1.0 (mailto:" + email + ")", accept, interval))
                item.update(status="review" if proposed else "missing", approved={k: w[k] for k in ("title", "authors", "venue", "status", "date")}, candidate=proposed)
                def norm(value):
                    return re.sub(r'\s+', ' ', unescape(str(value))).strip().rstrip('.').casefold()
                changes, alerts = {}, []
                if proposed.get('doi') and proposed['doi'] != normalize_doi(w.get('doi', '')):
                    alerts.append('Provider DOI does not match requested work')
                if proposed.get('pmid') and proposed['pmid'] != w.get('pmid'):
                    alerts.append('Provider PMID does not match requested work')
                for key in ('title', 'venue'):
                    if proposed.get(key) and norm(w[key]) != norm(proposed[key]):
                        changes[key] = {'approved': w[key], 'candidate': proposed[key]}
                if proposed.get('authors'):
                    tokens = []
                    for author in proposed['authors']:
                        initials = ''.join(part[0] for part in re.findall(r'[^\W\d_]+', author.get('given', ''), re.UNICODE))
                        tokens.append((author.get('family', '') + ' ' + initials).strip() if author.get('family') else author.get('name', ''))
                    if [norm(a['display']) for a in w['authors']] != [norm(a) for a in tokens]:
                        changes['authors'] = {'approved': [a['display'] for a in w['authors']], 'candidate': tokens}
                        alerts.append('Authorship/order conflict requires final-source review')
                for incoming, approved in (('volume', 'volume'), ('issue', 'issue'), ('page', 'pages')):
                    if proposed.get(incoming) and norm(w.get(approved, '')) != norm(proposed[incoming]):
                        changes[approved] = {'approved': w.get(approved), 'candidate': proposed[incoming]}
                if proposed.get('corrections') or proposed.get('update-to'):
                    alerts.append('Correction/retraction relationship requires review')
                if not proposed:
                    alerts.append('No usable record returned; retain approved content')
                item.update(changes=changes, alerts=alerts)
            except (HTTPError, URLError, TimeoutError, ValueError, KeyError, ET.ParseError) as e:
                item.update(status="error", error=type(e).__name__)
            proposals.append(item)
    write_json(output / "metadata-proposals.json", {"generated_at": datetime.now().isoformat(timespec="seconds"), "proposals": proposals})
    return proposals


class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])


def audit_artifact(directory):
    directory = Path(directory).resolve()
    if not (directory / "index.html").is_file():
        raise ValueError("Built homepage missing")
    errors, external = [], set()
    parsed = {}
    allowed_root = {"index.html", "404.html", "robots.txt", "sitemap.xml"}
    for p in directory.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(directory)
        if rel.parts[0] not in {"assets", "research", "publications"} and str(rel) not in allowed_root:
            errors.append("Unexpected artifact: " + rel.as_posix())
        reviewed_binary = rel.as_posix() in {"assets/img/justin-do.jpg", "assets/pdf/Justin_Do_CV.pdf"}
        if p.suffix not in (".html", ".css", ".js", ".xml", ".txt", ".bib", ".json", ".svg") and not reviewed_binary:
            errors.append("Unreviewed binary artifact: " + rel.as_posix())
        if p.suffix in (".html", ".json", ".txt", ".xml", ".bib"):
            text = p.read_text(encoding="utf-8")
            if re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]|/home/|/Users/|eras-planning|application_profile|Einstein|Albert Einstein|password|access_token", text, re.I):
                errors.append("Private/demo marker: " + rel.as_posix())
        if p.suffix == ".html":
            doc = HTMLLinks()
            doc.feed(p.read_text(encoding="utf-8"))
            parsed[p] = doc
    for p, doc in parsed.items():
        base = "/" + p.relative_to(directory).as_posix()
        for link in doc.links:
            url = urlsplit(urljoin("https://do-justin.github.io" + base, link))
            if url.scheme in ("mailto", "tel", "data"):
                continue
            if url.netloc != "do-justin.github.io":
                external.add(link)
                continue
            target = directory / unquote(url.path).lstrip("/")
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                errors.append("Broken internal link: " + link)
            elif url.fragment and target in parsed and url.fragment not in parsed[target].ids:
                errors.append("Broken anchor: " + link)
    if errors:
        raise ValueError("\n".join(errors))
    return {"html_pages": len(parsed), "external_links": sorted(external), "files": sum(p.is_file() for p in directory.rglob("*"))}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for command in ("validate", "generate", "cv"):
        sub.add_parser(command).add_argument("--profile", type=Path, default=PROFILE)
    exp = sub.add_parser("export")
    exp.add_argument("--profile", type=Path, required=True)
    exp.add_argument("--selection", type=Path, required=True)
    exp.add_argument("--output", type=Path, required=True)
    imp = sub.add_parser("import")
    imp.add_argument("--bundle", type=Path, required=True)
    imp.add_argument("--reviewed", action="store_true", required=True)
    ref = sub.add_parser("refresh")
    ref.add_argument("--output", type=Path, required=True)
    ref.add_argument("--email", required=True)
    audit = sub.add_parser("audit")
    audit.add_argument("--site", type=Path, default=ROOT / "_site")
    args = p.parse_args()
    if args.command in ("validate", "generate", "cv"):
        data = validate(read_json(args.profile))
        if args.command == "generate":
            generate(data)
        elif args.command == "cv":
            from cv import check_cv
            print(f"CV: {check_cv(ROOT)} pages; reviewed file unchanged")
        print(f"{args.command}: {len(data['works'])} public works validated")
    elif args.command == "export":
        result = export_profile(read_json(external_path(args.profile)), read_json(external_path(args.selection)))
        write_json(external_path(args.output), result)
        print("Public candidate exported to external staging; review before import")
    elif args.command == "import":
        result = validate(read_json(external_path(args.bundle)))
        write_json(PROFILE, result)
        print("Reviewed public bundle imported")
    elif args.command == "refresh":
        proposals = refresh(validate(read_json(PROFILE)), args.output, args.email)
        print(f"{len(proposals)} provider proposals saved externally; approved snapshot unchanged")
    elif args.command == "audit":
        print(json.dumps(audit_artifact(args.site), indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
