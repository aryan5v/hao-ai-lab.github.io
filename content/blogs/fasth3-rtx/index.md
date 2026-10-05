+++
title = "FastH3 Trim: Video and Audio Generation on One Consumer GPU"
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
    image = "img/cover.jpg"
    alt = "Blueprint drawings of a DGX Spark, a Mac Studio, an RTX 4090 and an RTX 5090"
    caption = "FastH3 Trim"
    hidden = true
+++

{{< image src="img/cover.jpg" alt="Blueprint drawings of a DGX Spark, a Mac Studio, an RTX 4090 and an RTX 5090" width="100%" >}}

{{< socialBadges github="hao-ai-lab/FastVideo" slack="https://join.slack.com/t/fastvideo/shared_invite/zt-3f4lao1uq-u~Ipx6Lt4J27AlD2y~IdLQ" huggingface="https://huggingface.co/collections/FastVideo/fastvideo-fasth3" >}}

FastH3 V2 generates video with synchronized audio in eight steps, but its weights take 138 GiB, more than four times the memory of the largest consumer GPU. This post continues [FastH3 Goes Local](/blogs/fasth3-local/), which brought FastH3 to the DGX Spark and the Mac and named the RTX family as the next target. Today we release **FastH3 Trim**, a smaller version of FastH3 that runs on one RTX 5090, one RTX 4090, a DGX Spark or a Mac. It removes 8 of the 50 transformer blocks, compresses the timestep conditioning, and stores the remaining weights in 4 or 8 bits.

FastH3 Trim is our first step toward smaller FastH3 models. Removing blocks makes the model faster and smaller, but it also costs some quality, and we explain that trade-off below.

## TL;DR

- **One RTX 5090 generates a 5 s, 832×480 clip with audio in 17.4 s**, and a 10 s, 1344×768 clip in 80.5 s. Each time runs from prompt submission to the finished MP4.
- **The release is 4.2× smaller than H3.** With the NVFP4 transformer and text encoder and a lightweight VAE, FastH3 Trim is 33.0 GiB, against 137.7 GiB for BF16 H3.
- **The same model runs across consumer hardware.** NVFP4 on Blackwell GPUs and DGX Spark, FP8 on the RTX 4090 and on GPUs with 16 GB or 12 GB of memory, and INT6 on Apple Silicon.
- **Pruning trades some quality for size and speed.** FastH3 V2 remains the quality reference. FastH3 Trim is the fast option, and we plan to improve it and to make it smaller.

## See it run

<figure class="fasth3-rtx-clip fasth3-rtx-hero">
  <div class="fasth3-rtx-frame fasth3-rtx-frame--wide" data-file="hero-rtx5090.mp4">
    <video controls playsinline preload="metadata" aria-label="FastH3 Trim on one RTX 5090, 10 s at 1344×768 with audio">
      <source src="img/videos/hero-rtx5090.mp4" type="video/mp4">
    </video>
  </div>
  <figcaption><b>One RTX 5090</b><span>FastH3 Trim, NVFP4 · 1344×768, 10 s, with audio · — s from prompt to MP4</span></figcaption>
</figure>

<div class="fasth3-rtx-grid">
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="ceramics-rtx5090.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim on one RTX 5090, ceramics">
        <source src="img/videos/ceramics-rtx5090.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>Ceramics</b><span>RTX 5090 · 832×480, 5 s · — s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="harbor-rtx5090.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim on one RTX 5090, harbor">
        <source src="img/videos/harbor-rtx5090.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>Harbor</b><span>RTX 5090 · 832×480, 5 s · — s</span></figcaption>
  </figure>
  <figure class="fasth3-rtx-clip">
    <div class="fasth3-rtx-frame" data-file="action-rtx5090.mp4">
      <video controls playsinline preload="metadata" aria-label="FastH3 Trim on one RTX 5090, action">
        <source src="img/videos/action-rtx5090.mp4" type="video/mp4">
      </video>
    </div>
    <figcaption><b>Action</b><span>RTX 5090 · 832×480, 5 s · — s</span></figcaption>
  </figure>
