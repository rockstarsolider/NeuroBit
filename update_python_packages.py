#!/usr/bin/env python
"""
update_packages.py – Upgrade outdated pip packages with Rich UI.
Run inside an activated virtual-environment:

    python update_packages.py
"""

from __future__ import annotations
import json, shutil, subprocess, sys
from typing import List

# ---------- optional Rich prettiness ----------------------------------------
try:
    from rich import print as rprint
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.table import Table
    from rich.panel import Panel

    RICH = True
    console = Console()
except ImportError:
    RICH = False
    console = None

# -----------------------------------------------------------------------------


def run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def fetch_outdated() -> list[dict]:
    proc = run([sys.executable, "-m", "pip", "list", "--outdated", "--format=json"])
    if proc.returncode != 0:
        sys.exit(proc.stderr or "pip list failed")
    return json.loads(proc.stdout or "[]")


# ──────────────────────────────────────────────────────────────────────────────
def print_table(pkgs: list[dict]) -> None:
    if not pkgs:
        (rprint if RICH else print)(
            "[bold green]✔ All packages are up-to-date[/]"
            if RICH
            else "All packages are up-to-date."
        )
        return

    if RICH:
        table = Table(title="Outdated packages", show_lines=False)
        table.add_column("#", style="bright_black", width=3, justify="right")
        table.add_column("Package", style="cyan", no_wrap=True)
        table.add_column("Current", style="magenta")
        table.add_column("Latest", style="green")
        for idx, p in enumerate(pkgs, 1):
            table.add_row(str(idx), p["name"], p["version"], p["latest_version"])
        console.print(table)
    else:
        width = shutil.get_terminal_size().columns
        print("=" * width)
        print("Outdated packages".center(width))
        print("=" * width)
        for idx, p in enumerate(pkgs, 1):
            print(
                f"{idx:>2}  {p['name']:<28} {p['version']:<15} → {p['latest_version']}"
            )
        print("=" * width)


# ──────────────────────────────────────────────────────────────────────────────
def ask_selection(pkgs: list[dict]) -> list[str]:
    if not pkgs:
        return []

    all_names = [p["name"] for p in pkgs]
    index_map = {str(i + 1): name for i, name in enumerate(all_names)}

    if RICH:
        msg = (
            "[b cyan]A[/]  upgrade [u]all[/]\n"
            "[b cyan]N[/]  [u]skip[/] upgrading\n"
            "[b cyan]1,3,5[/]  comma-separated [u]indices[/] or package names\n"
        )
        console.print(
            Panel(msg, title="Choose packages to upgrade", border_style="yellow")
        )
        choice = console.input("[bold yellow]› [/]").strip().lower()
    else:
        choice = input(
            "Upgrade packages?  a = all / comma-separated indices or names / n = none [n]: "
        ).strip().lower()

    if choice in {"a", "all"}:
        return all_names
    if choice in {"", "n", "none"}:
        return []

    selected: list[str] = []
    for token in [c.strip() for c in choice.split(",") if c.strip()]:
        if token in all_names:
            selected.append(token)
        elif token in index_map:
            selected.append(index_map[token])
        else:
            print(f"⚠ Unknown package or index: {token}")
    return selected


# ──────────────────────────────────────────────────────────────────────────────
def upgrade(packages: list[str]) -> None:
    if not packages:
        (rprint if RICH else print)("No packages selected for upgrade.")
        return

    if RICH:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
        )
        task = progress.add_task("[blue]Upgrading", total=len(packages))
        progress.start()

    for name in packages:
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", name]
        proc = run(cmd)
        ok = proc.returncode == 0
        if RICH:
            status = "[green]✔" if ok else "[red]✖"
            console.print(f"{status} {name}")
            progress.advance(task)
        else:
            print(f"{'✔' if ok else '✖'} {name}")
            if not ok:
                print(proc.stderr)

    if RICH:
        progress.stop()
        console.print("[bold green]Done.[/]")


def main() -> None:
    pkgs = fetch_outdated()
    print_table(pkgs)
    to_upgrade = ask_selection(pkgs)
    upgrade(to_upgrade)


if __name__ == "__main__":
    main()
