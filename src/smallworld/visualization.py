"""Interactive random-walk visualisation via vis.js.

Generates self-contained HTML pages that embed a vis.js graph together
with a walk-control panel.  The pages are designed to be served as
``<iframe>`` embeds inside the MkDocs documentation site.

The main entry points are:

* :func:`build_walk_visualization` — build the HTML string for one graph.
* :func:`save_walk_visualization`  — convenience wrapper that writes it to
  disk.

Node colour convention
----------------------
* **green**  — start node (initial position).
* **red**    — current walker position.
* **orange** — already visited.
* **blue**   — not yet visited.

Controls
--------
* **▶ Step**   — advance the walk by one step.
* **▶▶ Walk N** — advance *N* steps at once (configurable).
* **⏵ Auto**  — animate the walk at a configurable speed (ms / step).
* **↺ Reset**  — restart from the initial node.

Clicking any node in the graph re-starts the walk from that node.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from string import Template

import networkx as nx

from src.smallworld.plotting import _layout

__all__ = [
    "build_walk_visualization",
    "save_walk_visualization",
    "build_cover_time_visualization",
    "save_cover_time_visualization",
    "build_compare_times_visualization",
    "save_compare_times_visualization",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_walk_visualization(
    G: nx.Graph,
    *,
    start: int = 0,
    layout: str = "circular",
    height: str = "560px",
    seed: int = 42,
    scale: float = 350.0,
    title: str = "",
) -> str:
    """Generate a self-contained HTML page for interactive random-walk exploration.

    Parameters
    ----------
    G : networkx.Graph
        Graph to visualise.  Should be connected so the walker can reach
        every node.
    start : int, default 0
        Node where the walk begins.
    layout : {"circular", "spring"}, default ``"circular"``
        NetworkX layout used to position nodes initially.
    height : str, default ``"560px"``
        CSS height of the vis.js canvas.
    seed : int, default 42
        Random seed for the spring layout (ignored for circular).
    scale : float, default 350.0
        Scaling factor (pixels) passed to the layout function.
    title : str, default ``""``
        Optional heading rendered above the graph.

    Returns
    -------
    str
        A complete, UTF-8 HTML document.  Save it with
        :func:`save_walk_visualization` or embed it in an ``<iframe>``.
    """
    pos = _layout(G, layout, seed=seed, scale=scale)

    # ── vis.js node data ────────────────────────────────────────────────────
    nodes_data = []
    for node in sorted(G.nodes()):
        x, y = pos[node]
        nodes_data.append(
            {
                "id": node,
                "label": str(node),
                # vis.js Y grows downward; NetworkX Y grows upward → flip
                "x": round(float(x), 2),
                "y": round(float(-y), 2),
                "fixed": {"x": True, "y": True},
                "color": {
                    "background": "#4CAF50" if node == start else "#97C2FC",
                    "border": "#1B5E20" if node == start else "#2B7CE9",
                },
                "font": {"color": "#111111", "size": 12},
                "size": 16,
            }
        )

    edges_data = [{"from": u, "to": v} for u, v in G.edges()]

    # Adjacency list: keys are ints in Python → become strings in JSON
    adjacency: dict[int, list[int]] = {
        node: sorted(list(G.neighbors(node))) for node in G.nodes()
    }

    nodes_json = json.dumps(nodes_data, separators=(",", ":"))
    edges_json = json.dumps(edges_data, separators=(",", ":"))
    adj_json = json.dumps(
        {str(k): v for k, v in adjacency.items()}, separators=(",", ":")
    )

    n_nodes = G.number_of_nodes()
    title_html = (
        f"<h3 style='margin:0 0 6px;font-family:sans-serif;font-size:15px'>"
        f"{title}</h3>"
        if title
        else ""
    )

    # ── full HTML template ──────────────────────────────────────────────────
    return _HTML_TEMPLATE.format(
        title_html=title_html,
        nodes_json=nodes_json,
        edges_json=edges_json,
        adj_json=adj_json,
        start=start,
        n_nodes=n_nodes,
        height=height,
        start_label=str(start),
    )


def save_walk_visualization(
    G: nx.Graph,
    path: str | Path,
    *,
    start: int = 0,
    layout: str = "circular",
    height: str = "560px",
    seed: int = 42,
    scale: float = 350.0,
    title: str = "",
) -> Path:
    """Write the walk visualisation HTML to *path*.

    Parameters
    ----------
    G : networkx.Graph
        Graph to visualise.
    path : str or Path
        Destination ``.html`` file.
    start, layout, height, seed, scale, title
        Forwarded verbatim to :func:`build_walk_visualization`.

    Returns
    -------
    Path
        The path the file was written to.
    """
    path = Path(path)
    path.write_text(
        build_walk_visualization(
            G,
            start=start,
            layout=layout,
            height=height,
            seed=seed,
            scale=scale,
            title=title,
        ),
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Random Walk – SmallWorld</title>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: sans-serif; font-size: 13px; background: #fafafa; color: #222; }}

  #app {{
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 8px;
    gap: 6px;
  }}

  /* ── control bar ── */
  #controls {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px 12px;
  }}
  .ctrl-group {{ display: flex; align-items: center; gap: 5px; }}

  button {{
    padding: 5px 13px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    transition: filter .15s;
  }}
  button:hover   {{ filter: brightness(0.88); }}
  button:active  {{ filter: brightness(0.78); }}
  button:disabled{{ opacity: .45; cursor: default; filter: none; }}

  #btn-step  {{ background: #1976D2; color: #fff; }}
  #btn-walkn {{ background: #388E3C; color: #fff; }}
  #btn-auto  {{ background: #F57C00; color: #fff; }}
  #btn-reset {{ background: #C62828; color: #fff; }}

  input[type=number] {{
    width: 58px;
    padding: 4px 6px;
    border: 1px solid #bbb;
    border-radius: 4px;
    font-size: 13px;
  }}
  label {{ font-size: 12px; color: #666; }}

  /* ── stats bar ── */
  #stats-bar {{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }}
  #stats {{
    background: #f0f4f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 13px;
    white-space: nowrap;
  }}
  .legend {{
    display: flex;
    gap: 12px;
    font-size: 12px;
    color: #555;
  }}
  .dot {{
    display: inline-block;
    width: 11px; height: 11px;
    border-radius: 50%;
    margin-right: 3px;
    vertical-align: middle;
  }}

  /* ── trace box ── */
  #trace-box {{
    font-size: 11px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px 8px;
    max-height: 46px;
    overflow-y: auto;
    color: #555;
    line-height: 1.5;
  }}

  /* ── graph canvas ── */
  #graph {{
    flex: 1;
    border: 1px solid #ddd;
    border-radius: 6px;
    background: #ffffff;
  }}
</style>
</head>
<body>
<div id="app">

  {title_html}

  <!-- ── controls ── -->
  <div id="controls">
    <button id="btn-step">▶ Step</button>

    <div class="ctrl-group">
      <button id="btn-walkn">▶▶ Walk</button>
      <label>N =</label>
      <input type="number" id="n-input" value="5" min="1" max="10000">
    </div>

    <div class="ctrl-group">
      <button id="btn-auto">⏵ Auto</button>
      <label>ms =</label>
      <input type="number" id="speed-input" value="400" min="50" max="5000" step="50">
    </div>

    <button id="btn-reset">↺ Reset</button>
  </div>

  <!-- ── stats + legend ── -->
  <div id="stats-bar">
    <div id="stats">Step: 0 &nbsp;|&nbsp; Visited: 1 / {n_nodes} &nbsp;|&nbsp; Current: {start_label}</div>
    <div class="legend">
      <span><span class="dot" style="background:#4CAF50;border:1.5px solid #1B5E20"></span>Start</span>
      <span><span class="dot" style="background:#FF4444;border:1.5px solid #C62828"></span>Current</span>
      <span><span class="dot" style="background:#FF9800;border:1.5px solid #E65100"></span>Visited</span>
      <span><span class="dot" style="background:#97C2FC;border:1.5px solid #2B7CE9"></span>Unvisited</span>
    </div>
  </div>

  <!-- ── trace ── -->
  <div id="trace-box">Path: <span id="trace-span">{start_label}</span></div>

  <!-- ── vis.js canvas ── -->
  <div id="graph" style="height:{height}"></div>

</div><!-- #app -->

<script>
// ── graph data (injected by Python) ─────────────────────────────────────────
const NODES_DATA = {nodes_json};
const EDGES_DATA = {edges_json};
const ADJ        = {adj_json};   // keys are strings (JSON limitation)
const START      = {start};
const N_NODES    = {n_nodes};

// ── vis.js setup ─────────────────────────────────────────────────────────────
const nodesDS = new vis.DataSet(NODES_DATA);
const edgesDS = new vis.DataSet(EDGES_DATA);

const network = new vis.Network(
  document.getElementById('graph'),
  {{ nodes: nodesDS, edges: edgesDS }},
  {{
    physics: false,
    interaction: {{
      dragNodes: false,
      zoomView: true,
      hover: true,
    }},
    edges: {{
      color: {{ color: '#bbbbbb', highlight: '#555555' }},
      width: 1.5,
      smooth: {{ enabled: false }},
    }},
    nodes: {{
      shape: 'dot',
      borderWidth: 1.5,
    }},
  }}
);

// ── walk state ───────────────────────────────────────────────────────────────
let currentNode = START;
let stepCount   = 0;
let visited     = new Set([START]);
let traceArr    = [START];
let autoTimer   = null;
let autoPlaying = false;

// ── colour constants ─────────────────────────────────────────────────────────
const C = {{
  unvisited: {{ background: '#97C2FC', border: '#2B7CE9' }},
  visited:   {{ background: '#FF9800', border: '#E65100' }},
  current:   {{ background: '#FF4444', border: '#C62828' }},
  start:     {{ background: '#4CAF50', border: '#1B5E20' }},
}};

function nodeColor(id) {{
  if (id === currentNode) return C.current;
  if (id === START)       return C.start;
  if (visited.has(id))   return C.visited;
  return C.unvisited;
}}

function refreshColors() {{
  nodesDS.update(
    nodesDS.map(n => ({{ id: n.id, color: nodeColor(n.id) }}))
  );
}}

// ── walk core ────────────────────────────────────────────────────────────────
function walkStep() {{
  const neighbors = ADJ[String(currentNode)];
  if (!neighbors || neighbors.length === 0) return;          // isolated node
  currentNode = neighbors[Math.floor(Math.random() * neighbors.length)];
  visited.add(currentNode);
  stepCount++;
  traceArr.push(currentNode);
  if (traceArr.length > 300) traceArr = traceArr.slice(-300); // cap trace
  refreshColors();
  updateStats();
}}

function reset(newStart) {{
  stopAuto();
  currentNode = (newStart !== undefined) ? newStart : START;
  stepCount   = 0;
  visited     = new Set([currentNode]);
  traceArr    = [currentNode];
  refreshColors();
  updateStats();
}}

function updateStats() {{
  document.getElementById('stats').innerHTML =
    `Step: ${{stepCount}} &nbsp;|&nbsp; Visited: ${{visited.size}} / ${{N_NODES}} &nbsp;|&nbsp; Current: ${{currentNode}}`;
  const span = document.getElementById('trace-span');
  span.textContent = traceArr.join(' → ');
  const box = document.getElementById('trace-box');
  box.scrollTop = box.scrollHeight;
}}

// ── auto-play ─────────────────────────────────────────────────────────────────
function startAuto() {{
  const ms = Math.max(50, parseInt(document.getElementById('speed-input').value) || 400);
  autoTimer   = setInterval(walkStep, ms);
  autoPlaying = true;
  document.getElementById('btn-auto').textContent = '⏸ Pause';
}}

function stopAuto() {{
  clearInterval(autoTimer);
  autoTimer   = null;
  autoPlaying = false;
  document.getElementById('btn-auto').textContent = '⏵ Auto';
}}

// ── button wiring ─────────────────────────────────────────────────────────────
document.getElementById('btn-step').onclick = () => walkStep();

document.getElementById('btn-walkn').onclick = () => {{
  const n = Math.max(1, parseInt(document.getElementById('n-input').value) || 5);
  for (let i = 0; i < n; i++) walkStep();
}};

document.getElementById('btn-auto').onclick = () => {{
  if (autoPlaying) stopAuto(); else startAuto();
}};

document.getElementById('btn-reset').onclick = () => reset();

// click on node → restart walk from that node
network.on('click', params => {{
  if (params.nodes.length === 1) reset(params.nodes[0]);
}});

// ── initialise ───────────────────────────────────────────────────────────────
refreshColors();
updateStats();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Cover-time simulation visualisation
# ---------------------------------------------------------------------------

def build_cover_time_visualization(
    G: nx.Graph,
    *,
    title: str = "",
) -> str:
    """Generate a self-contained HTML page for interactive cover-time simulation.

    The page embeds the graph adjacency list and runs the cover-time algorithm
    entirely in JavaScript, so no server is required.  Users can choose the
    number of simulations and view the resulting distribution as a histogram.

    Parameters
    ----------
    G : networkx.Graph
        Graph to simulate on.
    title : str, default ``""``
        Optional heading rendered above the controls.

    Returns
    -------
    str
        A complete, UTF-8 HTML document.
    """
    adjacency: dict[str, list[int]] = {
        str(node): sorted(list(G.neighbors(node))) for node in G.nodes()
    }
    adj_json = json.dumps(adjacency, separators=(",", ":"))
    n_nodes  = G.number_of_nodes()
    title_html = (
        f"<h3>{title}</h3>"
        if title
        else ""
    )
    return _COVER_TIME_HTML_TEMPLATE.format(
        title_html=title_html,
        adj_json=adj_json,
        n_nodes=n_nodes,
    )


def save_cover_time_visualization(
    G: nx.Graph,
    path: "str | Path",
    *,
    title: str = "",
) -> "Path":
    """Write the cover-time visualisation HTML to *path*.

    Parameters
    ----------
    G : networkx.Graph
        Graph to simulate on.
    path : str or Path
        Destination ``.html`` file.
    title : str, default ``""``
        Forwarded to :func:`build_cover_time_visualization`.

    Returns
    -------
    Path
        The path the file was written to.
    """
    path = Path(path)
    path.write_text(
        build_cover_time_visualization(G, title=title),
        encoding="utf-8",
    )
    return path


_COVER_TIME_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cover Time – SmallWorld</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: sans-serif;
    font-size: 13px;
    background: #fafafa;
    color: #222;
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 10px;
    gap: 8px;
    overflow: hidden;
  }}
  h3 {{ font-size: 15px; flex-shrink: 0; margin-bottom: 2px; }}
  #controls {{
    display: flex;
    align-items: center;
    gap: 10px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px 12px;
    flex-shrink: 0;
    flex-wrap: wrap;
  }}
  label {{ font-size: 12px; color: #666; }}
  input[type=number] {{
    width: 80px;
    padding: 4px 6px;
    border: 1px solid #bbb;
    border-radius: 4px;
    font-size: 13px;
  }}
  button {{
    padding: 5px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    background: #1976D2;
    color: #fff;
    transition: filter .15s;
  }}
  button:hover  {{ filter: brightness(0.88); }}
  button:active {{ filter: brightness(0.78); }}
  button:disabled {{ opacity: .45; cursor: default; filter: none; }}
  #status {{ font-size: 12px; color: #888; }}
  #stats-row {{
    display: none;
    flex-direction: row;
    gap: 8px;
    flex-shrink: 0;
  }}
  .stat-card {{
    flex: 1;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px 10px;
    text-align: center;
  }}
  .stat-value {{ font-size: 22px; font-weight: 700; color: #1976D2; }}
  .stat-label {{ font-size: 10px; color: #888; margin-top: 2px; }}
  #chart-box {{
    display: none;
    flex: 1;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 0;
  }}
  #chart-lbl {{ font-size: 11px; color: #666; text-align: center; margin-bottom: 4px; }}
  #histogram {{ display: block; }}
</style>
</head>
<body>
{title_html}
<div id="controls">
  <label for="n-sims">Simulations:</label>
  <input type="number" id="n-sims" value="200" min="1" max="2000">
  <button id="run-btn">&#9654; Run</button>
  <span id="status">Press Run to start.</span>
</div>
<div id="stats-row">
  <div class="stat-card">
    <div class="stat-value" id="stat-avg">—</div>
    <div class="stat-label">Average cover time</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="stat-std">—</div>
    <div class="stat-label">Std deviation</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="stat-min">—</div>
    <div class="stat-label">Minimum</div>
  </div>
  <div class="stat-card">
    <div class="stat-value" id="stat-max">—</div>
    <div class="stat-label">Maximum</div>
  </div>
</div>
<div id="chart-box">
  <div id="chart-lbl">Cover time distribution (steps to visit all {n_nodes} nodes)</div>
  <canvas id="histogram"></canvas>
</div>
<script>
const ADJ     = {adj_json};
const N_NODES = {n_nodes};

function singleCoverTime() {{
  const keys    = Object.keys(ADJ);
  let current   = parseInt(keys[Math.floor(Math.random() * keys.length)]);
  const toVisit = new Set(keys.map(Number));
  toVisit.delete(current);
  let steps     = 0;
  const MAX     = 100000;
  while (toVisit.size > 0 && steps < MAX) {{
    const nb = ADJ[String(current)];
    current  = nb[Math.floor(Math.random() * nb.length)];
    toVisit.delete(current);
    steps++;
  }}
  return toVisit.size === 0 ? steps : null;
}}

function drawHistogram(data) {{
  const box    = document.getElementById('chart-box');
  const canvas = document.getElementById('histogram');
  const W      = box.clientWidth > 0  ? box.clientWidth  - 24 : 500;
  const H      = box.clientHeight > 0 ? box.clientHeight - 44 : 200;
  canvas.width  = Math.max(200, W);
  canvas.height = Math.max(140, H);

  const ctx  = canvas.getContext('2d');
  const minV = Math.min(...data), maxV = Math.max(...data);
  const range = maxV - minV || 1;
  const nBins = Math.min(40, Math.max(10, Math.ceil(Math.sqrt(data.length))));
  const binW  = range / nBins;

  const bins = new Array(nBins).fill(0);
  data.forEach(v => {{
    const b = Math.min(nBins - 1, Math.floor((v - minV) / binW));
    bins[b]++;
  }});
  const maxCount = Math.max(...bins);

  const pad = {{ t: 10, r: 10, b: 30, l: 42 }};
  const cW  = canvas.width  - pad.l - pad.r;
  const cH  = canvas.height - pad.t - pad.b;
  const bW  = cW / nBins;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = '#f0f0f0';
  ctx.lineWidth   = 1;
  for (let i = 1; i <= 4; i++) {{
    const y = pad.t + cH * (1 - i / 4);
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(pad.l + cW, y); ctx.stroke();
  }}

  ctx.fillStyle = '#1976D2';
  bins.forEach((count, i) => {{
    const bH = (count / maxCount) * cH;
    ctx.fillRect(pad.l + i * bW, pad.t + cH - bH, Math.max(1, bW - 1), bH);
  }});

  ctx.strokeStyle = '#aaa';
  ctx.lineWidth   = 1;
  ctx.beginPath();
  ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, pad.t + cH);
  ctx.lineTo(pad.l + cW, pad.t + cH);
  ctx.stroke();

  ctx.fillStyle = '#666';
  ctx.font      = '10px sans-serif';
  ctx.textAlign = 'center';
  for (let i = 0; i <= 5; i++) {{
    const x   = pad.l + (i / 5) * cW;
    const val = Math.round(minV + (i / 5) * range);
    ctx.fillText(val, x, pad.t + cH + 14);
  }}
  ctx.textAlign = 'right';
  ctx.fillText(maxCount, pad.l - 3, pad.t + 9);
  ctx.fillText('0',      pad.l - 3, pad.t + cH);
}}

document.getElementById('run-btn').addEventListener('click', () => {{
  const n      = Math.max(1, Math.min(2000, parseInt(document.getElementById('n-sims').value) || 200));
  const btn    = document.getElementById('run-btn');
  const status = document.getElementById('status');
  btn.disabled       = true;
  status.textContent = 'Running…';

  setTimeout(() => {{
    const results = [];
    for (let i = 0; i < n; i++) {{
      const t = singleCoverTime();
      if (t !== null) results.push(t);
    }}

    if (results.length === 0) {{
      status.textContent = 'No simulations converged.';
      btn.disabled = false;
      return;
    }}

    const avg = results.reduce((a, b) => a + b, 0) / results.length;
    const std = Math.sqrt(results.reduce((a, b) => a + (b - avg) ** 2, 0) / results.length);

    document.getElementById('stat-avg').textContent = avg.toFixed(1);
    document.getElementById('stat-std').textContent = std.toFixed(1);
    document.getElementById('stat-min').textContent = Math.min(...results);
    document.getElementById('stat-max').textContent = Math.max(...results);

    document.getElementById('stats-row').style.display = 'flex';
    document.getElementById('chart-box').style.display = 'block';
    drawHistogram(results);

    status.textContent = 'Done — ' + results.length + ' simulation' + (results.length > 1 ? 's' : '') + '.';
    btn.disabled = false;
  }}, 10);
}});
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Compare-times visualisation (Ring vs WS vs ER — cover time + mixing time)
# ---------------------------------------------------------------------------

def build_compare_times_visualization(
    *,
    N: int = 30,
    k: int = 4,
    beta: float = 0.1,
) -> str:
    """Generate the interactive comparison page (Ring / WS / ER).

    The page builds all three graphs entirely in JavaScript and lets the user
    run animated cover-time walks and mixing-time simulations side by side.
    No server or NetworkX graph is required — everything is self-contained.

    Parameters
    ----------
    N : int, default 30
        Initial number of nodes shown in the UI slider.
    k : int, default 4
        Initial mean degree shown in the UI slider.
    beta : float, default 0.1
        Initial Watts–Strogatz rewiring probability (must be in ``(0, 1]``).

    Returns
    -------
    str
        A complete, UTF-8 HTML document ready to be saved or embedded.
    """
    beta = max(1e-4, min(1.0, beta))
    return _COMPARE_TIMES_TEMPLATE.substitute(
        N=N,
        k=k,
        beta_log10=f"{math.log10(beta):.4f}",
        beta_str=f"{beta:.3f}",
    )


def save_compare_times_visualization(
    path: str | Path,
    *,
    N: int = 30,
    k: int = 4,
    beta: float = 0.1,
) -> Path:
    """Write the compare-times visualisation HTML to *path*.

    Parameters
    ----------
    path : str or Path
        Destination ``.html`` file.
    N, k, beta
        Forwarded to :func:`build_compare_times_visualization`.

    Returns
    -------
    Path
        The path the file was written to.
    """
    path = Path(path)
    path.write_text(
        build_compare_times_visualization(N=N, k=k, beta=beta),
        encoding="utf-8",
    )
    return path


# ``string.Template`` is used here (instead of str.format) so that the
# JavaScript curly-braces do not need to be doubled.  Only the five
# ``$placeholder`` tokens are substituted; everything else is literal.
_COMPARE_TIMES_TEMPLATE = Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Watts–Strogatz Explorer – SmallWorld</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: sans-serif;
  font-size: 12px;
  background: #f0f2f5;
  color: #222;
  padding: 8px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow: hidden;
}

/* ── Controls ───────────────────────────────────────────────────── */
#controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 7px 12px;
  height: 42px;
  flex-shrink: 0;
}
.cg { display: flex; align-items: center; gap: 4px; white-space: nowrap; }
label { font-size: 11px; color: #555; }
input[type=number] {
  width: 52px; padding: 2px 4px;
  border: 1px solid #bbb; border-radius: 3px; font-size: 11px;
}
input[type=range] { width: 120px; cursor: pointer; accent-color: #1565C0; }
#beta-badge {
  font-size: 12px; font-weight: 700;
  background: #e8f0fe; color: #1a56db;
  border-radius: 3px; padding: 1px 6px; min-width: 44px; text-align: center;
}
select {
  padding: 2px 4px; border: 1px solid #bbb; border-radius: 3px; font-size: 11px; cursor: pointer;
}

/* ── Node-colour legend ───────────────────────────────────────────────── */
#legend {
  display: flex;
  justify-content: center;
  gap: 12px;
  font-size: 10px;
  color: #666;
  height: 16px;
  align-items: center;
  flex-shrink: 0;
}
#legend span { display: flex; align-items: center; gap: 3px; }
.dot {
  display: inline-block; width: 10px; height: 10px;
  border-radius: 50%; flex-shrink: 0;
}

/* ── Three panels ───────────────────────────────────────────────────── */
#panels {
  display: flex;
  gap: 7px;
  flex: 1;
  min-height: 0;
}

.panel {
  flex: 1;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

/* header */
.ph {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
  height: 26px;
}
.ph-name { font-size: 11px; font-weight: 700; }
.ph-tick { font-size: 15px; color: #2e7d32; display: none; line-height: 1; }
.ph-tick.show { display: block; }

/* network canvas */
canvas.nc {
  display: block;
  width: 100%;
  flex: 1;
}

/* status row */
.ps {
  padding: 3px 8px;
  font-size: 10px;
  color: #666;
  background: #fafafa;
  border-top: 1px solid #eee;
  text-align: center;
  flex-shrink: 0;
  height: 22px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* distribution section */
.dist {
  border-top: 1px solid #eee;
  flex-shrink: 0;
  height: 75px;
  display: flex;
  flex-direction: column;
  padding: 3px 5px 4px;
}
.dist-lbl {
  font-size: 9px;
  color: #aaa;
  text-align: center;
  flex-shrink: 0;
  height: 12px;
  line-height: 12px;
}
canvas.dc {
  display: block;
  width: 100%;
  flex: 1;
}

/* ── Run bar ──────────────────────────────────────────────────────────────── */
#run-bar {
  display: flex;
  align-items: center;
  gap: 7px;
  height: 34px;
  flex-wrap: nowrap;
  flex-shrink: 0;
}
button {
  padding: 5px 12px; border: none; border-radius: 4px;
  cursor: pointer; font-size: 11px; font-weight: 600; color: #fff;
  transition: filter .12s; white-space: nowrap; flex-shrink: 0;
}
button:hover   { filter: brightness(0.87); }
button:active  { filter: brightness(0.74); }
button:disabled { opacity: .35; cursor: not-allowed; filter: none; }
#btn-cover  { background: #1565C0; }
#btn-mixing { background: #6A1B9A; }
#btn-reset  { background: #546E7A; font-size: 10px; padding: 4px 9px; }

#statusbar { font-size: 10px; color: #888; font-style: italic; flex: 1; min-width: 0; }

/* ── Progress strip ──────────────────────────────────────────────────── */
#pgwrap { height: 3px; background: #e0e0e0; border-radius: 2px; overflow: hidden; flex-shrink: 0; }
#pgfill { height: 100%; background: #1565C0; width: 0%; transition: width .2s; }
</style>
</head>
<body>

<!-- ── Controls ────────────────────────────────────────────────────────────────── -->
<div id="controls">
  <div class="cg"><label>N =</label><input type="number" id="inp-N" value="$N" min="10" max="50"></div>
  <div class="cg"><label>k =</label><input type="number" id="inp-k" value="$k" min="2" max="10" step="2"></div>
  <div class="cg">
    <label>β =</label>
    <input type="range" id="inp-beta" min="-3" max="0" step="0.04" value="$beta_log10">
    <span id="beta-badge">$beta_str</span>
  </div>
  <div class="cg">
    <label>Speed:</label>
    <select id="inp-speed">
      <option value="3">Slow</option>
      <option value="10" selected>Normal</option>
      <option value="40">Fast</option>
      <option value="99999">Instant</option>
    </select>
  </div>
</div>

<!-- ── Legend ────────────────────────────────────────────────────────────────────── -->
<div id="legend">
  <span><span class="dot" style="background:#4CAF50;outline:1.5px solid #1B5E20"></span>Start</span>
  <span><span class="dot" style="background:#FF4444;outline:1.5px solid #C62828"></span>Current</span>
  <span><span class="dot" style="background:#FF9800;outline:1.5px solid #E65100"></span>Visited</span>
  <span><span class="dot" style="background:#97C2FC;outline:1.5px solid #2B7CE9"></span>Unvisited</span>
  <span style="margin-left:6px"><span class="dot" style="background:#f47c2e;border-radius:0;height:2px;width:14px"></span> shortcut</span>
</div>

<!-- ── Three panels ──────────────────────────────────────────────────────────────────── -->
<div id="panels">

  <!-- Ring -->
  <div class="panel">
    <div class="ph">
      <span class="ph-name" style="color:#c62828">Ring lattice &thinsp;(β = 0)</span>
      <span class="ph-tick" id="tk-ring">✓</span>
    </div>
    <canvas class="nc" id="cv-ring"></canvas>
    <div class="ps" id="st-ring">L = — &nbsp;·  C = —</div>
    <div class="dist">
      <div class="dist-lbl" id="dl-ring">stationary distribution π(node) — run Mixing Time</div>
      <canvas class="dc" id="dv-ring"></canvas>
    </div>
  </div>

  <!-- WS -->
  <div class="panel">
    <div class="ph">
      <span class="ph-name" id="ws-hdr" style="color:#1565C0">Watts–Strogatz &thinsp;(β = $beta_str)</span>
      <span class="ph-tick" id="tk-ws">✓</span>
    </div>
    <canvas class="nc" id="cv-ws"></canvas>
    <div class="ps" id="st-ws">L = — &nbsp;·  C = —</div>
    <div class="dist">
      <div class="dist-lbl" id="dl-ws">stationary distribution π(node) — run Mixing Time</div>
      <canvas class="dc" id="dv-ws"></canvas>
    </div>
  </div>

  <!-- ER -->
  <div class="panel">
    <div class="ph">
      <span class="ph-name" style="color:#2e7d32">Erdős–Rényi &thinsp;(p = k/(N−1))</span>
      <span class="ph-tick" id="tk-er">✓</span>
    </div>
    <canvas class="nc" id="cv-er"></canvas>
    <div class="ps" id="st-er">L = — &nbsp;·  C = —</div>
    <div class="dist">
      <div class="dist-lbl" id="dl-er">stationary distribution π(node) — run Mixing Time</div>
      <canvas class="dc" id="dv-er"></canvas>
    </div>
  </div>

</div>

<!-- ── Run bar ────────────────────────────────────────────────────────────────────── -->
<div id="run-bar">
  <button id="btn-cover">▶ Cover Time</button>
  <button id="btn-mixing">▶ Mixing Time</button>
  <button id="btn-reset">↺ Reset</button>
  <span id="statusbar">Adjust β — the graph updates live. Then run a simulation.</span>
</div>
<div id="pgwrap"><div id="pgfill"></div></div>

<script>
// ═══════════════════════════════════════════════════════════════════════
// Constants & state
// ═══════════════════════════════════════════════════════════════════════
const NAMES = ['ring', 'ws', 'er'];
const COL   = { ring: '#c62828', ws: '#1565C0', er: '#2e7d32' };

let graphs   = {};
let walkers  = {};
let animTmr  = null;
let isRunning = false;

// ═══════════════════════════════════════════════════════════════════════
// Seeded PRNG
// ═══════════════════════════════════════════════════════════════════════
function mkRng(seed) {
  let s = (seed || 1) >>> 0;
  return () => { s ^= s<<13; s ^= s>>>17; s ^= s<<5; return (s>>>0)/0x100000000; };
}

// ═══════════════════════════════════════════════════════════════════════
// Graph builders
// ═══════════════════════════════════════════════════════════════════════
function buildRing(N, k) {
  const adj = Array.from({length:N}, ()=>new Set()), h = k>>1;
  for (let i=0;i<N;i++) for (let d=1;d<=h;d++) { const j=(i+d)%N; adj[i].add(j); adj[j].add(i); }
  return { adj: adj.map(s=>[...s]), shortcuts: new Set() };
}

function buildER(N, k, rng) {
  const p = k/(N-1), adj = Array.from({length:N}, ()=>new Set());
  for (let i=0;i<N;i++) for (let j=i+1;j<N;j++) if (rng()<p) { adj[i].add(j); adj[j].add(i); }
  return { adj: adj.map(s=>[...s]), shortcuts: null };
}

function buildWS(N, k, beta, rng) {
  const adj = Array.from({length:N}, ()=>new Set()), h = k>>1;
  for (let i=0;i<N;i++) for (let d=1;d<=h;d++) { const j=(i+d)%N; adj[i].add(j); adj[j].add(i); }
  const sc = new Set();
  for (let i=0;i<N;i++) for (let d=1;d<=h;d++) {
    const j=(i+d)%N;
    if (!adj[i].has(j)) continue;
    if (rng()<beta) {
      adj[i].delete(j); adj[j].delete(i);
      let nj, t=0;
      do { nj=Math.floor(rng()*N); t++; } while ((nj===i||adj[i].has(nj))&&t<N*3);
      if (t<N*3) { adj[i].add(nj); adj[nj].add(i); sc.add(Math.min(i,nj)+','+Math.max(i,nj)); }
      else       { adj[i].add(j);  adj[j].add(i); }
    }
  }
  return { adj: adj.map(s=>[...s]), shortcuts: sc };
}

// ═══════════════════════════════════════════════════════════════════════
// Metrics
// ═══════════════════════════════════════════════════════════════════════
function apl(adj) {
  const N=adj.length; let tot=0,cnt=0;
  for (let s=0;s<N;s++) {
    const d=new Int32Array(N).fill(-1); d[s]=0;
    const q=[s]; let qi=0;
    while (qi<q.length) { const u=q[qi++]; for (const v of adj[u]) if(d[v]<0){d[v]=d[u]+1;q.push(v);} }
    for (let t=0;t<N;t++) if(t!==s&&d[t]>0){tot+=d[t];cnt++;}
  }
  return cnt?tot/cnt:Infinity;
}

function cc(adj) {
  const N=adj.length, sets=adj.map(a=>new Set(a));
  let sum=0,nodes=0;
  for (let i=0;i<N;i++) {
    const nb=adj[i],deg=nb.length; if(deg<2)continue;
    let cl=0;
    for (let a=0;a<deg;a++) for (let b=a+1;b<deg;b++) if(sets[nb[a]].has(nb[b]))cl++;
    sum+=cl/(deg*(deg-1)/2); nodes++;
  }
  return nodes?sum/nodes:0;
}

// ═══════════════════════════════════════════════════════════════════════
// Canvas helpers
// ═══════════════════════════════════════════════════════════════════════
function setupCanvas(canvas) {
  const dpr=window.devicePixelRatio||1;
  const W=canvas.clientWidth||200, H=canvas.clientHeight||160;
  canvas.width=W*dpr; canvas.height=H*dpr;
  canvas.style.width=W+'px'; canvas.style.height=H+'px';
  const ctx=canvas.getContext('2d'); ctx.scale(dpr,dpr);
  ctx.clearRect(0,0,W,H);
  return {ctx,W,H};
}

function circPos(N,cx,cy,r) {
  return Array.from({length:N},(_,i)=>[cx+r*Math.cos(2*Math.PI*i/N-Math.PI/2),
                                        cy+r*Math.sin(2*Math.PI*i/N-Math.PI/2)]);
}

// ═══════════════════════════════════════════════════════════════════════
// Network drawing
// ═══════════════════════════════════════════════════════════════════════
function drawNet(name, walkerState) {
  const canvas=document.getElementById('cv-'+name);
  const {ctx,W,H}=setupCanvas(canvas);
  const {adj,shortcuts}=graphs[name];
  const N=adj.length; if(!N)return;
  const pad=16, r=Math.min(W,H)/2-pad;
  const pos=circPos(N,W/2,H/2,r);
  const nodeR=Math.max(4,Math.min(7,90/N));

  // Edges
  const loc=[], sc=[];
  for (let i=0;i<N;i++) for (const j of adj[i]) {
    if(j<=i)continue;
    (shortcuts&&shortcuts.has(i+','+j)?sc:loc).push([i,j]);
  }
  ctx.globalAlpha=0.45; ctx.lineWidth=1; ctx.strokeStyle='#90b8e8';
  for(const[i,j]of loc){ctx.beginPath();ctx.moveTo(...pos[i]);ctx.lineTo(...pos[j]);ctx.stroke();}
  ctx.globalAlpha=0.9; ctx.lineWidth=2; ctx.strokeStyle='#f47c2e';
  for(const[i,j]of sc){ctx.beginPath();ctx.moveTo(...pos[i]);ctx.lineTo(...pos[j]);ctx.stroke();}
  ctx.globalAlpha=1;

  // Nodes
  const w=walkerState;
  for (let i=0;i<N;i++) {
    let fill,stroke,lw;
    if (w&&w.current===i)                    { fill='#FF4444'; stroke='#B71C1C'; lw=1.5; }
    else if (w&&i===w.start)                 { fill='#4CAF50'; stroke='#1B5E20'; lw=1.5; }
    else if (w&&w.visited&&w.visited.has(i)) { fill='#FF9800'; stroke='#E65100'; lw=1; }
    else                                     { fill='#7eb3f5'; stroke='#1a6bc4'; lw=1; }
    ctx.fillStyle=fill; ctx.strokeStyle=stroke; ctx.lineWidth=lw;
    ctx.beginPath(); ctx.arc(...pos[i],nodeR,0,Math.PI*2); ctx.fill(); ctx.stroke();
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Distribution chart
// ═══════════════════════════════════════════════════════════════════════
function drawDist(name, dist, iterStr) {
  const canvas=document.getElementById('dv-'+name);
  const {ctx,W,H}=setupCanvas(canvas);
  const N=dist.length;
  const pad={t:2,r:2,b:11,l:2};
  const cW=W-pad.l-pad.r, cH=H-pad.t-pad.b;
  const maxV=Math.max(...dist)*1.12||1;
  const barW=Math.max(1,cW/N-0.4);

  const yu=pad.t+cH-(1/N/maxV)*cH;
  ctx.strokeStyle='#ccc'; ctx.lineWidth=0.8; ctx.setLineDash([2,2]);
  ctx.beginPath(); ctx.moveTo(pad.l,yu); ctx.lineTo(pad.l+cW,yu); ctx.stroke();
  ctx.setLineDash([]);

  for(let i=0;i<N;i++){
    const bH=(dist[i]/maxV)*cH;
    const x=pad.l+i*(cW/N), y=pad.t+cH-bH;
    const t=dist[i]/maxV;
    ctx.fillStyle=`hsl(210,65%,$${65-t*40}%)`;
    ctx.fillRect(x,y,barW,bH);
  }

  ctx.strokeStyle='#ddd'; ctx.lineWidth=0.8;
  ctx.beginPath(); ctx.moveTo(pad.l,pad.t+cH); ctx.lineTo(pad.l+cW,pad.t+cH); ctx.stroke();

  ctx.fillStyle='#999'; ctx.font='8px sans-serif';
  ctx.textAlign='left';  ctx.fillText('π(i)', pad.l, H-1);
  ctx.textAlign='right'; ctx.fillText(iterStr, pad.l+cW, H-1);

  document.getElementById('dl-'+name).textContent='stationary distribution π(node) — '+iterStr;
  document.getElementById('dl-'+name).style.color='#555';
}

function clearDist(name) {
  const canvas=document.getElementById('dv-'+name);
  const {ctx,W,H}=setupCanvas(canvas);
  ctx.fillStyle='#f8f8f8'; ctx.fillRect(0,0,W,H);
  ctx.strokeStyle='#eee'; ctx.lineWidth=0.5;
  ctx.beginPath(); ctx.moveTo(0,H/2); ctx.lineTo(W,H/2); ctx.stroke();
  document.getElementById('dl-'+name).textContent='stationary distribution π(node) — run Mixing Time';
  document.getElementById('dl-'+name).style.color='#aaa';
}

// ═══════════════════════════════════════════════════════════════════════
// Build graphs & render static state
// ═══════════════════════════════════════════════════════════════════════
function buildAndDraw() {
  const {N,k,beta}=getParams();
  graphs.ring = buildRing(N, k);
  graphs.er   = buildER(N, k, mkRng(42+N*97+k));
  graphs.ws   = buildWS(N, k, beta, mkRng(7+N*13));

  document.getElementById('ws-hdr').textContent='Watts–Strogatz  (β = '+beta.toFixed(3)+')';

  NAMES.forEach(name=>{
    drawNet(name, null);
    const {adj}=graphs[name];
    const L=apl(adj), C=cc(adj);
    const sc=graphs[name].shortcuts;
    let extra='';
    if(name==='ws') extra='  ·  '+( sc?sc.size:0)+' shortcuts';
    document.getElementById('st-'+name).textContent=
      'L = '+(isFinite(L)?L.toFixed(2):'∞')+'  ·  C = '+C.toFixed(3)+extra;
    document.getElementById('tk-'+name).classList.remove('show');
  });
}

// ═══════════════════════════════════════════════════════════════════════
// Cover-time animation
// ═══════════════════════════════════════════════════════════════════════
function startCoverTime() {
  if (isRunning) return;
  isRunning = true; setBusy(true); clearAnim();
  buildAndDraw();

  const {N}=getParams();
  NAMES.forEach(name=>{
    const {adj}=graphs[name];
    const reach=adj.map((a,i)=>a.length>0?i:-1).filter(i=>i>=0);
    const start=reach[Math.floor(Math.random()*reach.length)];
    walkers[name]={current:start,visited:new Set([start]),steps:0,done:false,start,reach};
    document.getElementById('tk-'+name).classList.remove('show');
    drawNet(name,walkers[name]);
    document.getElementById('st-'+name).textContent='Step 0  ·  visited 1/'+reach.length;
  });

  const spt=parseInt(document.getElementById('inp-speed').value);

  if (spt>=99999) {
    NAMES.forEach(name=>{
      const {adj}=graphs[name]; const w=walkers[name];
      while(!w.done){
        const nb=adj[w.current]; w.current=nb[Math.floor(Math.random()*nb.length)];
        w.visited.add(w.current); w.steps++;
        if(w.visited.size>=w.reach.length) w.done=true;
      }
      drawNet(name,w);
      document.getElementById('tk-'+name).classList.add('show');
      document.getElementById('st-'+name).textContent='✓ Cover time: '+w.steps+' steps';
    });
    setStatusBar('Cover time done (instant).');
    isRunning=false; setBusy(false); return;
  }

  setStatusBar('Animating cover-time random walk…');
  animTmr=setInterval(()=>{
    let allDone=true;
    NAMES.forEach(name=>{
      const w=walkers[name]; if(w.done)return;
      const {adj}=graphs[name];
      for(let s=0;s<spt;s++){
        if(w.done)break;
        const nb=adj[w.current];
        w.current=nb[Math.floor(Math.random()*nb.length)];
        w.visited.add(w.current); w.steps++;
        if(w.visited.size>=w.reach.length){ w.done=true; break; }
      }
      drawNet(name,w);
      if(w.done){
        document.getElementById('tk-'+name).classList.add('show');
        document.getElementById('st-'+name).textContent='✓ Cover time: '+w.steps+' steps';
      } else {
        document.getElementById('st-'+name).textContent=
          'Step '+w.steps+'  ·  visited '+w.visited.size+'/'+w.reach.length;
      }
      allDone=allDone&&w.done;
    });
    const frac=NAMES.reduce((s,n)=>{const w=walkers[n]; return s+(w.visited.size/w.reach.length);},0)/3;
    setProgress(frac);
    if(allDone){ clearAnim(); setStatusBar('Cover time complete.'); isRunning=false; setBusy(false); }
  }, 50);
}

// ═══════════════════════════════════════════════════════════════════════
// Mixing time
// ═══════════════════════════════════════════════════════════════════════
function startMixingTime() {
  if (isRunning) return;
  isRunning=true; setBusy(true); clearAnim();
  buildAndDraw();

  setStatusBar('Computing mixing time (matrix iteration)…');
  setProgress(0);

  let done=0;
  NAMES.forEach((name,idx)=>{
    setTimeout(()=>{
      const {adj}=graphs[name];
      const {dist,iters}=mixingTime(adj);
      drawDist(name, dist, '~'+iters+' iters');
      done++;
      setProgress(done/3);
      if(done===3){
        setStatusBar('Mixing time done. Dashed line = uniform (1/N).');
        isRunning=false; setBusy(false);
      }
    }, idx*15);
  });
}

function mixingTime(adj) {
  const N=adj.length;
  const P=Array.from({length:N},()=>new Float64Array(N));
  for(let j=0;j<N;j++){
    const deg=adj[j].length;
    if(deg>0) for(const i of adj[j]) P[i][j]=1/deg; else P[j][j]=1;
  }
  let v=new Float64Array(N),s=0;
  for(let i=0;i<N;i++){v[i]=Math.random();s+=v[i];}
  for(let i=0;i<N;i++)v[i]/=s;
  const nxt=new Float64Array(N);
  let iters=5000;
  for(let it=0;it<5000;it++){
    nxt.fill(0);
    for(let i=0;i<N;i++) for(let j=0;j<N;j++) nxt[i]+=P[i][j]*v[j];
    let d=0; for(let i=0;i<N;i++){const x=Math.abs(v[i]-nxt[i]);if(x>d)d=x;}
    if(d<1e-5){iters=it;break;}
    v.set(nxt);
  }
  return {dist:v,iters};
}

// ═══════════════════════════════════════════════════════════════════════
// Reset
// ═══════════════════════════════════════════════════════════════════════
function doReset() {
  clearAnim();
  isRunning=false; setBusy(false); setProgress(0);
  buildAndDraw();
  NAMES.forEach(name=>{
    clearDist(name);
    document.getElementById('tk-'+name).classList.remove('show');
  });
  setStatusBar('Reset. Adjust β — the graph updates live. Then run a simulation.');
}

// ═══════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════
function clearAnim() {
  if(animTmr){clearInterval(animTmr);animTmr=null;}
}
function getParams() {
  const N=Math.max(10,Math.min(50,parseInt(document.getElementById('inp-N').value)||$N));
  let k=Math.max(2,Math.min(20,parseInt(document.getElementById('inp-k').value)||$k));
  if(k%2)k--;
  const beta=Math.pow(10,parseFloat(document.getElementById('inp-beta').value));
  return {N,k,beta};
}
function setBusy(b) {
  ['btn-cover','btn-mixing','btn-reset'].forEach(id=>{
    document.getElementById(id).disabled=b;
  });
}
function setStatusBar(msg){document.getElementById('statusbar').textContent=msg;}
function setProgress(p){document.getElementById('pgfill').style.width=(Math.min(1,p)*100)+'%';}

// ═══════════════════════════════════════════════════════════════════════
// Parameter change handlers
// ═══════════════════════════════════════════════════════════════════════
let debT=null;
document.getElementById('inp-beta').addEventListener('input',()=>{
  const beta=Math.pow(10,parseFloat(document.getElementById('inp-beta').value));
  document.getElementById('beta-badge').textContent=beta.toFixed(3);
  if(isRunning)return;
  clearTimeout(debT); debT=setTimeout(buildAndDraw,100);
});
['inp-N','inp-k'].forEach(id=>document.getElementById(id).addEventListener('change',()=>{
  if(isRunning)return;
  clearTimeout(debT); debT=setTimeout(buildAndDraw,80);
}));

// ═══════════════════════════════════════════════════════════════════════
// Button wiring
// ═══════════════════════════════════════════════════════════════════════
document.getElementById('btn-cover').addEventListener('click', startCoverTime);
document.getElementById('btn-mixing').addEventListener('click', startMixingTime);
document.getElementById('btn-reset').addEventListener('click', doReset);

// ═══════════════════════════════════════════════════════════════════════
// Initial render
// ═══════════════════════════════════════════════════════════════════════
buildAndDraw();
NAMES.forEach(name=>clearDist(name));
</script>
</body>
</html>
""")
