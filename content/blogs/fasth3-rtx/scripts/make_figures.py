"""Figures and the speed table for the FastH3 consumer-hardware post.

usage: python make_figures.py [img_dir results_root index_md]
With no arguments it uses the post bundle this script sits in: writes img/*.svg, reads results/*.json, and
rewrites the table between the results-table markers in index.md. Every figure is a light/dark SVG.
"""
import math
import sys

BUNDLE = __import__("pathlib").Path(__file__).resolve().parent.parent
OUT = sys.argv[1] if len(sys.argv) > 1 else str(BUNDLE / "img")
# Muted palette: slate, clay, warm gray, plus brick red for removed blocks. Validated for CVD and
# normal-vision separation in both modes; every segment is direct-labeled, so low chroma is safe.
STYLE = """<style>
  .bg{fill:#fcfcfb} .t1{fill:#0b0b0b} .t2{fill:#52514e} .grid{stroke:#e4e3de} .axis{stroke:#9b9a95}
  .s1{fill:#33557d} .s2{fill:#b86a3c} .s3{fill:#b5afa5} .drop{fill:#b0463c} .ref{stroke:#52514e}
  .gap{stroke:#fcfcfb} .on{fill:#ffffff} .on3{fill:#0b0b0b} .est{fill:none;stroke:#52514e}
  .ring{fill:none;stroke:#0b0b0b}
  text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
  @media (prefers-color-scheme: dark){
    .bg{fill:#1a1a19} .t1{fill:#ffffff} .t2{fill:#c3c2b7} .grid{stroke:#2e2e2c} .axis{stroke:#6b6a66}
    .s1{fill:#7393bb} .s2{fill:#c27448} .s3{fill:#69655e} .drop{fill:#c9605a} .ref{stroke:#c3c2b7}
    .gap{stroke:#1a1a19} .on{fill:#0b0b0b} .on3{fill:#ffffff} .est{fill:none;stroke:#c3c2b7}
    .ring{fill:none;stroke:#ffffff}
  }
</style>"""
FONT_W = 7.4  # approximate px per character at 13px, for legend spacing


def svg_open(W, H, title, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="t d">'
            f'<title id="t">{title}</title><desc id="d">{desc}</desc>', STYLE,
            f'<rect class="bg" width="{W}" height="{H}"/>']


def legend(out, items, x, y):
    for cls, name in items:
        out.append(f'<rect class="{cls}" x="{x}" y="{y-10}" width="12" height="12" rx="3"/>'
                   f'<text class="t2" x="{x+18}" y="{y}" font-size="13">{name}</text>')
        x += 18 + FONT_W * len(name) + 22
    return x


def memory_stack():
    rows = [("MiniMax H3 / FastH3 V2, BF16", [62.14, 65.29, 0.56 + 9.70], 137.7),
            ("FastH3 Trim, NVFP4 (this release)", [15.34, 11.10, 0.56 + 5.93], 33.0)]
    names = ["Text encoder", "Video+audio DiT", "VAEs"]
    W, left, right, top = 760, 24, 24, 78
    scale = (W - left - right - 70) / 140.0
    bar_h, row_gap = 34, 62
    H = top + len(rows) * row_gap + 40
    out = svg_open(W, H, "Checkpoint size by component",
                   "BF16 H3 is 137.7 GiB (text encoder 62.1, DiT 65.3, VAEs 10.3). The FastH3 Trim NVFP4 "
                   "release is 33.0 GiB (text encoder 15.3, DiT 11.1, VAEs 6.5), 4.2 times smaller.")
    legend(out, [(f"s{i+1}", n) for i, n in enumerate(names)], left, 32)
    for r, (label, vals, total) in enumerate(rows):
        y = top + r * row_gap
        out.append(f'<text class="t1" x="{left}" y="{y-8}" font-size="13.5" font-weight="600">{label}</text>')
        x = left
        for i, v in enumerate(vals):
            w = v * scale
            out.append(f'<rect class="s{i+1}" x="{x:.1f}" y="{y}" width="{max(w-2,1):.1f}" height="{bar_h}" rx="4"/>')
            if w > 26:
                out.append(f'<text class="{"on3" if i == 2 else "on"}" x="{x+(8 if w > 46 else 4):.1f}" y="{y+22}" '
                           f'font-size="{12.5 if w > 46 else 11}" font-weight="600">{v:.1f}</text>')
            x += w
        out.append(f'<text class="t1" x="{x+8:.1f}" y="{y+22}" font-size="14" font-weight="700">{total:.1f} GiB</text>')
    out.append(f'<text class="t2" x="{left}" y="{H-12}" font-size="12">Hugging Face checkpoint size per component, '
               f'GiB. VAEs = video + audio VAE.</text>')
    out.append("</svg>")
    open(f"{OUT}/fig_memory_stack.svg", "w").write("\n".join(out))


