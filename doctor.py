"""
Environment doctor.

Checks whether the machine has what Smart Test needs to run for real:
Python version, key Python deps, Ollama running with the required models, the
Playwright browsers, and a usable database. Each check is a small pure-ish
function returning (ok, message) so they can be unit tested without the
services actually being present.

Usage:
    python doctor.py
"""

import importlib
import shutil
import subprocess
import sys

REQUIRED_MODELS = ["mistral", "llava"]
# Modules that the real run path needs (the heavy stack)
RUNTIME_DEPS = ["playwright", "langchain_ollama"]
# Modules the unit suite / core needs
CORE_DEPS = ["sqlalchemy", "rich"]


def check_python_version(min_major=3, min_minor=9):
    v = sys.version_info
    ok = (v.major, v.minor) >= (min_major, min_minor)
    return ok, f"Python {v.major}.{v.minor} (need >= {min_major}.{min_minor})"


def check_dependency(module_name):
    try:
        importlib.import_module(module_name)
        return True, f"{module_name} importable"
    except ImportError:
        return False, f"{module_name} NOT installed"


def check_ollama_installed(which=shutil.which):
    ok = which("ollama") is not None
    return ok, "ollama binary found" if ok else "ollama not on PATH"


def check_ollama_models(runner=None):
    """Check required models are present via `ollama list`."""
    runner = runner or (lambda: subprocess.run(
        ["ollama", "list"], capture_output=True, text=True, timeout=10))
    try:
        result = runner()
    except FileNotFoundError:
        return False, "ollama not installed"
    except Exception as e:
        return False, f"could not query ollama: {e}"

    if getattr(result, "returncode", 1) != 0:
        return False, "ollama not running (start it with: ollama serve)"

    out = (result.stdout or "")
    missing = [m for m in REQUIRED_MODELS if m not in out]
    if missing:
        return False, f"missing models: {', '.join(missing)} (ollama pull <model>)"
    return True, f"models present: {', '.join(REQUIRED_MODELS)}"


def check_playwright_browsers(runner=None):
    """Playwright package importable AND a chromium build present."""
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        return False, "playwright not installed (pip install playwright)"

    # The browser binaries are separate from the package
    from pathlib import Path
    cache = Path.home() / ".cache" / "ms-playwright"
    has_browser = cache.exists() and any(cache.glob("chromium-*"))
    if has_browser:
        return True, "playwright + chromium present"
    return False, "playwright installed but browsers missing (playwright install chromium)"


def check_database():
    try:
        from database import init_db
        init_db()
        return True, "database reachable and schema present"
    except Exception as e:
        return False, f"database error: {e}"


def run_all_checks():
    """Run every check, return list of (name, ok, message)."""
    results = [
        ("python", *check_python_version()),
        ("database", *check_database()),
    ]
    for dep in CORE_DEPS:
        results.append((f"dep:{dep}", *check_dependency(dep)))
    results.append(("ollama", *check_ollama_installed()))
    results.append(("ollama-models", *check_ollama_models()))
    results.append(("playwright", *check_playwright_browsers()))
    for dep in RUNTIME_DEPS:
        results.append((f"runtime:{dep}", *check_dependency(dep)))
    return results


def main():
    from rich.console import Console
    console = Console()
    console.print("[bold]Smart Test - environment doctor[/bold]\n")

    results = run_all_checks()
    failures = 0
    for name, ok, msg in results:
        mark = "[green]OK  [/green]" if ok else "[red]FAIL[/red]"
        if not ok:
            failures += 1
        console.print(f"{mark} {name}: {msg}")

    console.print("")
    if failures == 0:
        console.print("[green]All checks passed. Ready to run real tests.[/green]")
    else:
        console.print(f"[yellow]{failures} check(s) failed. "
                      "You can still use --dry-run without the AI stack.[/yellow]")
    return failures


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
