"""Concurrent load test for the CERP API.

Usage:
    python scripts/load_test.py --base http://127.0.0.1:8000 --users 10 --rounds 20
"""
import argparse
import statistics
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import requests

READ_ENDPOINTS = [
    "/api/sos/",
    "/api/sos/active/",
    "/api/dashboard/stats/",
    "/api/auth/me/",
    "/api/auth/emergency-contacts/",
]


def percentile(values, pct):
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round(pct / 100 * len(ordered)) - 1))
    return ordered[index]


def login(base, username, password):
    response = requests.post(
        f"{base}/api/auth/login/", json={"username": username, "password": password}, timeout=60
    )
    response.raise_for_status()
    return response.json()["access"]


def worker(base, token, rounds):
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {token}"
    results = []
    for _ in range(rounds):
        for path in READ_ENDPOINTS:
            start = time.perf_counter()
            try:
                ok = session.get(base + path, timeout=60).status_code < 400
            except requests.RequestException:
                ok = False
            results.append((path, (time.perf_counter() - start) * 1000, ok))
    return results


def time_sos(base, token, count):
    headers = {"Authorization": f"Bearer {token}"}
    timings = []
    for _ in range(count):
        start = time.perf_counter()
        response = requests.post(
            f"{base}/api/sos/", headers=headers, timeout=60,
            json={"category": "OTHER", "message": "Load test alert", "latitude": 18.52, "longitude": 73.85},
        )
        timings.append((time.perf_counter() - start) * 1000)
        if response.status_code == 201:
            requests.post(
                f"{base}/api/sos/{response.json()['id']}/resolve/", headers=headers, timeout=60,
                json={"resolution_notes": "Load test cleanup"},
            )
    return timings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument("--username", default="resident1")
    parser.add_argument("--password", default="Resident@2026")
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--rounds", type=int, default=20)
    parser.add_argument("--sos", type=int, default=10, help="SOS creations to time (0 to skip)")
    args = parser.parse_args()

    token = login(args.base, args.username, args.password)
    print(f"Target {args.base} | {args.users} concurrent users x {args.rounds} rounds x {len(READ_ENDPOINTS)} endpoints\n")

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.users) as pool:
        batches = list(pool.map(lambda _: worker(args.base, token, args.rounds), range(args.users)))
    elapsed = time.perf_counter() - started

    by_path = defaultdict(list)
    errors = defaultdict(int)
    for batch in batches:
        for path, ms, ok in batch:
            by_path[path].append(ms)
            errors[path] += 0 if ok else 1

    header = f"{'Endpoint':32} {'Reqs':>6} {'Errors':>7} {'Avg ms':>8} {'p50 ms':>8} {'p95 ms':>8} {'Max ms':>8}"
    print(header)
    print("-" * len(header))
    total = 0
    all_ms = []
    for path in READ_ENDPOINTS:
        values = by_path[path]
        total += len(values)
        all_ms += values
        print(f"{path:32} {len(values):>6} {errors[path]:>7} {statistics.mean(values):>8.0f} "
              f"{percentile(values, 50):>8.0f} {percentile(values, 95):>8.0f} {max(values):>8.0f}")
    print("-" * len(header))
    print(f"{'ALL READS':32} {total:>6} {sum(errors.values()):>7} {statistics.mean(all_ms):>8.0f} "
          f"{percentile(all_ms, 50):>8.0f} {percentile(all_ms, 95):>8.0f} {max(all_ms):>8.0f}")
    print(f"\nThroughput: {total / elapsed:.1f} requests/second over {elapsed:.1f}s")

    if args.sos:
        sos = time_sos(args.base, token, args.sos)
        print(f"\nSOS creation (full notification fan-out), {len(sos)} alerts:")
        print(f"  avg {statistics.mean(sos):.0f} ms | p95 {percentile(sos, 95):.0f} ms | max {max(sos):.0f} ms")


if __name__ == "__main__":
    main()