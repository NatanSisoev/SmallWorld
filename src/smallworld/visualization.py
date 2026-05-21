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
from pathlib import Path

import networkx as nx

from src.smallworld.plotting import _layout

__all__ = [
    "build_walk_visualization",
    "save_walk_visualization",
    "build_cover_time_visualization",
    "save_cover_time_visualization",
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
