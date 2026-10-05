# FastH3 consumer launch: instructions for device agents

> **FINAL (Oct 5, 20:00 UTC; gallery update 21:00): the gallery uses ONE prompt, `corgi-weather`, on every device.** Render corgi-weather first with both models at seed 1234 and push it right away; the other 3 showcase prompts are optional and only if time allows. Timing runs still come first if your device has no numbers yet.

The blog post is `content/blogs/fasth3-rtx/index.md` on branch `fasth3-rtx-blog` of
`aryan5v/hao-ai-lab.github.io` (PR hao-ai-lab/hao-ai-lab.github.io#108). Its story: **FastH3 V2 (8 steps, better than
base H3) now runs on one consumer machine**, and **FastH3 Trim** is an experimental pruned version that is smaller and
faster. You produce clips and times for your machines and push them to this branch. Do not edit `index.md`; the lead
session wires your files in.

## Who does what

| Agent | Devices (folder names) | Format |
|---|---|---|
| Lead | `gb200x4`, `rtx5090`, `rtx-pro-6000` | NVFP4 |
| Track B | `rtx4090-24gb`, `rtx4090-16gb`, `rtx4090-12gb` (stretch: `rtx4090-8gb`) | FP8 |
| Track C | `spark-1x`, `spark-2x`, `m4max` | NVFP4 (Spark), MLX INT6 (Mac) |

## Models

| Format | FastH3 V2 | FastH3 Trim |
|---|---|---|
| NVFP4 (5090, PRO 6000, Spark) | `FastVideo/FastVideo-FastH3-8-Step-V2-NVFP4-Consumer` | `FastVideo/FastVideo-FastH3-Trim-8-Step-NVFP4` |
| FP8 (4090 and its memory tiers) | `FastVideo/FastVideo-FastH3-8-Step-V2-FP8` | `FastVideo/FastVideo-FastH3-Trim-8-Step-FP8` |
| MLX INT6 (Mac) | `FastVideo/FastVideo-FastH3-8-Step-V2-MLX-INT6` | `FastVideo/FastVideo-FastH3-Trim-8-Step-MLX-INT6` |
| BF16 source | `FastVideo/FastVideo-FastH3-8-Step-V2` | `FastVideo/FastVideo-FastH3-Trim-8-Step` |

The Trim repos and V2 BF16 are public. V2 FP8 and V2 NVFP4-Consumer are uploading and become public after a test
generation; start with Trim and switch to V2 when its repo appears. Track C creates both MLX INT6 repos (below).

Code: RTX GPUs use the branch of hao-ai-lab/FastVideo#1919 (`aryan5v:fasth3-rtx`). Spark and Mac use the branch of
hao-ai-lab/FastVideo#1920 (`aryan5v:fasth3-spark-mlx`), which includes the GB10 NVFP4 fence that DGX Spark needs for
correct repeated runs.

Every repo ships the NVFP4 text encoder. On GPUs without FP4 (the 4090) it dequantizes per layer; use the
streamed encoder with fused dequantization (`FASTVIDEO_H3_ENCODER_LAYERWISE=1`, `FASTVIDEO_H3_ENCODER_FUSED_DEQUANT=1`).
MLX loads it natively. No other encoder is needed.

## Two jobs per device

### 1. Times (the numbers in the post)

- Prompts: `latency-ceramics-005` and `latency-harbor-005` from `fasth3-rtx-launch/benchmark_prompts.json`.
- Settings: **832x480 and 1344x768, both 124 frames (5 s)**, 24 fps, seed 1234, guidance 1.0, 8 DMD steps from
  `fastvideo_inference.json`, VSA sparsity 0.8, tile 64, lightweight VAE.
- Protocol: warm process, one untimed warmup, then each prompt twice. e2e = wall time of one generate call, from prompt
  to finished MP4 (text encoding + denoising + video and audio decoding + MP4 write). Report the median per prompt.