</div>

<div class="fasth3-rtx-todo"><b>TODO (clips).</b> Add <code>img/videos/hero-rtx5090.mp4</code> (10 s, 1344×768) and the three 5 s clips <code>ceramics-</code>, <code>harbor-</code> and <code>action-rtx5090.mp4</code> (prompts <code>latency-ceramics-005</code>, <code>latency-harbor-005</code> and one action prompt). Replace each "— s" with the clip's end-to-end time. Turn the audio on.</div>

## How fast is it

All times in this post are end to end. Each one starts when we submit the prompt and stops when the MP4 file with video and audio is written, so it includes text encoding, all eight denoising steps, video and audio decoding, and the MP4 export. The server is warm: one untimed request compiles the model first. We then run each of two benchmark prompts twice and report the median.

{{< image src="img/fig_e2e.svg" alt="Thin horizontal bars of end-to-end seconds on a log scale, FastH3 Trim unless noted. 832×480, 5 s: 4× GB200 baseline 4.3, RTX PRO 6000 15.1, RTX 5090 17.4, RTX 4090 FP8 41.8, two DGX Sparks 78.3, one DGX Spark 134.5, M4 Max pending. 832×480, 10 s: RTX 4090 79.7, 4090 with a 16 GB cap 104.0, with a 12 GB cap 107.3, two Sparks 164.5, one Spark 277.3. 1344×768, 10 s: 4× GB200 20.6, RTX 5090 80.5, RTX PRO 6000 83.9, RTX 5090 FastH3 V2 90.1, RTX 4090 pending. A dashed line marks each clip's own length." width="100%" title="Figure 1. End-to-end time per clip, FastH3 Trim unless noted. Four GB200s are the data-center baseline; every other row is one machine. The dashed line is the length of the clip itself." >}}

On a 5090, FastH3 Trim generates the 10 s, 768p clip in 80.5 s. The full FastH3 V2 takes 90.1 s on the same GPU. Most of the speed on consumer GPUs comes from the model being small enough to stay in GPU memory, which the next section explains.

<div class="fasth3-rtx-todo"><b>TODO (numbers).</b> Re-measure the RTX 4090 at 1344×768, 10 s (the last run, 279.9 s, predates the current kernels). Re-run the RTX PRO 6000 with the all-layer NVFP4 export. Add the M4 Max INT6 row.</div>

## Making H3 small enough for one GPU

H3 is three networks. A Qwen3-VL text encoder reads the prompt, a 50-block diffusion transformer (DiT) denoises the video and audio latents together, and two VAEs decode the latents into frames and sound. In BF16 these weights total 137.7 GiB, and a 32 GB RTX 5090 cannot hold even the DiT. We reduced each network separately.

{{< image src="img/fig_memory_stack.svg" alt="Stacked bars. BF16 H3: text encoder 62.1 GiB, DiT 65.3 GiB, VAEs 10.3 GiB, 137.7 GiB total. FastH3 Trim with NVFP4: text encoder 15.3, DiT 11.1, VAEs 6.5, 33.0 GiB total." width="100%" title="Figure 2. Checkpoint size by component. The FastH3 Trim NVFP4 release is 4.2× smaller than BF16 H3." >}}

