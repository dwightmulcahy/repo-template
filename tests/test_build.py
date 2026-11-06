import json
import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("edition", ["web", "offline"])
def test_build_edition(tmp_path, edition):
    out = tmp_path / edition
    subprocess.run(
        ["node", "scripts/build.mjs", edition],
        cwd=ROOT, env={**os.environ, "OUT_DIR": str(out)}, check=True,
    )
    assert (out / "index.html").is_file()
    assert json.loads((out / "build.json").read_text())["edition"] == edition


def test_build_rejects_unknown_edition():
    r = subprocess.run(["node", "scripts/build.mjs", "bogus"], cwd=ROOT, capture_output=True)
    assert r.returncode != 0


def _build(tmp_path, **env):
    out = tmp_path / "v"
    clean = {k: v for k, v in os.environ.items()
             if k not in ("APP_VERSION", "GIT_SHA", "GIT_DIR", "REPOSITORY", "GITHUB_REPOSITORY")}
    subprocess.run(["node", "scripts/build.mjs", "web"], cwd=ROOT,
                   env={**clean, "OUT_DIR": str(out), **env}, check=True, capture_output=True)
    return out


def _info(tmp_path, **env):
    meta = json.loads((_build(tmp_path, **env) / "build.json").read_text())
    return {k: meta[k] for k in ("version", "commit", "repository")}


@pytest.mark.parametrize(
    "env, expected",
    [
        ({}, ("dev", "", "")),
        ({"APP_VERSION": "1.4.2", "GIT_SHA": "ABCDEF0123456789", "REPOSITORY": "me/app"},
         ("1.4.2", "abcdef0", "https://github.com/me/app")),
        ({"APP_VERSION": "v2.0.0-rc.1", "GITHUB_REPOSITORY": "org/x.y"}, ("2.0.0-rc.1", "", "https://github.com/org/x.y")),
        ({"APP_VERSION": "<script>", "GIT_SHA": "not-a-sha", "REPOSITORY": "a/b/c"}, ("dev", "", "")),
    ],
)
def test_version_info(tmp_path, env, expected):
    assert tuple(_info(tmp_path, **env).values()) == expected


def test_build_info_is_embedded_in_the_page(tmp_path):
    out = _build(tmp_path, APP_VERSION="1.0.0", GIT_SHA="abc1234")
    html = (out / "index.html").read_text()
    m = re.search(r'<script type="application/json" id="build-info">(.*?)</script>', html, re.S)
    assert json.loads(m.group(1)) == json.loads((out / "build.json").read_text())


def _git(tmp_path, head, refs=None, packed="", config=""):
    git = tmp_path / "git"
    (git / "refs" / "heads").mkdir(parents=True)
    (git / "HEAD").write_text(head)
    for name, sha in (refs or {}).items():
        (git / "refs" / "heads" / name).write_text(sha + "\n")
    if packed:
        (git / "packed-refs").write_text(packed)
    (git / "config").write_text(config)
    return str(git)


ORIGIN = '[core]\n\tbare = false\n[remote "upstream"]\n\turl = https://github.com/up/stream.git\n[remote "origin"]\n\turl = {}\n'


@pytest.mark.parametrize(
    "head, refs, packed, url, expected",
    [
        ("ref: refs/heads/main\n", {"main": "35C7C08" + "a" * 33}, "", "git@github.com:me/app.git", ("35c7c08", "https://github.com/me/app")),
        ("ref: refs/heads/main\n", {}, "# pack-refs\n" + "1" * 40 + " refs/heads/main\n", "https://github.com/me/app/", ("1111111", "https://github.com/me/app")),
        ("2222222" + "c" * 33 + "\n", {}, "", "https://gitlab.com/me/app.git", ("2222222", "")),
        ("ref: refs/heads/other\n", {}, "", "ssh://git@github.com/me/app", ("", "https://github.com/me/app")),
        ("ref: refs/../../etc/passwd\n", {}, "", "", ("", "")),
    ],
)
def test_local_builds_read_git_dir(tmp_path, head, refs, packed, url, expected):
    git = _git(tmp_path, head, refs, packed, ORIGIN.format(url) if url else "")
    info = _info(tmp_path, GIT_DIR=git)
    assert (info["commit"], info["repository"]) == expected


def test_env_wins_over_git_dir_and_missing_git_dir_is_ignored(tmp_path):
    git = _git(tmp_path, "ref: refs/heads/main\n", {"main": "3" * 40}, config=ORIGIN.format("git@github.com:me/app.git"))
    info = _info(tmp_path, GIT_DIR=git, GIT_SHA="abcdef0", REPOSITORY="other/repo")
    assert (info["commit"], info["repository"]) == ("abcdef0", "https://github.com/other/repo")
    assert _info(tmp_path, GIT_DIR=str(tmp_path / "nope"))["commit"] == ""


def test_build_fails_without_the_build_info_placeholder(tmp_path):
    src = tmp_path / "repo"
    (src / "scripts").mkdir(parents=True)
    (src / "src").mkdir()
    (src / "scripts" / "build.mjs").write_text((ROOT / "scripts" / "build.mjs").read_text())
    (src / "src" / "index.html").write_text("<!doctype html><title>x</title>")
    r = subprocess.run(["node", "scripts/build.mjs", "web"], cwd=src, capture_output=True, text=True)
    assert r.returncode != 0 and "build-info" in r.stderr
