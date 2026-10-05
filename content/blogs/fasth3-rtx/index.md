+++
title = "FastH3 Trim: Video and Audio Generation on the RTX 5090, RTX 4090, DGX Spark and Mac"
date = 2026-10-05T00:00:00-07:00
url = "/blogs/fasth3-rtx/"
authors = ["FastVideo Team"]
author = "FastVideo Team"
ShowReadingTime = true
draft = true
contentClass = "fasth3-rtx-article"
[socialIcons]
    [[socialIcons.icon]]
      name = "twitter"
      url = "https://twitter.com/haoailab"
    [[socialIcons.icon]]
      name = "github"
      url = "https://github.com/hao-ai-lab/FastVideo"
[cover]
    image = "img/cover.png"
    alt = "FastH3 generating video with audio on an RTX 5090"
    caption = "FastH3 on consumer GPUs"
    hidden = true
+++

<div class="fasth3-rtx-todo"><b>TODO (cover + hero video).</b> One 10 s, 1344×768 clip with audio generated on a single RTX 5090, with the wall clock burned into the corner. Cover image is a still from it.</div>

{{< socialBadges github="hao-ai-lab/FastVideo" slack="https://join.slack.com/t/fastvideo/shared_invite/zt-3f4lao1uq-u~Ipx6Lt4J27AlD2y~IdLQ" huggingface="https://huggingface.co/collections/FastVideo/fastvideo-fasth3" >}}

## **TL;DR:**

- **One RTX 5090 generates a 5 s, 832×480 clip with synchronized audio in 17.4 s with FastH3 Trim.** A 10 s, 1344×768 clip takes 80.5 s. Four GB200s, our data-center baseline, take 4.3 s and 20.6 s. We measure each time from prompt submission to the finished MP4.
- **FastH3 Trim is a new model.** It keeps 42 of the 50 H3 transformer blocks, uses rank-16 timestep conditioning, and samples in 8 distilled steps. In NVFP4, its transformer is 11.1 GiB. The BF16 H3 transformer is 65.3 GiB.
- **The full model is 4.2× smaller.** FastH3 Trim with an NVFP4 text encoder and a lightweight VAE is 33.0 GiB. BF16 H3 is 137.7 GiB. This reduction lets one consumer GPU hold the model.
- **All FP4 layers use calibrated activation scales.** In 40 of 42 blocks, one MLP layer receives inputs larger than the maximum value of an uncalibrated FP4 activation. We measured the activation range of each layer over 1,000 prompts and all denoising steps. The checkpoint contains these scales.
- **The RTX 4090 and GPUs with less memory use FP8.** One RTX 4090 generates a 5 s, 480p clip in 41.8 s. With the allocator limited to 16 GB or 12 GB, a 10 s, 480p clip also completes.

This post continues [FastH3 Goes Local](/blogs/fasth3-local/), which identified the RTX family as the next CUDA target. FastH3 builds on [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3). We thank the MiniMax team for releasing its weights and code.

## Five models, one prompt

Each column is one model and format. Each row uses the same prompt and seed. All clips are 832×480, 5 s, with audio. Turn the audio on.

