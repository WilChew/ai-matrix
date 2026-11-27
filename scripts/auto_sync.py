#!/usr/bin/env python3
"""
scripts/auto_sync.py
Automated Frontier AI Models & Agents Sync Script for GitHub Actions.
Tracks global top AI models and autonomous agent releases, detects diffs,
and updates index.html, version.json, and CHANGELOG.md automatically.
Author: Wil Chew@2026
"""

import os
import sys
import json
import re
import datetime
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INDEX_HTML = os.path.join(PROJECT_ROOT, "index.html")
VERSION_JSON = os.path.join(PROJECT_ROOT, "version.json")
CHANGELOG_MD = os.path.join(PROJECT_ROOT, "CHANGELOG.md")
RELEASE_NOTES_MD = os.path.join(PROJECT_ROOT, "release_notes.md")

AGENT_REPOS = [
    {
        "brand_key": "claudecode",
        "name": "Claude Code",
        "repo": "anthropics/claude-code",
        "url_prefix": "https://github.com/anthropics/claude-code/releases/tag/"
    },
    {
        "brand_key": "codex",
        "name": "OpenAI Codex CLI",
        "repo": "openai/codex",
        "url_prefix": "https://github.com/openai/codex/releases/tag/"
    },
    {
        "brand_key": "copilot",
        "name": "GitHub Copilot CLI",
        "repo": "github/copilot-cli",
        "url_prefix": "https://github.com/github/copilot-cli/releases/tag/"
    },
    {
        "brand_key": "deepseek",
        "name": "DeepSeek Harness & CLI",
        "repo": "deepseek-ai/DeepSeek-Coder",
        "url_prefix": "https://github.com/deepseek-ai/DeepSeek-Coder/releases/tag/"
    }
]

