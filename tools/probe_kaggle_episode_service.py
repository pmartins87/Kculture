"""Bounded public-access probe for Kaggle simulation EpisodeService.

Purpose: determine whether the official EpisodeService calls exposed by
kaggle-environments can enumerate/retrieve our known hosted submissions from a
clean GitHub Actions runner without waiting for daily episode datasets.

This performs only four primary calls (two submission lists + two known replay
lookups), writes raw JSON only when HTTP 200 JSON is returned, and never sends
credentials/cookies.  It is a diagnostic, not a bulk scraper.
"""
from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path("artifacts/episode-service-probe")
ROOT.mkdir(parents=True, exist_ok=True)
BASE = "https://www.kaggle.com/requests/EpisodeService/"
TARGETS = {
    "r4b": {"submission_id": 55784381, "known_episode_id": 100996939},
    "kexp050": {"submission_id": 55818927, "known_episode_id": 100987834},
}


def post(session: requests.Session, endpoint: str, body: dict):
    url = BASE + endpoint
    try:
        r = session.post(url, json=body, timeout=30)
        rec = {
            "url": url,
            "status_code": r.status_code,
            "content_type": r.headers.get("content-type"),
            "bytes": len(r.content),
        }
        try:
            data = r.json()
            rec["json_type"] = type(data).__name__
            rec["top_keys"] = sorted(data.keys()) if isinstance(data, dict) else None
            return rec, data
        except Exception as exc:
            rec["json_error"] = repr(exc)
            rec["text_prefix"] = r.text[:500]
            return rec, None
    except Exception as exc:
        return {"url": url, "request_error": repr(exc)}, None


def main():
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Kculture-research/1.0 (+bounded EpisodeService provenance probe)",
            "Accept": "application/json",
        }
    )
    report = {"schema_version": "episode-service-public-probe-v1", "targets": {}}

    for label, target in TARGETS.items():
        sub_id = target["submission_id"]
        ep_id = target["known_episode_id"]
        list_meta, list_data = post(session, "ListEpisodes", {"SubmissionId": sub_id})
        replay_meta, replay_data = post(session, "GetEpisodeReplay", {"EpisodeId": ep_id})

        target_report = {
            "submission_id": sub_id,
            "known_episode_id": ep_id,
            "list": list_meta,
            "replay": replay_meta,
        }
        report["targets"][label] = target_report

        if list_data is not None:
            (ROOT / f"{label}_list_episodes_raw.json").write_text(
                json.dumps(list_data, indent=2, sort_keys=True), encoding="utf-8"
            )
        if replay_data is not None:
            (ROOT / f"{label}_{ep_id}_replay_raw.json").write_text(
                json.dumps(replay_data), encoding="utf-8"
            )

    report["public_access_supported"] = all(
        t["list"].get("status_code") == 200
        and t["replay"].get("status_code") == 200
        and "json_error" not in t["list"]
        and "json_error" not in t["replay"]
        for t in report["targets"].values()
    )
    (ROOT / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["public_access_supported"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