<div class="fasth3-rtx-scroll">
<div class="fasth3-rtx-grid fasth3-rtx-grid--models">
  <div></div>
  <div class="fasth3-rtx-colhead"><b>FastH3 V2</b><span>BF16 · 4× GB200</span></div>
  <div class="fasth3-rtx-colhead"><b>FastH3 V2</b><span>NVFP4 · RTX 5090</span></div>
  <div class="fasth3-rtx-colhead"><b>FastH3 Trim</b><span>NVFP4 · RTX 5090</span></div>
  <div class="fasth3-rtx-colhead"><b>FastH3 Trim</b><span>MLX INT6 · M4 Max</span></div>
  <div class="fasth3-rtx-colhead"><b>FastH3 Trim</b><span>FP8 · RTX 4090</span></div>
  <div class="fasth3-rtx-rowhead">Ceramics</div>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/ceramics-v2-bf16.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 V2, BF16 · 4× GB200, Ceramics">
        <source src="img/videos/models/ceramics-v2-bf16.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 V2</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/ceramics-v2-nvfp4.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 V2, NVFP4 · RTX 5090, Ceramics">
        <source src="img/videos/models/ceramics-v2-nvfp4.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 V2</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/ceramics-trim-nvfp4.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim, NVFP4 · RTX 5090, Ceramics">
        <source src="img/videos/models/ceramics-trim-nvfp4.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 Trim</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/ceramics-trim-int6.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim, MLX INT6 · M4 Max, Ceramics">
        <source src="img/videos/models/ceramics-trim-int6.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 Trim</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/ceramics-trim-fp8.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim, FP8 · RTX 4090, Ceramics">
        <source src="img/videos/models/ceramics-trim-fp8.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 Trim</b><span>— s</span></figcaption>
  </figure>
  <div class="fasth3-rtx-rowhead">Harbor</div>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/harbor-v2-bf16.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 V2, BF16 · 4× GB200, Harbor">
        <source src="img/videos/models/harbor-v2-bf16.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 V2</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/harbor-v2-nvfp4.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 V2, NVFP4 · RTX 5090, Harbor">
        <source src="img/videos/models/harbor-v2-nvfp4.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 V2</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/harbor-trim-nvfp4.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim, NVFP4 · RTX 5090, Harbor">
        <source src="img/videos/models/harbor-trim-nvfp4.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 Trim</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/harbor-trim-int6.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim, MLX INT6 · M4 Max, Harbor">
        <source src="img/videos/models/harbor-trim-int6.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 Trim</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/harbor-trim-fp8.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim, FP8 · RTX 4090, Harbor">
        <source src="img/videos/models/harbor-trim-fp8.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 Trim</b><span>— s</span></figcaption>
  </figure>
  <div class="fasth3-rtx-rowhead">Action</div>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/action-v2-bf16.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 V2, BF16 · 4× GB200, Action">
        <source src="img/videos/models/action-v2-bf16.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 V2</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/action-v2-nvfp4.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 V2, NVFP4 · RTX 5090, Action">
        <source src="img/videos/models/action-v2-nvfp4.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 V2</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/action-trim-nvfp4.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim, NVFP4 · RTX 5090, Action">
        <source src="img/videos/models/action-trim-nvfp4.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 Trim</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/action-trim-int6.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim, MLX INT6 · M4 Max, Action">
        <source src="img/videos/models/action-trim-int6.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 Trim</b><span>— s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="models/action-trim-fp8.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim, FP8 · RTX 4090, Action">
        <source src="img/videos/models/action-trim-fp8.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>FastH3 Trim</b><span>— s</span></figcaption>
  </figure>
</div>
</div>

<div class="fasth3-rtx-todo"><b>TODO (clips).</b> Fill <code>img/videos/models/&lt;prompt&gt;-&lt;model&gt;.mp4</code> for the prompts <code>latency-ceramics-005</code>, <code>latency-harbor-005</code> and one action prompt, with the shipping checkpoint. Replace each "— s" with that clip's end-to-end time.</div>

## The same clip on every machine

<div class="fasth3-rtx-grid fasth3-rtx-grid--devices">
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="devices/ceramics-gb200x4.mp4">
      <video controls playsinline preload="metadata" aria-label="4× GB200, ceramics">
        <source src="img/videos/devices/ceramics-gb200x4.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>4× GB200</b><span>baseline · NVFP4 · 4.3 s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="devices/ceramics-pro6000.mp4">
      <video controls playsinline preload="metadata" aria-label="RTX PRO 6000, ceramics">
        <source src="img/videos/devices/ceramics-pro6000.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>RTX PRO 6000</b><span>96 GB · NVFP4 · 15.1 s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="devices/ceramics-rtx5090.mp4">
      <video controls playsinline preload="metadata" aria-label="RTX 5090, ceramics">
        <source src="img/videos/devices/ceramics-rtx5090.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>RTX 5090</b><span>32 GB · NVFP4 · 17.4 s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="devices/ceramics-rtx4090.mp4">
      <video controls playsinline preload="metadata" aria-label="RTX 4090, ceramics">
        <source src="img/videos/devices/ceramics-rtx4090.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>RTX 4090</b><span>24 GB · FP8 · 41.8 s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="devices/ceramics-rtx4090-16gb.mp4">
      <video controls playsinline preload="metadata" aria-label="RTX 4090, 16 GB cap, ceramics">
        <source src="img/videos/devices/ceramics-rtx4090-16gb.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>RTX 4090, 16 GB cap</b><span>FP8 · 10 s clip · 104.0 s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="devices/ceramics-rtx4090-12gb.mp4">
      <video controls playsinline preload="metadata" aria-label="RTX 4090, 12 GB cap, ceramics">
        <source src="img/videos/devices/ceramics-rtx4090-12gb.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>RTX 4090, 12 GB cap</b><span>FP8 · 10 s clip · 107.3 s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="devices/ceramics-spark.mp4">
      <video controls playsinline preload="metadata" aria-label="DGX Spark, ceramics">
        <source src="img/videos/devices/ceramics-spark.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>DGX Spark</b><span>128 GB unified · NVFP4 · 134.5 s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="devices/ceramics-m4max.mp4">
      <video controls playsinline preload="metadata" aria-label="M4 Max, ceramics">
        <source src="img/videos/devices/ceramics-m4max.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>M4 Max</b><span>36 GB unified · MLX INT6 · pending</span></figcaption>
  </figure>
