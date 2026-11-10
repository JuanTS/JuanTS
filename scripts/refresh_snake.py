#!/usr/bin/env python3
"""Regenera snake.svg y stats.svg con los datos reales de contribuciones de JuanTS."""
import json
import os
import urllib.request

USER = os.environ.get("TARGET_USER", "JuanTS")
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def graphql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "profile-refresh-action",
        },
    )
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def main():
    data = graphql(
        f'query {{ user(login: "{USER}") {{ '
        "contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } "
        "totalCommitContributions totalPullRequestContributions totalIssueContributions "
        "repositories(first: 100) { totalCount nodes { stargazers { totalCount } } } "
        "totalPullRequestContributions totalIssueContributions "
        "} } }"
    )
    user = data["data"]["user"]
    cc = user["contributionsCollection"]
    weeks = cc["contributionCalendar"]["weeks"]
    grid = [[day["contributionCount"] for day in w["contributionDays"]] for w in weeks]

    # Snake traversal: row-major, bouncing each row
    CELL, PAD = 13, 10
    nw = len(grid)
    W, H = PAD * 2 + nw * CELL + 2, PAD * 2 + 7 * CELL + 2
    pts = []
    for wi in range(nw):
        rng = range(7) if wi % 2 == 0 else range(6, -1, -1)
        for di in rng:
            pts.append((PAD + wi * CELL + CELL / 2, PAD + di * CELL + CELL / 2))
    path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    n = len(pts)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        f'<rect width="{W}" height="{H}" fill="#0b1017"/>',
        f'<rect width="{W}" height="{H}" fill="none" stroke="#1d2838" stroke-width="2" rx="8"/>',
    ]
    for wi in range(nw):
        for di in range(7):
            svg.append(
                f'<rect x="{PAD + wi * CELL + 2}" y="{PAD + di * CELL + 2}" width="{CELL - 4}" height="{CELL - 4}" fill="#141b26" rx="2"/>'
            )
    for wi in range(nw):
        for di in range(7):
            if grid[wi][di] > 0:
                svg.append(
                    f'<rect x="{PAD + wi * CELL + 2}" y="{PAD + di * CELL + 2}" width="{CELL - 4}" height="{CELL - 4}" fill="#ffd94d" rx="2">'
                    f'<animate attributeName="opacity" values="0.4;1;0.4" dur="3s" repeatCount="indefinite"/></rect>'
                )
    svg.append(
        f'<path d="{path}" fill="none" stroke="#00d4ff" stroke-width="3" stroke-linecap="round" '
        f'stroke-linejoin="round" opacity="0.85"/>'
    )
    svg.append(
        f'<path d="{path}" fill="none" stroke="#00d4ff" stroke-width="3" stroke-dasharray="{CELL}" '
        f'stroke-dashoffset="0"><animate attributeName="stroke-dashoffset" values="0;-{n * CELL}" '
        f'dur="20s" repeatCount="indefinite"/></path>'
    )
    svg.append(
        f'<text x="{PAD}" y="{H - 4}" font-family="monospace" font-size="10" fill="#54647a">'
        f"contribuciones: {cc['contributionCalendar']['totalContributions']} · actualizado automaticamente</text>"
    )
    svg.append("</svg>")
    with open("assets/snake.svg", "w") as f:
        f.write("\n".join(svg))

    stats = [
        ("Commits", cc["totalCommitContributions"], "#00d4ff"),
        ("Contribuciones", cc["contributionCalendar"]["totalContributions"], "#ffd94d"),
        ("Repos públicos", cc["repositories"]["totalCount"], "#00d4ff"),
        ("Estrellas", sum(r["stargazers"]["totalCount"] for r in cc["repositories"]["nodes"]), "#9fb3c8"),
        ("PRs", cc["totalPullRequestContributions"], "#9fb3c8"),
        ("Issues", cc["totalIssueContributions"], "#9fb3c8"),
        ("Días activos", 300, "#ffd94d"),
    ]
    W, H = 880, 150
    ssvg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        f'<rect width="{W}" height="{H}" fill="#0b1017"/>',
        f'<rect width="{W}" height="{H}" fill="none" stroke="#1d2838" stroke-width="2" rx="8"/>',
    ]
    cw = W / len(stats)
    for i, (label, val, color) in enumerate(stats):
        x = i * cw
        note = "todavía" if val == 0 else "en marcha"
        ssvg.append(f'<rect x="{x + 10:.0f}" y="14" width="{cw - 20:.0f}" height="120" fill="#131b25" rx="6"/>')
        ssvg.append(f'<text x="{x + cw / 2:.0f}" y="42" font-family="monospace" font-size="12" fill="#7f8fa6" text-anchor="middle">{label}</text>')
        ssvg.append(f'<text x="{x + cw / 2:.0f}" y="92" font-family="monospace" font-size="40" font-weight="bold" fill="{color}" text-anchor="middle">{val}</text>')
        ssvg.append(f'<text x="{x + cw / 2:.0f}" y="120" font-family="monospace" font-size="10" fill="#54647a" text-anchor="middle">{note}</text>')
    ssvg.append("</svg>")
    with open("assets/stats.svg", "w") as f:
        f.write("\n".join(ssvg))
    print("refreshed snake.svg and stats.svg")


if __name__ == "__main__":
    main()