- **Text encoder: 62.1 → 15.3 GiB.** H3 reads hidden state 50 of a 64-layer Qwen3-VL and never generates text, so we remove the last 14 layers and the language-model head without changing the features H3 uses. The remaining linear layers are stored in NVFP4.
- **DiT: 65.3 → 11.1 GiB.** We remove 8 of the 50 blocks, replace each block's timestep projection with a rank-16 factorization, and store the attention, MLP and sparse-attention gate weights in NVFP4.
- **VAEs: 10.3 → 6.5 GiB.** We decode video with the [LynnReal lightweight video VAE](https://huggingface.co/stdstu123/LynnReal-Onmi-light-vae), a distilled 26-block decoder with the same latent interface as the H3 VAE, loaded with [Kijai's INT8 weights](https://huggingface.co/Kijai/MiniMax-H3-experimental). It uses 2.3 GiB of GPU memory, and every device in this post uses the same one.

Size matters for speed. On a 32 GB GPU, the question is whether the DiT can stay in GPU memory between requests. When it can, each request only moves the text encoder in and out.

## FastH3 Trim: removing blocks

Pruning is an experiment we plan to refine over time, and it is our path to even smaller models. It is also not free. We remove the blocks we measured as least important, but each block still holds part of what the model learned, so the pruned model loses some information and quality can drop. In return it gets both faster and smaller. FastH3 Trim is the first step, and more will follow.

{{< image src="img/fig_squares.svg" alt="Squares drawn to scale, area equal to transformer checkpoint size. H3 BF16, 65.3 GiB, is tiled with blocks 0 to 49; blocks 6, 7, 9, 13, 15, 16, 22 and 23 are red (removed), and blocks 0, 1, 5, 47, 48 and 49 are outlined as most sensitive. Arrows lead to smaller squares tiled with the same 42 kept blocks: Trim BF16 34.8 GiB (1.9× smaller), FP8 19.9 (3.3×), INT6 14.3 (4.6×), NVFP4 11.1 (5.9×)." width="100%" title="Figure 3. The transformer in each format we ship, drawn to scale: area is checkpoint size. FastH3 Trim removes blocks 6, 7, 9, 13, 15, 16, 22 and 23; the remaining 42 shrink as the bits per weight drop." >}}

### Choosing the blocks

Our first pruned model chose blocks by their activations, which clearly beat removing blocks at even intervals. We recovered that model with teacher guidance and then used DMD to reduce its sampling steps. Motion coherence, fine detail and prompt adherence stayed weak. Quantization-aware distillation (QAD) did not beat post-training quantization in our side-by-side comparisons.

For FastH3 Trim we measured each block directly. Starting from base H3, we skipped one block at a time and recorded how much the video and audio predictions changed. We tested four examples (motion, speech, music and sound events) at three noise levels, for 600 measurements in total. Each block was ranked by the largest change it caused under any condition, so a block that matters to either video or audio is kept. The first and last blocks changed the output the most. The eight blocks we removed are all in the first half of the network.

### Compressing the timestep conditioning

H3 conditions each block on the diffusion timestep through an AdaLN projection, which maps a 2,688-dimensional time embedding to six modulation vectors. These projections take 24 GiB in BF16 across the 50 blocks. Their input, however, is a smooth function of a single number, the timestep, so it uses very few of its 2,688 dimensions. FastH3 Trim replaces the projections with one shared 2,688→16 basis and a small projection per block. We store the factorized weights in FP16, because BF16 gives about 1.7× larger reconstruction error.

### Training

We trained the new 42-block model directly with eight-step DMD2, using the FastH3 V2 objective. Base H3 initializes both the frozen teacher and the trainable critic, and attention is 80% sparse. The model samples at timesteps 999, 874, 749, 624, 500, 375, 250 and 125, and its sparse attention keeps 20% of the attention tiles.

**We pick checkpoints by watching them.** Later checkpoints looked sharper but started to add objects partway through a clip, for example a second dragon in a sword-fight scene, and our automatic scorer did not notice. We release checkpoint 300, which held its scenes together best when we reviewed the held-out prompts by eye.

## Four-bit weights without clipping

NVFP4 stores each group of 16 values as 4-bit floats with a shared 8-bit scale, plus one scale per tensor that sets the overall range. For weights, we compute that per-tensor scale from the weights themselves. For activations it must be fixed before the data arrives. The simplest choice, a unit scale, covers magnitudes up to 6 × 448 = 2,688, and H3 activations are much larger.

{{< image src="img/fig_fc_out_amax.svg" alt="Bar chart of the largest input to each block's MLP output projection across 42 blocks, on a log scale. 40 of 42 bars exceed the 2,688 line; block 37 reaches 368,640." width="100%" title="Figure 4. Largest input to each block's MLP output projection, over 1,000 calibration prompts and all eight steps. With a unit scale, everything above the dashed line is clipped." >}}

In 40 of the 42 blocks, the input to the MLP output projection exceeds 2,688. In block 37 it reaches 368,640, 137 times the limit, and a unit scale clips these values on every forward pass. So we calibrate: we ran 1,000 prompts through the full eight-step sampler, recorded the largest input to each linear layer, and stored one static scale per layer in the checkpoint. FastH3 Trim has 294 calibrated layers, covering the attention projections, the MLPs and the sparse-attention gate. This extends the FastH3 V2 NVFP4 recipe from the MLPs to every quantized layer.

## Running on each machine

### RTX 5090

Our first FP4 export quantized only the MLPs, the setting we use on data-center GPUs. On a 5090 that left a 20 GB DiT, because the BF16 attention projections alone take 9.7 GB, and the text encoder no longer fit beside it. Every request moved the DiT to host memory and back: a 480p clip took 26.4 s, and a 768p clip did not fit at all.

With attention and the gate also in NVFP4, the DiT is 11.1 GiB and stays on the GPU. Only the 15.3 GiB text encoder moves per prompt. The same 480p clip takes 17.4 s, and the 10 s, 768p clip now fits and takes 80.5 s.

One detail cost us a crash first. Fast host-to-GPU copies need page-locked ("pinned") host memory, and PyTorch's pinned allocator rounds each block up to a power of two. For the H3 FP4 weight shapes, 2.87 GiB of tensors used 5.06 GiB of host RAM, enough to get the process killed in a 60 GB cloud container. We now pin one exact-size buffer per module with `cudaHostRegister` and place the tensors inside it, which brings the same tensors down to 2.90 GiB.

### RTX 4090 and GPUs with less memory

The RTX 4090 has no FP4 tensor cores, so it uses FP8: 8-bit weights with one scale per output channel and 8-bit activations with one scale per token. PyTorch's FP8 matrix multiply with these scales runs at about 70 TFLOPS on a 4090, slower than BF16 at about 160 TFLOPS. The per-tensor FP8 kernel runs at 220–305 TFLOPS, so we call it with unit scales and apply both scale vectors to the output in one fused pass. The result matches per-token, per-channel scaling and costs 5–10% more than per-tensor scaling.

Three more changes bring the 4090 to 41.8 s for a 5 s clip:

- **Sparse attention:** queries and keys are quantized to INT8 for the score computation, while values stay in BF16. The fine attention kernel runs 1.6× faster with about 0.6% relative error.
- **Text encoder:** it streams to the GPU one layer at a time through exact-size pinned buffers, and one fused kernel expands its NVFP4 weights.
- **VAE:** the same INT8 lightweight VAE as every other device, with a fused dequantization step and one shared quantized input for the Q, K and V projections. Decoded frames are bit-identical to the unoptimized path.

| RTX 4090, FastH3 Trim, FP8 | 832×480, 5 s | 832×480, 10 s |
|---|---:|---:|
| 24 GB (full GPU) | 41.8 s | 79.7 s |
| Limited to 16 GB | — | 104.0 s |
| Limited to 12 GB | — | 107.3 s |

For the 16 GB and 12 GB rows, we cap the PyTorch allocator on the same 4090. They show that the model fits in that much memory; a real 16 GB GPU will be slower.

### DGX Spark and Apple Silicon

A DGX Spark keeps the text encoder, the DiT and both VAEs in its 128 GB of unified memory, so nothing moves between requests. It uses the same NVFP4 checkpoints and lightweight VAE as the 5090, and two Sparks split each request with sequence parallelism.

| DGX Spark, 832×480 | 5 s | 10 s |
|---|---:|---:|
| 1× Spark, FastH3 Trim | 134.5 s | 277.3 s |
| 1× Spark, FastH3 V2 | 141.4 s | 307.2 s |
| 2× Spark, FastH3 Trim | 78.3 s | 164.5 s |
| 2× Spark, FastH3 V2 | 87.2 s | 180.0 s |

In [FastH3 Goes Local](/blogs/fasth3-local/), a 5 s clip took 243 s on one Spark and 209 s on two, with the four-step preview model and the full H3 VAE. The eight-step models now do twice as many denoising steps and still finish faster.

On Apple Silicon, FastH3 Trim runs in MLX with INT6 weights, the NVFP4 text encoder and the lightweight VAE.

<div class="fasth3-rtx-todo"><b>TODO (Mac).</b> M4 Max INT6 times at 5 s and 10 s, measured with the default attention path. Compare against FastH3 Goes Local (M4 Max INT6, 456 s for 5 s with the four-step preview and full VAE) and state those differences next to any ratio.</div>

## Where the time goes

{{< image src="img/fig_stages.svg" alt="100% stacked bars. RTX 4090 FastH3 Trim FP8 480p 5 s, 41.8 s: denoise 78%, decode 16%, rest 6%. RTX 4090 480p 10 s, 79.7 s: denoise 80%, decode 17%, rest 4%. 4× GB200 V1 768p 10 s, 15.5 s: denoise 37%, decode 25%, rest 38%." width="100%" title="Figure 5. Share of end-to-end time per stage." >}}

On one 4090, denoising is about 80% of the end-to-end time. Once the model fits in GPU memory and denoising gets fast, the other stages take a larger share. On four GB200s, the four-step V1 model spends 9.8 s computing a 10 s, 768p clip: 5.7 s denoising, 3.8 s decoding across the four GPUs, and the rest on text encoding. Moving frames out of the GPU workers and writing the MP4 take another 5.7 s, and that is the next stage we will optimize.

## Limitations and what comes next

- **FastH3 Trim is less capable than FastH3 V2.** Removing eight blocks costs some detail and prompt adherence, and long or busy scenes can gain or lose objects partway through. Use V2 when quality matters most.
- **This is our first pruned release.** We are experimenting with pruning FastH3 V2 itself instead of base H3, and we plan to push toward smaller models.
- **We reviewed quality by eye** on 36 held-out prompts, not with a large human study. Our automatic scorer misses speech and anatomy defects, so we do not rely on it.
- **Not tested yet:** RTX 30-series GPUs, real 16 GB and 12 GB GPUs (our numbers cap memory on a 4090), an 8 GB tier, and 10 s, 768p clips with less than 24 GB.

## Get the models

| Hardware | Model | Hugging Face |
|---|---|---|
| RTX 5090, RTX PRO 6000, DGX Spark (Blackwell) | FastH3 Trim, NVFP4 | [`FastVideo/FastVideo-FastH3-Trim-8-Step-NVFP4`](https://huggingface.co/FastVideo/FastVideo-FastH3-Trim-8-Step-NVFP4) |
| RTX 4090, 16 GB and 12 GB GPUs | FastH3 Trim, FP8 | [`FastVideo/FastVideo-FastH3-Trim-8-Step-FP8`](https://huggingface.co/FastVideo/FastVideo-FastH3-Trim-8-Step-FP8) |
| Apple Silicon (MLX) | FastH3 Trim, INT6 | [`FastVideo/FastVideo-FastH3-Trim-8-Step-MLX-INT6`](https://huggingface.co/FastVideo/FastVideo-FastH3-Trim-8-Step-MLX-INT6) |
| Source weights | FastH3 Trim, BF16 | [`FastVideo/FastVideo-FastH3-Trim-8-Step`](https://huggingface.co/FastVideo/FastVideo-FastH3-Trim-8-Step) |
| Full quality, Blackwell GPUs | FastH3 V2, NVFP4 | [`FastVideo/FastVideo-FastH3-8-Step-V2-NVFP4`](https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2-NVFP4) |
| Full quality, data-center GPUs | FastH3 V2, BF16 | [`FastVideo/FastVideo-FastH3-8-Step-V2`](https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2) |

Each repository includes the text encoder, the lightweight VAE and a `fastvideo_inference.json` file with the sampling schedule, which FastVideo reads automatically. On one RTX 5090:

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

<div class="fasth3-rtx-todo"><b>TODO before publishing.</b> Make the Trim repos public under these names and link each one to its Cookbook recipe.</div>

## Acknowledgements

FastH3 builds on [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3), and we thank the MiniMax team for releasing its weights and code.

The lightweight decoder is the [LynnReal Lightweight Video VAE](https://huggingface.co/stdstu123/LynnReal-Onmi-light-vae) ([paper](https://arxiv.org/abs/2609.15863), [code](https://github.com/LynnReal-AI/LynnReal-Omni)), loaded with the INT8 weights from [Kijai](https://huggingface.co/Kijai)'s [MiniMax-H3-experimental](https://huggingface.co/Kijai/MiniMax-H3-experimental). We thank both.

We thank the NVIDIA Enterprise Products team (Pengcheng Li and Cliff Woolley) for the Video Sparse Attention kernel, and the FlashInfer and NVIDIA Model Optimizer teams for the FP4 kernels and calibration tools. The FP4 sparse attention on RTX GPUs builds on [SageAttention](https://github.com/thu-ml/SageAttention), and Ollin Boer Bohan's [TAEH3](https://github.com/madebyollin/taehv) is the fast preview decoder.

The FastVideo team worked closely with [Nuva Lab](https://nuvalab.ai/), [NVIDIA FastGen](https://github.com/NVlabs/FastGen) (Julius Berner, Chao Liu, Arash Vahdat) and the NVIDIA Enterprise Products team on [FastH3](/blogs/fasth3-preview/). We also thank the [vLLM project](https://vllm.ai/), [NVIDIA](https://www.nvidia.com/en-us/) and [MBZUAI](https://mbzuai.ac.ae/) for their continued sponsorship and support of FastVideo.

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
.fasth3-rtx-article .fasth3-rtx-todo {
  margin: 1.4rem 0;
  padding: 0.85rem 1rem;
  border: 1.5px dashed #eb6834;
  border-radius: 10px;
  background: rgba(235, 104, 52, 0.07);
  font-size: 0.9rem;
  line-height: 1.5;
}

.fasth3-rtx-article .fasth3-rtx-grid {
  display: grid;
  margin: 1rem 0 1.6rem;
  gap: 0.9rem 0.6rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.fasth3-rtx-article .fasth3-rtx-clip {
  min-width: 0;
  margin: 0;
}

.fasth3-rtx-article .fasth3-rtx-hero {
  margin: 1.4rem 0 0.4rem;
}

.fasth3-rtx-article .fasth3-rtx-frame {
  position: relative;
  aspect-ratio: 832 / 480;
  border: 1.5px dashed var(--border);
  border-radius: 8px;
}

.fasth3-rtx-article .fasth3-rtx-frame--wide {
  aspect-ratio: 1344 / 768;
}

.fasth3-rtx-article .fasth3-rtx-frame::before {
  content: "pending · " attr(data-file);
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 0.4rem;
  color: var(--secondary);
  font-size: 0.72rem;
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
  font-size: 0.8rem;
  line-height: 1.35;
}

.fasth3-rtx-article .fasth3-rtx-clip > figcaption span {
  color: var(--secondary);
}

.fasth3-rtx-article table {
  font-size: 0.92rem;
}

.fasth3-rtx-article td {
  font-variant-numeric: tabular-nums;
}

@media (max-width: 760px) {
  .fasth3-rtx-article .fasth3-rtx-grid {
    grid-template-columns: 1fr;
  }
}
</style>
