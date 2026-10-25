"""Bundle the browser app into ONE self-contained HTML file: web/India-Sim-Engine.html (opens offline except fonts)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_data import build  # noqa: E402


def bundle(out: Path = HERE / "India-Sim-Engine.html") -> Path:
    data_path = build()
    data = json.loads(data_path.read_text(encoding="utf-8"))
    tpl = (HERE / "index.template.html").read_text(encoding="utf-8")
    safe = lambda s: s.replace("</", "<\\/")  # noqa: E731  never close the <script> early
    html = (tpl.replace("/*__CSS__*/", (HERE / "app.css").read_text(encoding="utf-8"))
               .replace("/*__VER__*/", data["engine_version"])
               .replace("/*__DATA__*/", safe(json.dumps(data, separators=(",", ":"))))
               .replace("/*__ENGINE__*/", safe((HERE / "engine.js").read_text(encoding="utf-8")))
               .replace("/*__APP__*/", safe((HERE / "app.js").read_text(encoding="utf-8"))))
    out.write_text(html, encoding="utf-8")
    return out


if __name__ == "__main__":
    p = bundle()
    print(p, f"{p.stat().st_size / 1024:.0f} KB")