def amax():
    vals = [7808, 12224, 7168, 6496, 11648, 16000, 3552, 2816, 5024, 1728, 1624, 3024, 11008, 3072, 7200, 10240,
            4672, 10176, 8960, 21248, 16256, 13248, 18816, 12032, 15168, 18560, 13952, 15168, 37120, 15232, 30080,
            262144, 28160, 16320, 19712, 28160, 148480, 368640, 47872, 43776, 62464, 141312]
    W, H, l, r, t, b = 760, 350, 64, 24, 50, 50
    lo, hi = 3.0, 6.0  # log10 range 1e3..1e6
    pw, ph = W - l - r, H - t - b
    y = lambda v: t + ph * (1 - (math.log10(v) - lo) / (hi - lo))
    bw = pw / len(vals)
    out = svg_open(W, H, "Largest input to each block's MLP output projection",
                   "Across 1,000 calibration prompts and all 8 steps, 40 of 42 blocks see ff.fc_out inputs above "
                   "2,688, the largest magnitude an NVFP4 unit global scale can represent; block 37 reaches 368,640.")
    for e in range(3, 7):
        yy = y(10 ** e)
        out.append(f'<line class="grid" x1="{l}" x2="{W-r}" y1="{yy:.1f}" y2="{yy:.1f}" stroke-width="1"/>'
                   f'<text class="t2" x="{l-8}" y="{yy+4:.1f}" font-size="12" text-anchor="end">'
                   f'{["1K","10K","100K","1M"][e-3]}</text>')
    for i, v in enumerate(vals):
        x = l + i * bw + 1
        out.append(f'<rect class="s1" x="{x:.1f}" y="{y(v):.1f}" width="{bw-2:.1f}" height="{t+ph-y(v):.1f}" rx="2">'
                   f'<title>Block {i}: {v:,}</title></rect>')
    ry = y(2688)
    out.append(f'<line class="ref" x1="{l}" x2="{W-r}" y1="{ry:.1f}" y2="{ry:.1f}" stroke-width="1.5" '
               f'stroke-dasharray="5 4"/>'
               f'<line class="ref" x1="{l}" x2="{l+26}" y1="{t-14}" y2="{t-14}" stroke-width="1.5" stroke-dasharray="5 4"/>'
               f'<text class="t1" x="{l+32}" y="{t-10}" font-size="12.5" font-weight="600">2,688: the largest input '
               f'an uncalibrated (unit-scale) NVFP4 activation can represent</text>')
    mx = vals.index(max(vals))
    out.append(f'<text class="t1" x="{l + mx*bw + bw/2:.1f}" y="{y(max(vals))-6:.1f}" font-size="12.5" '
               f'text-anchor="middle" font-weight="600">368,640</text>')
    for i in range(0, len(vals), 5):
        out.append(f'<text class="t2" x="{l + i*bw + bw/2:.1f}" y="{t+ph+18}" font-size="11.5" text-anchor="middle">{i}</text>')
    out.append(f'<line class="axis" x1="{l}" x2="{W-r}" y1="{t+ph}" y2="{t+ph}" stroke-width="1"/>'
               f'<text class="t2" x="{l+pw/2:.1f}" y="{H-10}" font-size="12.5" text-anchor="middle">'
               f'Transformer block (FastH3 Trim, 42 blocks)</text>'
               f'<text class="t2" x="16" y="{t+ph/2:.1f}" font-size="12.5" text-anchor="middle" '
               f'transform="rotate(-90 16 {t+ph/2:.1f})">max |input|, log scale</text></svg>')
    open(f"{OUT}/fig_fc_out_amax.svg", "w").write("\n".join(out))


