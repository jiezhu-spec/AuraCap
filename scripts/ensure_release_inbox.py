from __future__ import annotations

import json
import os

import httpx


def _get_repo() -> tuple[str, str]:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repo:
        raise RuntimeError("GITHUB_REPOSITORY is missing")
    owner, name = repo.split("/", 1)
    return owner, name


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


async def _ensure_release(owner: str, repo: str, token: str, tag: str) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=_headers(token))
        if r.status_code == 200:
            return r.json()
        if r.status_code != 404:
            raise RuntimeError(f"fetch release failed: {r.status_code} {r.text}")

        create_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        body = {
            "tag_name": tag,
            "name": "AuraCap Inbox",
            "body": "Temporary inbox release for AuraCap GitHub-only asset uploads.",
            "draft": False,
            "prerelease": False,
        }
        c = await client.post(create_url, headers=_headers(token), json=body)
        if c.status_code >= 400:
            raise RuntimeError(f"create release failed: {c.status_code} {c.text}")
        return c.json()


async def main() -> int:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is missing")

    tag = os.environ.get("GITHUB_RELEASE_INBOX_TAG", "auracap-inbox")
    owner, repo = _get_repo()
    release = await _ensure_release(owner, repo, token, tag)

    info = {
        "tag": tag,
        "release_id": release.get("id"),
        "upload_url": str(release.get("upload_url", "")).replace("{?name,label}", ""),
        "html_url": release.get("html_url"),
    }
    print(json.dumps(info, ensure_ascii=False, indent=2))

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## AuraCap Release Inbox\n\n")
            f.write(f"- tag: `{info['tag']}`\n")
            f.write(f"- release_id: `{info['release_id']}`\n")
            f.write(f"- upload_url: `{info['upload_url']}`\n")
            f.write(f"- html_url: {info['html_url']}\n")

    return 0


if __name__ == "__main__":
    import asyncio

    raise SystemExit(asyncio.run(main()))
