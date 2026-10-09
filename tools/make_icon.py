"""Membuat assets/icon.ico dari logo programatis."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from allsave.branding import save_icon  # noqa: E402

if __name__ == "__main__":
    out = ROOT / "assets" / "icon.ico"
    out.parent.mkdir(exist_ok=True)
    save_icon(str(out))
    print(f"Icon dibuat: {out}")
