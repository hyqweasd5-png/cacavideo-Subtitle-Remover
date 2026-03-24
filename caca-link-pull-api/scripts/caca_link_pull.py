#!/usr/bin/env python3
"""CLI helper for the cacaLinkPull async media-pull API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any


DEFAULT_BASE_URL = (
    "https://env-00jxh2cj3gfd.dev-hz.cloudbasefunction.cn/http/router/"
)
DEFAULT_SUBMIT_PATH = "user/pub/cacaLinkPullAsycTest"
DEFAULT_STATUS_PATH = "user/pub/cacaLinkPullStatusTest"


def env_or_value(value: str | None, env_name: str) -> str | None:
    if value:
        return value
    return os.environ.get(env_name)


def require_auth(args: argparse.Namespace) -> tuple[str, str]:
    secret_id = env_or_value(args.secret_id, "CACA_SECRET_ID")
    secret_key = env_or_value(args.secret_key, "CACA_SECRET_KEY")
    if not secret_id or not secret_key:
        raise SystemExit(
            "Missing credentials. Pass --secret-id/--secret-key or set "
            "CACA_SECRET_ID and CACA_SECRET_KEY."
        )
    return secret_id, secret_key


def build_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Expected JSON response, got: {text[:300]}") from exc


def post_json(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            parsed = parse_json(body)
            if not isinstance(parsed, dict):
                raise SystemExit("Expected JSON object response.")
            parsed.setdefault("_http_status", response.status)
            return parsed
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        parsed = parse_json(body)
        if not isinstance(parsed, dict):
            raise SystemExit("Expected JSON object response.")
        parsed.setdefault("_http_status", exc.code)
        return parsed
    except urllib.error.URLError as exc:
        raise SystemExit(f"Request failed: {exc}") from exc


def emit(data: Any, pretty: bool) -> None:
    if pretty:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    print(json.dumps(data, ensure_ascii=False))


def is_failure(payload: dict[str, Any]) -> bool:
    code = payload.get("code")
    status = str(payload.get("status") or "").lower()
    return (isinstance(code, int) and code < 0) or status == "failed"


def is_success(payload: dict[str, Any]) -> bool:
    if payload.get("media"):
        return True
    status = str(payload.get("status") or "").lower()
    code = payload.get("code")
    is_ok = payload.get("isOk")
    return status == "finished" or (code == 0 and is_ok == 1 and "taskId" not in payload)


def is_pending(payload: dict[str, Any]) -> bool:
    code = payload.get("code")
    status = str(payload.get("status") or "").lower()
    return code == 1 or status in {"pending", "processing"}


def summarize(payload: dict[str, Any]) -> str:
    code = payload.get("code")
    status = payload.get("status", "-")
    msg = payload.get("msg", "")
    return f"code={code} status={status} msg={msg}"


def submit_payload(args: argparse.Namespace, secret_id: str, secret_key: str) -> dict[str, Any]:
    return {
        "secret_id": secret_id,
        "secret_key": secret_key,
        "video_link": args.video_link,
        "x1": args.x1,
        "y1": args.y1,
        "x2": args.x2,
        "y2": args.y2,
        "mode": args.mode,
    }


def status_payload(task_id: str, secret_id: str, secret_key: str) -> dict[str, Any]:
    return {
        "taskId": task_id,
        "secret_id": secret_id,
        "secret_key": secret_key,
    }


def command_submit(args: argparse.Namespace) -> int:
    secret_id, secret_key = require_auth(args)
    url = build_url(args.base_url, args.submit_path)
    payload = submit_payload(args, secret_id, secret_key)
    result = post_json(url, payload, args.timeout)
    emit(result, args.pretty)
    return 1 if is_failure(result) else 0


def command_status(args: argparse.Namespace) -> int:
    secret_id, secret_key = require_auth(args)
    url = build_url(args.base_url, args.status_path)
    payload = status_payload(args.task_id, secret_id, secret_key)
    result = post_json(url, payload, args.timeout)
    emit(result, args.pretty)
    return 1 if is_failure(result) else 0


def poll_task(
    args: argparse.Namespace,
    task_id: str,
    secret_id: str,
    secret_key: str,
) -> tuple[int, dict[str, Any]]:
    url = build_url(args.base_url, args.status_path)
    last: dict[str, Any] | None = None
    for attempt in range(1, args.max_attempts + 1):
        payload = status_payload(task_id, secret_id, secret_key)
        last = post_json(url, payload, args.timeout)
        print(
            f"[attempt {attempt}/{args.max_attempts}] {summarize(last)}",
            file=sys.stderr,
        )
        if is_failure(last):
            return 1, last
        if is_success(last):
            return 0, last
        if attempt < args.max_attempts and is_pending(last):
            time.sleep(args.interval)
            continue
        if attempt < args.max_attempts:
            time.sleep(args.interval)
    return 1, last or {"code": -999, "msg": "No status response received."}


def command_wait(args: argparse.Namespace) -> int:
    secret_id, secret_key = require_auth(args)
    exit_code, result = poll_task(args, args.task_id, secret_id, secret_key)
    emit(result, args.pretty)
    return exit_code


def command_run(args: argparse.Namespace) -> int:
    secret_id, secret_key = require_auth(args)
    submit_url = build_url(args.base_url, args.submit_path)
    submit_result = post_json(
        submit_url,
        submit_payload(args, secret_id, secret_key),
        args.timeout,
    )
    print(f"[submit] {summarize(submit_result)}", file=sys.stderr)
    task_id = submit_result.get("taskId")
    if is_failure(submit_result) or not task_id:
        emit({"submit": submit_result}, args.pretty)
        return 1

    exit_code, final_result = poll_task(args, str(task_id), secret_id, secret_key)
    emit({"submit": submit_result, "final": final_result}, args.pretty)
    return exit_code


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--base-url",
        default=os.environ.get("CACA_BASE_URL", DEFAULT_BASE_URL),
        help="Router base URL.",
    )
    parser.add_argument(
        "--submit-path",
        default=os.environ.get("CACA_SUBMIT_PATH", DEFAULT_SUBMIT_PATH),
        help="Relative submit route.",
    )
    parser.add_argument(
        "--status-path",
        default=os.environ.get("CACA_STATUS_PATH", DEFAULT_STATUS_PATH),
        help="Relative status route.",
    )
    parser.add_argument(
        "--secret-id",
        help="API secret_id. Falls back to CACA_SECRET_ID.",
    )
    parser.add_argument(
        "--secret-key",
        help="API secret_key. Falls back to CACA_SECRET_KEY.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )


def add_submit_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--video-link", required=True, help="Remote media URL.")
    parser.add_argument(
        "--mode",
        choices=["normal", "protect"],
        default="normal",
        help="Pull mode.",
    )
    parser.add_argument("--x1", type=float, default=0.0, help="Range x1.")
    parser.add_argument("--y1", type=float, default=0.0, help="Range y1.")
    parser.add_argument("--x2", type=float, default=0.0, help="Range x2.")
    parser.add_argument("--y2", type=float, default=0.0, help="Range y2.")


def add_wait_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--interval",
        type=float,
        default=30.0,
        help="Polling interval in seconds.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=10,
        help="Maximum number of status requests.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI for the cacaLinkPull async media-pull API."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    submit_parser = subparsers.add_parser("submit", help="Submit a new pull job.")
    add_common_arguments(submit_parser)
    add_submit_arguments(submit_parser)
    submit_parser.set_defaults(handler=command_submit)

    status_parser = subparsers.add_parser("status", help="Check an existing task.")
    add_common_arguments(status_parser)
    status_parser.add_argument("--task-id", required=True, help="Task identifier.")
    status_parser.set_defaults(handler=command_status)

    wait_parser = subparsers.add_parser("wait", help="Poll until task completion.")
    add_common_arguments(wait_parser)
    wait_parser.add_argument("--task-id", required=True, help="Task identifier.")
    add_wait_arguments(wait_parser)
    wait_parser.set_defaults(handler=command_wait)

    run_parser = subparsers.add_parser(
        "run", help="Submit a job and poll until completion."
    )
    add_common_arguments(run_parser)
    add_submit_arguments(run_parser)
    add_wait_arguments(run_parser)
    run_parser.set_defaults(handler=command_run)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