</div>

<div class="fasth3-rtx-todo"><b>TODO (clips).</b> Fill <code>img/videos/devices/ceramics-&lt;device&gt;.mp4</code> from the benchmark runs. The 4090 memory-cap clips are 10 s; all others are 5 s.</div>

## Benchmark results

All times in this post are **end-to-end** times. The measurement starts when the prompt is submitted. It stops when the MP4 file with video and audio is written. Each time includes:

- text encoding,
- all denoising steps,
- video and audio decoding,
- MP4 export.

The server is warm. One untimed generation completes compilation first. Then each of the two benchmark prompts runs two times, and we report the median of these four runs. No frames are dropped, and no preview decoder is used.

We use three clip settings, all at 24 fps: 832×480 for 5 s (124 frames) and 10 s (243 frames), and 1344×768 for 10 s (243 frames). Four GB200s are the data-center baseline. Every other row is a single machine.

{{< image src="img/fig_e2e.svg" alt="Thin horizontal bars of end-to-end seconds on a log scale, FastH3 Trim 8-step unless noted. 832×480, 5 s: 4× GB200 baseline 4.3, RTX PRO 6000 15.1, RTX 5090 17.4, RTX 4090 FP8 41.8, two DGX Sparks 78.3, one DGX Spark 134.5, M4 Max pending. 832×480, 10 s: RTX 4090 79.7, 4090 with a 16 GB cap 104.0, with a 12 GB cap 107.3, two Sparks 164.5, one Spark 277.3. 1344×768, 10 s: 4× GB200 20.6, RTX 5090 80.5, RTX PRO 6000 83.9, RTX 5090 FastH3 V2 90.1, RTX 4090 pending. A dashed line marks each clip's own length." width="100%" title="Figure 1. End-to-end time per clip, FastH3 Trim 8-step unless noted. The dashed line is the length of the clip itself." >}}

<div class="fasth3-rtx-todo"><b>TODO before publishing.</b> (1) 4090 at 768p, 10 s: the last verified run is 279.9 s, before the current kernels; re-measure. (2) RTX PRO 6000 rows use the MLP-only FP4 export; re-run with the full-FP4 export the 5090 uses. (4) Mac row from Track C.</div>

FastH3 Trim is the speed default. FastH3 V2 keeps all 50 blocks and is the quality reference; on a 5090 it takes 90.1 s for the 10 s, 768p clip, against 80.5 s for FastH3 Trim.

## Why H3 does not fit on one GPU

H3 contains three networks:

- A Qwen3-VL text encoder reads the prompt.
- A 50-block diffusion transformer (DiT) denoises the video and audio latents together.
- Two VAEs decode the latents into frames and sound.

In BF16, these weights are 137.7 GiB. A 32 GB RTX 5090 cannot hold the DiT alone. We reduced the size of each network separately.

{{< image src="img/fig_memory_stack.svg" alt="Stacked bars. BF16 H3: text encoder 62.1 GiB, DiT 65.3 GiB, VAEs 10.3 GiB, 137.7 GiB total. FastH3 Trim with full NVFP4: text encoder 15.3, DiT 11.1, VAEs 6.5, 33.0 GiB total." width="100%" title="Figure 2. Checkpoint size by component. The FastH3 Trim NVFP4 release is 4.2× smaller than BF16 H3." >}}

