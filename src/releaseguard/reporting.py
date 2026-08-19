import json
from pathlib import Path

from jinja2 import BaseLoader, Environment, select_autoescape

from releaseguard.models import ScanResult

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>ReleaseGuard report</title><style>
body{font-family:system-ui,sans-serif;margin:0;background:#f4f7fb;color:#172033}.wrap{max-width:960px;margin:40px auto;padding:0 20px}
.card{background:white;border-radius:14px;padding:24px;box-shadow:0 5px 20px #18315314;margin-bottom:18px}.score{font-size:48px;font-weight:750}
.pass{color:#087f5b}.warning{color:#b35c00}.blocked,.blocker{color:#c92a2a}.finding{border-left:4px solid #94a3b8;padding:12px 16px;margin:12px 0;background:#f8fafc}
code{overflow-wrap:anywhere}.meta{color:#667085}h1,h2{margin-top:0}
</style></head><body><main class="wrap"><section class="card"><h1>ReleaseGuard</h1>
<div class="score {{ result.status }}">{{ result.score }}/100</div><h2 class="{{ result.status }}">{{ result.status|upper }}</h2>
<p class="meta">Target: <code>{{ result.target }}</code> · Checks: {{ result.checks_run }} · Policy: v{{ result.policy_version }}</p></section>
<section class="card"><h2>Findings ({{ result.findings|length }})</h2>
{% if result.findings %}{% for item in result.findings %}<article class="finding {{ item.severity }}"><strong>{{ item.severity|upper }} · {{ item.check }}</strong>
<p>{{ item.message }}</p>{% if item.path %}<p><code>{{ item.path }}</code></p>{% endif %}{% if item.remediation %}<p><b>Fix:</b> {{ item.remediation }}</p>{% endif %}</article>{% endfor %}
{% else %}<p class="pass">All configured release checks passed.</p>{% endif %}</section></main></body></html>"""


def write_reports(result: ScanResult, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "releaseguard-report.json"
    html_path = output_dir / "releaseguard-report.html"
    json_path.write_text(json.dumps(result.model_dump(mode="json"), indent=2), encoding="utf-8")
    env = Environment(loader=BaseLoader(), autoescape=select_autoescape(["html"]))
    html_path.write_text(env.from_string(TEMPLATE).render(result=result), encoding="utf-8")
    return json_path, html_path

