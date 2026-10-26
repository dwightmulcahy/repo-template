from unittest.mock import patch

from scripts.generate_release_notes import render


@patch("scripts.generate_release_notes.previous_tag", return_value="v1.1.0")
@patch(
    "scripts.generate_release_notes.commit_subjects",
    return_value=[
        ("abc1234", "feat(status): add dashboard"),
        ("def5678", "fix: prevent release race"),
        ("987abcd", "docs: explain Docker tags"),
    ],
)
def test_groups_conventional_commits(_subjects, _previous):
    notes = render("v1.2.0", "owner/app", "My App", "docker.io/owner/app")

    assert "# My App 1.2.0" in notes
    assert "## ✨ Features" in notes
    assert "**status:** add dashboard (abc1234)" in notes
    assert "## 🐛 Bug fixes" in notes
    assert "docker pull docker.io/owner/app:1.2.0" in notes
    assert "compare/v1.1.0...v1.2.0" in notes


@patch("scripts.generate_release_notes.previous_tag", return_value=None)
@patch(
    "scripts.generate_release_notes.commit_subjects",
    return_value=[("abc1234", "feat!: replace legacy configuration")],
)
def test_highlights_breaking_changes(_subjects, _previous):
    notes = render("0.1.0", "owner/app", "My App", "owner/app")

    assert "## 💥 Breaking changes" in notes
    assert "replace legacy configuration" in notes