- **Text encoder: 62.1 → 15.3 GiB.** H3 reads hidden state 50 of a 64-layer Qwen3-VL and does not generate text. Thus we remove the last 14 layers and the language-model head. This removal does not change the features that H3 reads. We store the remaining linear layers in NVFP4.
- **DiT: 65.3 → 11.1 GiB.** Pruning removes 8 of the 50 blocks. In each block, a rank-16 factorization replaces the full-rank timestep projection. NVFP4 then stores all attention, MLP and sparse-attention gate weights in 4 bits.
- **VAE: 9.7 → 5.9 GiB.** We decode with the [LynnReal lightweight video VAE](https://huggingface.co/stdstu123/LynnReal-Onmi-light-vae), a distilled 26-block decoder with the same latent interface as the H3 VAE. We load it with [Kijai's INT8 weights](https://huggingface.co/Kijai/MiniMax-H3-experimental). In GPU memory, it uses 2.3 GiB.

The smaller size also gives most of the speed increase. On a 32 GB GPU, the important condition is whether the DiT stays in GPU memory between requests. If it does, each request moves only the text encoder into and out of GPU memory.

## FastH3 Trim

FastH3 Trim keeps 42 of the 50 H3 transformer blocks. It removes blocks 6, 7, 9, 13, 15, 16, 22 and 23.

{{< image src="img/fig_squares.svg" alt="Squares drawn to scale, area equal to transformer checkpoint size. H3 BF16, 65.3 GiB, is tiled with blocks 0 to 49; blocks 6, 7, 9, 13, 15, 16, 22 and 23 are red (removed), and blocks 0, 1, 5, 47, 48 and 49 are outlined as most sensitive. Arrows lead to smaller squares tiled with the same 42 kept blocks: Trim BF16 34.8 GiB (1.9× smaller), FP8 19.9 (3.3×), INT6 14.3 (4.6×), NVFP4 11.1 (5.9×)." width="100%" title="Figure 3. The transformer in each format we ship, drawn to scale: area is checkpoint size. Pruning removes eight blocks; the remaining 42 shrink as the bits per weight drop." >}}

### Choosing the blocks

Our first version compressed base H3 from 50 to 42 transformer blocks with activation-guided selection, which clearly beat removing blocks at uniform intervals. We reduced the AdaLN representation, recovered the pruned model with teacher guidance, and then used DMD to adapt it to fewer sampling steps. Quantization came last. We also tried quantization-aware distillation (QAD), but in our side-by-side comparisons the QAD variants were not better than post-training quantization. Motion coherence, fine detail and prompt adherence remained the main weaknesses.

For FastH3 Trim we changed how we select blocks. Starting from base H3, we skipped each block one at a time and measured how much the video and audio flow predictions changed. The screen used four examples (motion, speech, music and sound events) at three noise levels, which gives 600 block-removal measurements. We ranked the blocks by the largest change they caused in any of these conditions, so a block that matters for either video or audio is kept. This gave a different set of eight removed blocks from the activation-selected version.

### Training

We started a new 42-block student with the rank-16 AdaLN described below. We then trained it directly with eight-step DMD2, using the training objective of FastH3 V2: base H3 initializes both the frozen teacher and the trainable critic, and attention is 80% sparse. This tests whether distribution matching can repair the damage from pruning while it also adapts the model to fewer steps and sparse attention. We chose checkpoint 300 by eye; later checkpoints added objects and lost consistency within the clip. Quantization comes after checkpoint selection. QAD stays an option if post-training quantization leaves a visible quality gap.


H3 conditions each block on the diffusion timestep through an AdaLN projection. This projection maps a 2,688-dimensional time embedding to six modulation vectors. In BF16, these projections use 24 GiB across the 50 blocks. Their input is a smooth function of one scalar, the timestep. Thus the input uses very few of its 2,688 dimensions. FastH3 Trim replaces the projections with one shared 2,688→16 basis and a small projection per block. We store the factorized weights in FP16, because BF16 gives an approximately 1.7× larger reconstruction error.

The student model is distilled to 8 steps with DMD2. It samples at timesteps 999, 874, 749, 624, 500, 375, 250 and 125. Video Sparse Attention (VSA) keeps 20% of the attention tiles.

**Checkpoint selection requires visual review.** We compared checkpoints on 36 held-out prompts with a fixed seed. A later checkpoint gave sharper output overall. However, in a sword-fight prompt, it added a second dragon halfway through the clip. Our automatic scorer did not detect this defect. We now review each candidate checkpoint on the full prompt set by eye.

<div class="fasth3-rtx-todo"><b>TODO (quality figure).</b> Side-by-side frames: BF16 Trim vs NVFP4 Trim vs FastH3 V2 on three prompts. Frame grids for BF16 vs MLP-only NVFP4 vs full NVFP4 already exist from the 36-prompt evaluation.</div>

## Calibrated FP4 activation scales

NVFP4 stores each group of 16 values as 4-bit floating-point numbers with a shared 8-bit scale. A second, per-tensor scale sets the range. For weights, we calculate this second scale from the weights. For activations, we must set it before the data is available.

The simplest choice is a unit scale. A unit scale can represent magnitudes up to 6 × 448 = 2,688. H3 activations are much larger than this limit.

{{< image src="img/fig_fc_out_amax.svg" alt="Bar chart of the largest input to each block's MLP output projection across 42 blocks, on a log scale. 40 of 42 bars exceed the 2,688 line; block 37 reaches 368,640." width="100%" title="Figure 4. Largest input to each block's MLP output projection, over 1,000 calibration prompts and all eight steps. With a unit scale, everything above the dashed line saturates." >}}

The input to the MLP output projection is larger than 2,688 in 40 of 42 blocks. In block 37, it reaches 368,640, which is 137 times the limit. With a unit scale, these values are clipped on each forward pass.

Thus we calibrate the scales:

1. We ran 1,000 prompts through the full 8-step sampler.
2. For each linear layer, we recorded the largest input value.
3. We stored one static scale per layer in the checkpoint.

FastH3 Trim has 294 calibrated linear layers: attention projections, MLPs and the sparse-attention gate. The same procedure gives 350 scales for the 4-step V1 checkpoint. This procedure extends the FastH3 V2 NVFP4 recipe from the MLPs to all quantized layers.

<div class="fasth3-rtx-todo"><b>TODO (quality evidence).</b> Same-seed clips: BF16 vs NVFP4 (MLP only) vs NVFP4 (all layers) for FastH3 Trim and V1. The 36-prompt evaluation is done; pick three prompts with audio.</div>

## Fitting the DiT in a 32 GB RTX 5090

Our first FastH3 Trim FP4 export quantized only the MLPs, which is our setting for data-center GPUs. On a 5090, this export gave a 20 GB DiT, because the BF16 attention projections alone are 9.7 GB. The text encoder did not fit in GPU memory together with this DiT. Thus each request moved the DiT to host memory and back. A 480p clip took 26.4 s, and a 768p clip did not fit.

With attention and the gate also in NVFP4, the DiT is 11.1 GiB. The DiT now stays in GPU memory, and only the 15.3 GiB text encoder is loaded for each prompt. The same 480p clip takes 17.4 s. A 10 s, 768p generation also fits, and it takes 80.5 s. This time is shorter than the 90.1 s of the larger FastH3 V2 on the same GPU.

**Pinned host memory can have a large overhead.** Fast transfers between host and GPU require page-locked ("pinned") host memory. The PyTorch pinned-memory allocator rounds each block up to a power of two. For the H3 FP4 weight shapes, 2.87 GiB of tensors used 5.06 GiB of host RAM. In a 60 GB cloud container, this overhead caused the operating system to stop the process. We now pin one buffer of the exact size per module with `cudaHostRegister`, and we place the tensors in that buffer. The same 2.87 GiB of tensors now uses 2.90 GiB.

## RTX 4090 and GPUs with less memory

The RTX 4090 does not have FP4 tensor cores. Thus it uses FP8: 8-bit weights with one scale per output channel, and 8-bit activations with one scale per token.

**The default FP8 path is slower than BF16 on this GPU.** On a 4090, the PyTorch FP8 matrix multiply with per-token and per-channel scales runs at approximately 70 TFLOPS. BF16 runs at approximately 160 TFLOPS, and the per-tensor FP8 kernel runs at 220–305 TFLOPS. We use the per-tensor kernel with unit scales. Then one fused pass applies both scale vectors to the output. The result is the same as per-token, per-channel scaling, at a cost of 5–10% more than per-tensor scaling.

Every GPU decodes with the same lightweight VAE and the same INT8 weights. On the 4090 we only made its INT8 matrix multiplies faster: one fused pass dequantizes the output, and the Q, K and V projections share one quantized input. The decoded frames are identical to the unoptimized path.

<div class="fasth3-rtx-todo"><b>TODO (4090 write-up, from PR #46).</b> INT8 QK / BF16 PV sparse attention on sm89, and layer-by-layer streaming of the NVFP4 text encoder with fused dequantization. The 4090 time split is in Figure 5.</div>

| RTX 4090, FastH3 Trim, FP8 | 832×480, 124 frames | 832×480, 243 frames |
|---|---:|---:|
| 24 GB (full GPU) | 41.8 s | 79.7 s |
| Limited to 16 GB | — | 104.0 s |
| Limited to 12 GB | — | 107.3 s |

For the 16 GB and 12 GB rows, we limit the PyTorch allocator on the same 4090. These rows show that the model fits in that amount of GPU memory. A real 16 GB GPU is slower.

<div class="fasth3-rtx-todo"><b>TODO.</b> 8 GB attempt, minimum system RAM per tier, RTX 30-series (FP8 weights with BF16 compute).</div>

## DGX Spark and Apple Silicon

On a DGX Spark, the text encoder, the DiT and both VAEs stay in the 128 GB of unified memory. Nothing moves between requests. We use the same NVFP4 checkpoints and the light VAE as on the RTX 5090. Two Sparks split each request with sequence parallelism.

| DGX Spark, 832×480 | 124 frames (5 s) | 243 frames (10 s) |
|---|---:|---:|
| 1× Spark, FastH3 Trim 8-step | 134.5 s | 277.3 s |
| 1× Spark, FastH3 V2 8-step | 141.4 s | 307.2 s |
| 2× Spark, FastH3 Trim 8-step | 78.3 s | 164.5 s |
| 2× Spark, FastH3 V2 8-step | 87.2 s | 180.0 s |

Each value is the average of the two benchmark prompts. Each prompt's value is the median of two timed runs after one warmup. Repeated runs of a prompt give identical frames.

In [FastH3 Goes Local](/blogs/fasth3-local/), a 124-frame clip took 243 s on one Spark and 209 s on two. Those runs used the 4-step preview and the full H3 VAE. The new 8-step models do twice as many denoising steps and are still faster: 134.5 s on one Spark and 78.3 s on two.

<div class="fasth3-rtx-todo"><b>TODO (Mac, Track C, PR #47).</b> FastH3 Trim in MLX INT6 on the M4 Max (36 GB), light VAE, NVFP4 encoder. INT6 medians at 124 and 243 frames are still running. Compare against FastH3 Goes Local (M4 Max INT6, 456 s at 124 frames, four-step preview, full VAE) and state those differences beside any ratio.</div>

## Where the time goes

{{< image src="img/fig_stages.svg" alt="100% stacked bars. RTX 4090 FastH3 Trim FP8 480p 5 s, 41.8 s: denoise 78%, decode 16%, rest 6%. RTX 4090 480p 10 s, 79.7 s: denoise 80%, decode 17%, rest 4%. 4× GB200 V1 768p 10 s, 15.5 s: denoise 37%, decode 25%, rest 38%." width="100%" title="Figure 5. Share of end-to-end time per stage." >}}

<div class="fasth3-rtx-todo"><b>TODO.</b> Add a 5090 row from the run logs.</div>

On one 4090, denoising is approximately 80% of the end-to-end time. When the model fits in GPU memory, the other stages become a larger part of the total. On four GB200 GPUs, V1 uses 9.8 s of compute for a 10 s, 768p clip:

- 5.7 s for denoising,
- 3.8 s for decoding, distributed across the four GPUs,
- the remaining time for text encoding.

The transfer of frames out of the GPU workers and the MP4 write take another 5.7 s. This is the next stage that we will optimize.

## Get the models

<div class="fasth3-rtx-todo"><b>TODO before publishing.</b> Make the Trim repos public under these names and link each to its Cookbook recipe.</div>

| Hardware | Model | Hugging Face |
|---|---|---|
| RTX 5090, RTX PRO 6000, DGX Spark (Blackwell) | FastH3 Trim, 8-step, NVFP4 | [`FastVideo/FastVideo-FastH3-Trim-8-Step-NVFP4`](https://huggingface.co/FastVideo/FastVideo-FastH3-Trim-8-Step-NVFP4) |
| RTX 4090, 16 GB and 12 GB GPUs | FastH3 Trim, 8-step, FP8 | [`FastVideo/FastVideo-FastH3-Trim-8-Step-FP8`](https://huggingface.co/FastVideo/FastVideo-FastH3-Trim-8-Step-FP8) |
| Apple Silicon, MLX | FastH3 Trim, 8-step, INT6 | [`FastVideo/FastVideo-FastH3-Trim-8-Step-MLX-INT6`](https://huggingface.co/FastVideo/FastVideo-FastH3-Trim-8-Step-MLX-INT6) |
| Source weights | FastH3 Trim, 8-step, BF16 | [`FastVideo/FastVideo-FastH3-Trim-8-Step`](https://huggingface.co/FastVideo/FastVideo-FastH3-Trim-8-Step) |
| Full quality, Blackwell GPUs | FastH3 V2, 8-step, NVFP4 | [`FastVideo/FastVideo-FastH3-8-Step-V2-NVFP4`](https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2-NVFP4) |
| Full quality, data-center GPUs | FastH3 V2, 8-step, BF16 | [`FastVideo/FastVideo-FastH3-8-Step-V2`](https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2) |

Each repository contains the NVFP4 text encoder, the lightweight VAE and a `fastvideo_inference.json` file. This file contains the sampling schedule. FastVideo reads it and uses the correct steps automatically.

Example for one RTX 5090:

```python
from fastvideo import VideoGenerator

generator = VideoGenerator.from_config({
    "model_path": "FastVideo/FastVideo-FastH3-Trim-8-Step-NVFP4",
    "engine": {
        "num_gpus": 1,
        "quantization": {"transformer_quant": "NVFP4", "layer_profile": "h3_dit_vsa"},
        "offload": {"text_encoder": True, "pin_cpu_memory": True},
    },
    "pipeline": {"experimental": {"attention_backend": "VIDEO_SPARSE_ATTN_H3", "h3_sequential_load": True}},
})
generator.generate_video(
    prompt="A potter smooths the rim of a spinning bowl as an apprentice watches.",
    height=480, width=832, num_frames=124, guidance_scale=1.0, output_path="out.mp4",
)
```

<div class="fasth3-rtx-todo"><b>TODO.</b> Replace the environment-variable switches used in our benchmarks (FP4 sparse attention, fusions, VAE parking) with Cookbook recipes and one-line CLI commands for the 5090, 4090 and 16 GB tiers.</div>

## Limitations

- **Pruning decreases quality to increase speed.** FastH3 Trim keeps 42 of 50 blocks. FastH3 V2 is the quality reference.
- **FP4 attention is new.** Calibrated scales cover all quantized layers. We reviewed 36 prompts by eye. We did not do a large human study.
- **Not tested yet:** RTX 30-series GPUs, real 16 GB and 12 GB GPUs (our results limit memory on a 4090), and 10 s, 768p clips with less than 24 GB.

## Acknowledgements

FastVideo FastH3 builds on [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3). We thank the MiniMax team for releasing its weights and code.

The lightweight decoder is the [LynnReal Lightweight Video VAE](https://huggingface.co/stdstu123/LynnReal-Onmi-light-vae) ([paper](https://arxiv.org/abs/2609.15863), [code](https://github.com/LynnReal-AI/LynnReal-Omni)). We load it with the INT8 weights from [Kijai](https://huggingface.co/Kijai)'s [MiniMax-H3-experimental](https://huggingface.co/Kijai/MiniMax-H3-experimental). We thank both.

We thank the NVIDIA Enterprise Products team (Pengcheng Li and Cliff Woolley) for the Video Sparse Attention kernel. We also thank the FlashInfer and NVIDIA Model Optimizer teams for the FP4 kernels and calibration tools. The FP4 sparse attention on RTX GPUs builds on [SageAttention](https://github.com/thu-ml/SageAttention). Ollin Boer Bohan's [TAEH3](https://github.com/madebyollin/taehv) is the fast preview decoder.

The FastVideo Team collaborated closely with [Nuva Lab](https://nuvalab.ai/), [NVIDIA FastGen](https://github.com/NVlabs/FastGen) (Julius Berner, Chao Liu, Arash Vahdat) and the NVIDIA Enterprise Products team on [FastH3](/blogs/fasth3-preview/). We also thank the [vLLM project](https://vllm.ai/), [NVIDIA](https://www.nvidia.com/en-us/) and [MBZUAI](https://mbzuai.ac.ae/) for their continued sponsorship and support of FastVideo.

## FastVideo team

**Contributor:** [Aryan Kumar](https://github.com/aryan5v)
<a href="https://github.com/aryan5v" aria-label="Aryan Kumar GitHub"><i class="fab fa-github"></i></a>
<a href="https://www.linkedin.com/in/aryan-kumar01" aria-label="Aryan Kumar LinkedIn"><i class="fab fa-linkedin"></i></a>
<a href="https://x.com/aryan_xv" aria-label="Aryan Kumar X"><i class="fab fa-x-twitter"></i></a>  
**Tech lead:** [Will Lin](https://github.com/SolitaryThinker)
<a href="https://github.com/SolitaryThinker" aria-label="Will Lin GitHub"><i class="fab fa-github"></i></a>
<a href="https://www.linkedin.com/in/will-lin-294920100" aria-label="Will Lin LinkedIn"><i class="fab fa-linkedin"></i></a>
<a href="https://x.com/wlsaidhi" aria-label="Will Lin X"><i class="fab fa-x-twitter"></i></a>  
**Advisor:** [Hao Zhang](https://github.com/zhisbug)
<a href="https://github.com/zhisbug" aria-label="Hao Zhang GitHub"><i class="fab fa-github"></i></a>
<a href="https://www.linkedin.com/in/haozhangml" aria-label="Hao Zhang LinkedIn"><i class="fab fa-linkedin"></i></a>
<a href="https://x.com/haozhangml" aria-label="Hao Zhang X"><i class="fab fa-x-twitter"></i></a>

<style>
.fasth3-rtx-article .fasth3-rtx-scroll {
  width: 100%;
  overflow-x: auto;
}

.fasth3-rtx-article .fasth3-rtx-grid {
  display: grid;
  margin: 1.4rem 0 1.8rem;
  gap: 0.9rem 0.55rem;
  align-items: start;
}

.fasth3-rtx-article .fasth3-rtx-grid--models {
  min-width: 720px;
  grid-template-columns: 4.6rem repeat(5, minmax(0, 1fr));
}

.fasth3-rtx-article .fasth3-rtx-grid--devices {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.fasth3-rtx-article .fasth3-rtx-colhead,
.fasth3-rtx-article .fasth3-rtx-rowhead {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.8rem;
  line-height: 1.3;
}

.fasth3-rtx-article .fasth3-rtx-colhead span {
  color: var(--secondary);
}

.fasth3-rtx-article .fasth3-rtx-rowhead {
  align-self: center;
  font-weight: 600;
}

.fasth3-rtx-article .fasth3-rtx-clip {
  min-width: 0;
  margin: 0;
}

.fasth3-rtx-article .fasth3-rtx-frame {
  position: relative;
  aspect-ratio: 832 / 480;
  border: 1.5px dashed var(--border);
  border-radius: 8px;
}

.fasth3-rtx-article .fasth3-rtx-frame::before {
  content: "pending · " attr(data-file);
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 0.4rem;
  color: var(--secondary);
  font-size: 0.68rem;
  text-align: center;
}

.fasth3-rtx-article .fasth3-rtx-frame video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  background: transparent;
}

.fasth3-rtx-article .fasth3-rtx-clip > figcaption {
  display: flex;
  flex-wrap: wrap;
  gap: 0.2rem 0.45rem;
  margin: 0.4rem 0 0;
  font-size: 0.78rem;
  line-height: 1.3;
}

.fasth3-rtx-article .fasth3-rtx-clip > figcaption span {
  color: var(--secondary);
}

@media (max-width: 760px) {
  .fasth3-rtx-article .fasth3-rtx-grid--devices {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.fasth3-rtx-article .fasth3-rtx-todo {
  margin: 1.4rem 0;
  padding: 0.85rem 1rem;
  border: 1.5px dashed #eb6834;
  border-radius: 10px;
  background: rgba(235, 104, 52, 0.07);
  font-size: 0.9rem;
  line-height: 1.5;
}

.fasth3-rtx-article .fasth3-rtx-todo ul {
  margin: 0.5rem 0 0;
  padding-left: 1.2rem;
}

.fasth3-rtx-article .fasth3-rtx-pending {
  color: #eb6834;
  font-weight: 600;
}

.fasth3-rtx-article .fasth3-rtx-table table {
  width: 100%;
  font-size: 0.92rem;
}

.fasth3-rtx-article .fasth3-rtx-table td:nth-child(4),
.fasth3-rtx-article .fasth3-rtx-table td:nth-child(5) {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

@media (max-width: 760px) {
  .fasth3-rtx-article .fasth3-rtx-table {
    overflow-x: auto;
  }
}
</style>