REMOVED = {6, 7, 9, 13, 15, 16, 22, 23}
MOST_SENSITIVE = {49, 0, 1, 5, 48, 47}  # largest worst-case bypass error in the block screen


def squares():
    """Transformer size per format as squares drawn to scale (area = GiB), tiled with its blocks."""
    stages = [  # label, GiB on disk
        ("H3, BF16", 65.3),
        ("Trim, BF16", 34.8),
        ("Trim, FP8", 19.9),
        ("Trim, INT6", 14.3),
        ("Trim, NVFP4", 11.1),
    ]
    W, left, S, arrow = 760, 24, 272, 40  # S is the side of the 65.3 GiB square
    kept = [i for i in range(50) if i not in REMOVED]
    side = [S * math.sqrt(g / stages[0][1]) for _, g in stages]
    y1 = 78 + S                                  # row 1 baseline: H3, pruned BF16, FP8
    y_link = y1 + 55                             # elbow from FP8 down to row 2
    y2 = y_link + 15 + side[3]                   # row 2 baseline: INT6, NVFP4
    H = y2 + 72
    out = svg_open(W, H, "FastH3 Trim transformer size by number format, drawn to scale",
                   "Squares whose area is the transformer checkpoint size. H3 BF16 65.3 GiB, 50 blocks with 8 "
                   "removed; Trim BF16 34.8 (1.9x smaller); FP8 19.9 (3.3x); INT6 14.3 (4.6x); NVFP4 11.1 (5.9x).")
    out.append(f'<text class="t1" x="{left}" y="26" font-size="15" font-weight="700">'
               f'Transformer size, drawn to scale: area is GiB</text>')
    x = legend(out, [("s1", "kept (42)"), ("drop", "removed (8)")], left, 54)
    out.append(f'<rect class="ring" x="{x}" y="44" width="12" height="12" rx="3" stroke-width="2"/>'
               f'<text class="t2" x="{x+18}" y="54" font-size="13">most sensitive</text>')

    def arrow_right(xa, xb, y):
        out.append(f'<line class="ref" x1="{xa:.1f}" x2="{xb-7:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke-width="1.5"/>'
                   f'<path class="t2" d="M{xb:.1f} {y:.1f} l-8 -4.5 v9 z"/>')

    def square(i, x0, base):
        label, gib = stages[i]
        s = side[i]
        y0 = base - s
        ids, cols, rows = (range(50), 10, 5) if i == 0 else (kept, 7, 6)
        tw, th = s / cols, s / rows
        g = 2 if s > 180 else 1.5
        font = min(12, tw * 0.42)
        out.append(f'<g><title>{label}: {gib} GiB</title>')
        for k, b in enumerate(ids):
            tx, ty = x0 + (k % cols) * tw, y0 + (k // cols) * th
            cls = "drop" if b in REMOVED else "s1"
            out.append(f'<rect class="{cls}" x="{tx+g/2:.1f}" y="{ty+g/2:.1f}" width="{tw-g:.1f}" '
                       f'height="{th-g:.1f}" rx="{min(4, tw/6):.1f}"/>')
            if font >= 7.5:
                out.append(f'<text class="on" x="{tx+tw/2:.1f}" y="{ty+th/2+font*0.36:.1f}" font-size="{font:.1f}" '
                           f'font-weight="600" text-anchor="middle">{b}</text>')
            if i == 0 and b in MOST_SENSITIVE:
                out.append(f'<rect class="ring" x="{tx+1:.1f}" y="{ty+1:.1f}" width="{tw-2:.1f}" '
                           f'height="{th-2:.1f}" rx="4" stroke-width="2"/>')
        out.append('</g>')
        ratio = "50 blocks" if i == 0 else f'{stages[0][1] / gib:.1f}× smaller'
        out.append(f'<text class="t1" x="{x0:.1f}" y="{base+20:.1f}" font-size="13" font-weight="600">{label}</text>'
                   f'<text class="t2" x="{x0:.1f}" y="{base+37:.1f}" font-size="12">'
                   f'{gib} GiB · {ratio}</text>')
        return x0 + s

    x = left
    centers = []
    for i, base in [(0, y1), (1, y1), (2, y1), (3, y2), (4, y2)]:
        if i in (0, 3):
            x = left
        else:
            arrow_right(x + 6, x + arrow - 6, base - min(side[i - 1], side[i]) / 2)
            x += arrow
        centers.append(x + side[i] / 2)
        x = square(i, x, base)
    # Elbow from the end of row 1 (FP8) to the start of row 2 (INT6).
    top3 = y2 - side[3]
    out.append(f'<path class="ref" fill="none" stroke-width="1.5" d="M{centers[2]:.1f} {y1+46:.1f} '
               f'V{y_link:.1f} H{centers[3]:.1f} V{top3-7:.1f}"/>'
               f'<path class="t2" d="M{centers[3]:.1f} {top3:.1f} l-4.5 -8 h9 z"/>')

    tx, ty = x + 34, y2 - side[3] + 34
    out.append(f'<text class="t1" x="{tx:.1f}" y="{ty:.1f}" font-size="30" font-weight="700">5.9× smaller</text>')
    for k, line in enumerate(["Drop 8 blocks,", "shrink the timestep path,", "store 4 bits."]):
        out.append(f'<text class="t2" x="{tx:.1f}" y="{ty+30+k*20:.1f}" font-size="14.5">{line}</text>')
    out.append(f'<text class="t2" x="{left}" y="{H-12}" font-size="11.5">Weights only, size on disk.</text></svg>')
    open(f"{OUT}/fig_squares.svg", "w").write("\n".join(out))


# One setting everywhere: 832x480, 124 frames (5 s), end to end. Values measured before the per-device agents
# pushed their results/*.json; any record there (frames == 124, width 832) overrides the matching cell.
DEVICES = [  # slug, label, memory, baseline values {model: seconds}
    ("gb200x4", "4× GB200", "data-center reference", {"trim": 4.3}),
    ("rtx-pro-6000", "RTX PRO 6000", "96 GB", {}),
    ("rtx5090", "RTX 5090", "32 GB", {"trim": 17.4}),
    ("rtx4090-24gb", "RTX 4090", "24 GB", {"trim": 41.8}),
    ("rtx4090-16gb", "RTX 4090, 16 GB limit", "16 GB", {}),
    ("rtx4090-12gb", "RTX 4090, 12 GB limit", "12 GB", {}),
    ("spark-1x", "DGX Spark", "128 GB unified", {"v2": 141.4, "trim": 134.5}),
    ("spark-2x", "2× DGX Spark", "128 GB each", {"v2": 87.2, "trim": 78.3}),
    ("m4max", "Mac, M4 Max", "36 GB unified", {}),
]


def load_results(root):
    """{(device, 'v2'|'trim'): median seconds} from results/*.json at 832x480, 124 frames."""
    import glob, json, os, statistics
    cells = {}
    for path in glob.glob(os.path.join(root, "results", "*.json")):
        by_cell = {}
        for r in json.load(open(path)):
            if r.get("frames") != 124 or r.get("width") != 832 or not r.get("e2e_median_s"):
                continue
            family = "v2" if str(r.get("model", "")).startswith("v2") else "trim"
            by_cell.setdefault((r["device"], family), []).append(float(r["e2e_median_s"]))
        for key, values in by_cell.items():
            cells[key] = statistics.median(values)
    return cells



def load_results_all(root):
    """{(device, family, width): median seconds} for 124-frame runs at 832x480 and 1344x768."""
    import glob, json, os, statistics
    cells = {}
    for path in glob.glob(os.path.join(root, "results", "*.json")):
        groups = {}
        for r in json.load(open(path)):
            if r.get("frames") != 124 or not r.get("e2e_median_s") or r.get("status", "ok") != "ok":
                continue
            family = "v2" if str(r.get("model", "")).startswith("v2") else "trim"
            groups.setdefault((r["device"], family, r["width"]), []).append(float(r["e2e_median_s"]))
        cells.update({k: statistics.median(v) for k, v in groups.items()})
    return cells


def results_table(root, index_path):
    """Rewrite the markdown table between the results-table markers in index.md."""
    cells = load_results_all(root)
    rows = ["| Machine | Memory | V2, 480p | Trim, 480p | V2, 768p | Trim, 768p |", "|---|---|---:|---:|---:|---:|"]
    for slug, label, mem, base in DEVICES:
        vals = []
        for family, width in (("v2", 832), ("trim", 832), ("v2", 1344), ("trim", 1344)):
            v = cells.get((slug, family, width), base.get(family) if width == 832 else None)
            vals.append(f"{v:.1f} s" if v else "—")
        rows.append(f"| {label} | {mem} | " + " | ".join(vals) + " |")
    text = open(index_path).read()
    start, end = "<!-- results-table:start -->", "<!-- results-table:end -->"
    a, b = text.index(start) + len(start), text.index(end)
    open(index_path, "w").write(text[:a] + "\n" + "\n".join(rows) + "\n" + text[b:])


def e2e(results_root=None):
    """Paired thin bars per device (FastH3 V2, FastH3 Trim) on a shared log axis; pending cells draw as outlines."""
    measured = load_results(results_root) if results_root else {}
    rows = []
    for slug, label, mem, base in DEVICES:
        rows.append((label, mem, {m: measured.get((slug, m), base.get(m)) for m in ("v2", "trim")}))
    W, left, right, label_w = 760, 24, 24, 214
    bar_h, pair_gap, row_gap = 9, 12, 34
    x0 = left + label_w
    pw = W - x0 - right - 70
    lo, hi = math.log10(2), math.log10(1000)
    xs = lambda v: x0 + pw * (math.log10(v) - lo) / (hi - lo)
    top = 70
    H = top + len(rows) * row_gap + 34
    desc = "; ".join(f"{label}: V2 {c['v2'] or 'pending'}, Trim {c['trim'] or 'pending'}" for label, _, c in rows)
    out = svg_open(W, H, "End-to-end seconds for a 5 s, 832x480 clip with audio", desc)
    legend(out, [("s1", "FastH3 V2"), ("s2", "FastH3 Trim")], left, 26)
    out.append(f'<line class="ref" x1="{left}" x2="{left+22}" y1="46" y2="46" stroke-width="1.5" stroke-dasharray="4 3"/>'
               f'<text class="t2" x="{left+28}" y="50" font-size="12.5">5 s: the clip plays in real time · log scale</text>')
    for tick in (2, 5, 10, 20, 50, 100, 200, 500, 1000):
        tx = xs(tick)
        out.append(f'<line class="grid" x1="{tx:.1f}" x2="{tx:.1f}" y1="{top-6}" y2="{top + len(rows) * row_gap - 8}" stroke-width="1"/>'
                   f'<text class="t2" x="{tx:.1f}" y="{top + len(rows) * row_gap + 8}" font-size="10.5" text-anchor="middle">{tick} s</text>')
    y = top
    for label, mem, cells in rows:
        out.append(f'<text class="t1" x="{left}" y="{y+11}" font-size="12.5" font-weight="600">{label}</text>'
                   f'<text class="t2" x="{left}" y="{y+25}" font-size="11">{mem}</text>')
        for k, (model, cls) in enumerate((("v2", "s1"), ("trim", "s2"))):
            yy = y + k * pair_gap
            v = cells[model]
            if v is None:
                out.append(f'<rect class="est" x="{x0}" y="{yy}" width="{pw*0.12:.1f}" height="{bar_h}" rx="3" stroke-width="1" '
                           f'stroke-dasharray="3 2"/><text class="t2" x="{x0+pw*0.12+5:.1f}" y="{yy+8.5}" font-size="10.5">pending</text>')
            else:
                w = xs(v) - x0
                out.append(f'<rect class="{cls}" x="{x0}" y="{yy}" width="{w:.1f}" height="{bar_h}" rx="2.5">'
                           f'<title>{label}, {"FastH3 V2" if model == "v2" else "FastH3 Trim"}: {v} s</title></rect>'
                           f'<text class="t1" x="{x0+w+5:.1f}" y="{yy+8.5}" font-size="11" font-weight="700">{v:.1f} s</text>')
        y += row_gap
    cx = xs(124 / 24)
    out.append(f'<line class="ref" x1="{cx:.1f}" x2="{cx:.1f}" y1="{top-8}" y2="{top + len(rows) * row_gap - 6}" '
               f'stroke-width="1.5" stroke-dasharray="4 3"/>')
    out.append("</svg>")
    open(f"{OUT}/fig_e2e.svg", "w").write("\n".join(out))


def stages():
    """Share of end-to-end time per stage, 100% stacked, with absolute totals."""
    rows = [  # label, sub, denoise, decode (video + audio), everything else, total
        ("RTX 4090", "Trim FP8, 480p, 5 s", 32.69, 6.63 + 0.08, 41.75),
        ("RTX 4090", "Trim FP8, 480p, 10 s", 63.51, 13.23 + 0.14, 79.67),
        ("4× GB200", "V1, 768p, 10 s", 5.7, 3.8 + 0.1, 15.5),
    ]
    names = ["Denoise", "Decode video and audio", "Text encode, frame export, MP4"]
    W, left, right, top = 760, 24, 24, 74
    bar_h, row_gap = 32, 66
    pw = W - left - right - 70
    H = top + len(rows) * row_gap + 18
    out = svg_open(W, H, "Where the end-to-end time goes",
                   "Share of end-to-end time. RTX 4090 5 s 480p, 41.8 s: denoise 78%, decode 16%, rest 6%. "
                   "RTX 4090 10 s 480p, 79.7 s: denoise 80%, decode 17%, rest 4%. 4x GB200 V1 768p 10 s, 15.5 s: "
                   "denoise 37%, decode 25%, rest 38%.")
    legend(out, [(f"s{i+1}", n) for i, n in enumerate(names)], left, 30)
    for r, (dev, sub, den, dec, total) in enumerate(rows):
        y = top + r * row_gap
        out.append(f'<text class="t1" x="{left}" y="{y-8}" font-size="13.5" font-weight="600">{dev}'
                   f'<tspan class="t2" font-weight="400" font-size="12.5">  {sub}</tspan></text>')
        x = left
        for i, v in enumerate([den, dec, total - den - dec]):
            w = v / total * pw
            out.append(f'<rect class="s{i+1}" x="{x:.1f}" y="{y}" width="{max(w-2,1):.1f}" height="{bar_h}" rx="4">'
                       f'<title>{names[i]}: {v:.1f} s ({v/total:.0%})</title></rect>')
            if w > 40:
                out.append(f'<text class="{"on3" if i == 2 else "on"}" x="{x+8:.1f}" y="{y+21}" font-size="12.5" '
                           f'font-weight="600">{v:.1f} s · {v/total:.0%}</text>' if w > 110 else
                           f'<text class="{"on3" if i == 2 else "on"}" x="{x+6:.1f}" y="{y+21}" font-size="12" '
                           f'font-weight="600">{v/total:.0%}</text>')
            x += w
        out.append(f'<text class="t1" x="{x+8:.1f}" y="{y+21}" font-size="14" font-weight="700">{total:.1f} s</text>')
    out.append("</svg>")
    open(f"{OUT}/fig_stages.svg", "w").write("\n".join(out))


memory_stack()
amax()
squares()
RESULTS = sys.argv[2] if len(sys.argv) > 2 else str(BUNDLE)
e2e(RESULTS)
results_table(RESULTS, sys.argv[3] if len(sys.argv) > 3 else str(BUNDLE / "index.md"))
stages()
print("ok")