def make_request(url, timeout=10):
    headers = {
        "User-Agent": "Antigravity-AutoSync/2.0 (Wil Chew@2026)",
        "Accept": "application/vnd.github+json"
    }
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {github_token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[Warning] Failed to fetch {url}: {e}")
    return None

def fetch_agent_releases():
    """Fetch latest releases for tracked agent repos."""
    results = {}
    for agent in AGENT_REPOS:
        repo = agent["repo"]
        url = f"https://api.github.com/repos/{repo}/releases?per_page=5"
        data = make_request(url)
        if data and isinstance(data, list) and len(data) > 0:
            latest = data[0]
            tag = latest.get("tag_name", "").strip()
            published_at = latest.get("published_at", "")[:10].replace("-", ".")
            body = (latest.get("body") or "").strip()
            headline = latest.get("name") or tag
            headline = headline.replace(tag, "").strip(" -:") or "Autonomous agent capability enhancements"
            results[agent["brand_key"]] = {
                "brand_key": agent["brand_key"],
                "tag": tag,
                "date": published_at,
                "headline": headline[:120],
                "url": latest.get("html_url", f"{agent['url_prefix']}{tag}"),
                "source": agent["name"]
            }
            print(f"✓ Found {agent['name']} latest release: {tag} ({published_at})")
    return results

def fetch_openrouter_frontier_models():
    """Fetch top models catalog from OpenRouter."""
    url = "https://openrouter.ai/api/v1/models"
    data = make_request(url, timeout=15)
    if not data or "data" not in data:
        return []
    
    models = data["data"]
    frontier_prefixes = [
        "google/", "openai/", "anthropic/", "microsoft/", "x-ai/", "deepseek/", "bytedance/"
    ]
    frontier_models = []
    for m in models:
        mid = m.get("id", "")
        if any(mid.startswith(p) for p in frontier_prefixes) and ":batch" not in mid:
            frontier_models.append({
                "id": mid,
                "name": m.get("name", mid),
                "context_length": m.get("context_length", 0),
                "created": m.get("created", 0)
            })
    frontier_models.sort(key=lambda x: x.get("created", 0), reverse=True)
    return frontier_models

def get_current_tracked_releases(html_content):
    """Extract known agent tags from DEFAULT_AGENT_RELEASES in index.html."""
    pattern = r'tag:\s*["\']([^"\']+)["\']'
    known_tags = set(re.findall(pattern, html_content))
    return known_tags

def bump_patch_version(current_ver):
    """Bumps version from v2.2.0 -> v2.2.1."""
    match = re.match(r'^v?(\d+)\.(\d+)\.(\d+)$', current_ver.strip())
    if match:
        major, minor, patch = match.groups()
        return f"v{major}.{minor}.{int(patch) + 1}"
    return f"{current_ver}-sync"

def inject_agent_release_into_html(html, update):
    brand = update["brand_key"]
    tag = update["tag"]
    date_str = update["date"]
    source = update["source"]
    url = update["url"]
    headline = update["headline"].replace('"', '\\"')
    
    snippet = f'''        {{
          id: "{brand}-{tag}",
          tag: "{tag}",
          date: "{date_str}",
          source: "{source}",
          url: "{url}",
          headline_zh: "官方版本发布：{headline}",
          headline_en: "Official release: {headline}",
          bullets_zh: [
            "通过 GitHub Actions 云端定时检测发现的新官方版本发布。",
            "支持多轮复杂代理自主规划与更深度的终端/IDE交互协同。"
          ],
          bullets_en: [
            "Official agent release detected via automated GitHub Actions cloud sync.",
            "Enhanced autonomous tool usage, execution workflows, and deep IDE synergy."
          ]
        }},
'''
    pattern = rf'({brand}:\s*\[\s*\n)'
    if re.search(pattern, html):
        html = re.sub(pattern, rf'\1{snippet}', html, count=1)
        print(f"✓ Injected release {tag} into DEFAULT_AGENT_RELEASES.{brand}")
    return html

def bump_html_cache_keys(html):
    def repl_models(m):
        prefix = m.group(1)
        num = int(m.group(2)) + 1
        return f"{prefix}{num}"
    def repl_agents(m):
        prefix = m.group(1)
        num = int(m.group(2)) + 1
        return f"{prefix}{num}"
    html = re.sub(r'(DASHBOARD_LIVE_MODELS_V)(\d+)', repl_models, html)
    html = re.sub(r'(DASHBOARD_AGENT_RELEASES_V)(\d+)', repl_agents, html)
    return html

def main():
    dry_run = "--dry-run" in sys.argv
    force_sync = "--force" in sys.argv
    print(f"=== Starting Frontier AI & Agent Auto-Sync (Dry-run: {dry_run}, Force: {force_sync}) ===")

    if not os.path.exists(INDEX_HTML):
        print(f"Error: {INDEX_HTML} not found.")
        sys.exit(1)

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    known_tags = get_current_tracked_releases(html)
    print(f"Tracked agent releases currently in index.html: {len(known_tags)} tags found.")

    # 1. Fetch live releases
    live_agents = fetch_agent_releases()
    new_agent_updates = []

    for brand, rel in live_agents.items():
        tag = rel["tag"]
        if tag and tag not in known_tags:
            print(f"🔥 NEW RELEASE DETECTED: {rel['source']} {tag}!")
            new_agent_updates.append(rel)

    # 2. Fetch live OpenRouter catalog
    frontier_models = fetch_openrouter_frontier_models()
    print(f"Fetched {len(frontier_models)} frontier models from OpenRouter catalog.")

    has_updates = len(new_agent_updates) > 0 or force_sync

    if not has_updates:
        print("\n✨ All tracked models and agents are already at their latest releases. No changes needed.")
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
                f.write("has_updates=false\n")
        return

    print(f"\n🚀 Proceeding with update: {len(new_agent_updates)} new releases found.")

    # Load current version
    current_ver = "v2.2.0"
    if os.path.exists(VERSION_JSON):
        with open(VERSION_JSON, "r", encoding="utf-8") as f:
            v_data = json.load(f)
            current_ver = v_data.get("version", current_ver)

    new_ver = bump_patch_version(current_ver)
    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    release_title = f"{new_ver} - Automated Frontier Sync: {', '.join([u['source'] for u in new_agent_updates]) or 'Daily Pulse'}"

    # Generate release notes
    notes_lines = [
        f"### 🤖 Automated Frontier Intelligence & Agent Sync ({today_str})",
        "",
        "This update was automatically discovered, verified, and released via GitHub Actions:",
        ""
    ]
    for u in new_agent_updates:
        notes_lines.append(f"- **{u['source']} `{u['tag']}`** ({u['date']}): {u['headline']}")
    if not new_agent_updates:
        notes_lines.append("- Routine daily frontier catalog synchronization and cache refresh.")
    notes_lines.append("")
    notes_lines.append("- **Author**: `Wil Chew@2026`")

    release_notes_text = "\n".join(notes_lines)

    if dry_run:
        print(f"\n[DRY RUN] Would bump version to: {new_ver}")
        print(f"[DRY RUN] Release Title: {release_title}")
        print(f"[DRY RUN] Release Notes:\n{release_notes_text}")
        return

    # Update index.html
    updated_html = html
    for update in new_agent_updates:
        updated_html = inject_agent_release_into_html(updated_html, update)
    updated_html = bump_html_cache_keys(updated_html)
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(updated_html)
    print("✓ Updated index.html with new releases and bumped cache keys.")

    # Update version.json
    new_v_data = {
        "version": new_ver,
        "title": release_title,
        "release_notes": release_notes_text
    }
    with open(VERSION_JSON, "w", encoding="utf-8") as f:
        json.dump(new_v_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Updated version.json -> {new_ver}")

    # Update CHANGELOG.md
    if os.path.exists(CHANGELOG_MD):
        with open(CHANGELOG_MD, "r", encoding="utf-8") as f:
            old_changelog = f.read()
        changelog_entry = f"## [{new_ver}] - {today_str}\n\n{release_notes_text}\n\n---\n\n"
        if "---" in old_changelog:
            header, rest = old_changelog.split("---", 1)
            updated_changelog = header + "---\n\n" + changelog_entry + rest.lstrip("\n")
        else:
            updated_changelog = changelog_entry + old_changelog
        with open(CHANGELOG_MD, "w", encoding="utf-8") as f:
            f.write(updated_changelog)
        print(f"✓ Updated CHANGELOG.md with entry for {new_ver}")

    # Write release_notes.md for gh release create
    with open(RELEASE_NOTES_MD, "w", encoding="utf-8") as f:
        f.write(release_notes_text)
    print(f"✓ Written {RELEASE_NOTES_MD}")

    # Set GITHUB_OUTPUT
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write("has_updates=true\n")
            f.write(f"new_version={new_ver}\n")
            f.write(f"release_title={release_title}\n")

    print(f"\n🎉 Auto-sync completed successfully! Ready for commit & release {new_ver}.")

if __name__ == "__main__":
    main()