- Use your fastest verified recipe for the device and record every env var it sets.
- Both models, both resolutions. If a combination does not fit or fails, record it (peak memory and the error) and move on.

### 2. Showcase clips (the gallery)

- The 4 prompts in `fasth3-rtx-launch/showcase_prompts.json`: corgi-weather, street-food-jingle, parrot-pirate,
  grandma-dj. The post shows one clip per model per device, picked from these.
- 832x480, 124 frames, **seed 1234 only**, once with FastH3 V2 and once with FastH3 Trim: 8 clips per device.
- No extra seeds, no other prompts.

## Files (exact names)

```
content/blogs/fasth3-rtx/img/videos/<device>/<model>-<prompt>.mp4          seed 1234
content/blogs/fasth3-rtx/img/videos/<device>/<model>-<prompt>-s42.mp4      seed 42
content/blogs/fasth3-rtx/results/<device>.json
```

- `<model>`: `v2-nvfp4`, `trim-nvfp4`, `v2-fp8`, `trim-fp8`, `v2-int6`, `trim-int6`
- `<prompt>`: a showcase key (for example `fox-snow`); also save the benchmark clips as `ceramics` and `harbor`.
- Keep each MP4 under 8 MB (H.264 + AAC). Re-encoding does not change the recorded time:
  `ffmpeg -i in.mp4 -c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out.mp4`

`results/<device>.json` is a list with one record per (model, prompt, resolution) timing run:

```json
{"device": "rtx4090-16gb", "hardware": "RTX 4090", "memory_limit_gib": 16, "model": "trim-fp8",
 "repo": "FastVideo/FastVideo-FastH3-Trim-8-Step-FP8", "prompt": "ceramics", "width": 832, "height": 480,
 "frames": 124, "e2e_median_s": 0.0, "e2e_runs_s": [0.0, 0.0], "denoise_s": 0.0, "decode_s": 0.0,
 "peak_gpu_gib": 0.0, "peak_host_gib": 0.0, "fastvideo_commit": "<sha>", "env": {"FASTVIDEO_...": "1"},
 "status": "ok", "notes": ""}
```

Use `"status": "does_not_fit"` or `"failed"` with the error in `notes` when a run does not complete. The lead session
builds Figure 1 and the table directly from these files.

## Push

```bash
git clone --filter=blob:none --sparse -b fasth3-rtx-blog https://github.com/aryan5v/hao-ai-lab.github.io.git blog
cd blog && git sparse-checkout set content/blogs/fasth3-rtx fasth3-rtx-launch
# copy your clips into content/blogs/fasth3-rtx/img/videos/<device>/ and write results/<device>.json
git add content/blogs/fasth3-rtx/img/videos/<device> content/blogs/fasth3-rtx/results/<device>.json
git commit -m "[blog]: FastH3 V2 and Trim clips and times on <device>"
git pull --rebase origin fasth3-rtx-blog && git push origin HEAD:fasth3-rtx-blog
```

Push after each device or batch of clips, not only at the end. Touch only your own folders and results files. If the
push races another agent, run `git pull --rebase` and push again.

## Track C only: MLX INT6 repos

Convert both BF16 sources with `scripts/checkpoint_conversion/convert_minimax_h3_mlx.py` (pruned path from #1920) and
upload them as `FastVideo/FastVideo-FastH3-8-Step-V2-MLX-INT6` and `FastVideo/FastVideo-FastH3-Trim-8-Step-MLX-INT6`
(private; the lead makes them public). Include a short README: source repo, INT6 affine weights, NVFP4 text encoder,
lightweight VAE, 8-step schedule. On the Mac use the reference attention path, not the opt-in SIMD Metal kernel
(it gives wrong values on partially filled tiles). If everything does not fit in 36 GB at once, use phased placement
and record it.

## When you finish

Reply with a table of every run (device, model, resolution, e2e median, peak memory, status), the clips you pushed and
any repos you created.
