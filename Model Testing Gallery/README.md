# Model Testing Gallery

One-shot browser demos written by local models on my own hardware — one prompt, one
self-contained HTML file, no follow-up fixes. Every build here is real output, published
unedited, defects and all.

Organised by model. Prompts live in [`prompts/`](prompts) and are quoted verbatim.

## Builds

| Model | Builds | Prompt |
|---|---|---|
| Qwen3.8-27B (Q8_K_XL, four serving configs) | `Qwen3.8-27B/DFlash2/pagoda.html`, `DSpine/THE-PAGODA.html`, `MTP/sky-temple.html`, `Plain/pagoda.html` | `prompts/pagoda.md` |
| Qwen 4 Preview | `Qwen 4 Preview/{liberty-1886,medieval-village,the-pagoda,torchlight-depths}.html` | `prompts/liberty.md`, `village.md`, `pagoda.md`, `torchlight.md` |
| Qwen Code (Qwen 4 Max Preview) | `QwenCode/{sky-temple,medieval-village,liberty-1886}.html`, `QwenCode/lbuild/baseline-gap.html` | `prompts/pagoda.md`, `village.md`, `liberty.md` |
| DeepSeek V4.1 Flash | `DeepSeek-V4.1-Flash-1017/{THE-CASTLE,sky-temple-…,test1-…}.html` | `prompts/castle.md`, `prompts/bench-pack-sky-temple.md` |
| MiniMax M3.1 Flash | `MiniMax M3.1-Flash Tests/{sky-temple-minimax-m3-1-flash,dusk-cityline-minimax-m3.1-flash}.html` | `prompts/bench-pack-sky-temple.md`, `bench-pack-dusk-cityline.md` |
| HY4 | `HY4/THE-CASTLE.html` | `prompts/castle.md` |
| LongCat 2.5 | `LongCat-2.5/sky-temple.html` | `prompts/pagoda.md` |

## Method

- **One shot.** One message, no human fixes. Follow-up counts are recorded per build where the
  session log has them; Qwen3.8-27B restarted sessions on its context limit and those are marked
  as follow-ups rather than fresh runs.
- **Self-contained.** Each file must open by double-click with no network access, except the
  three.js import map where the prompt allowed it.
- **Judged in a real browser** at 1920×1080 from `file://`. A 2D canvas faking depth is a failure.

## Provenance

DeepSeek Harness sessions (`C:\Users\Eamon\.dsh\sessions`) hold the first prompt and every
follow-up for the Qwen and DeepSeek builds. Older builds predate the harness and are matched to
the published bench pack instead; where a build predates the current pack revision that is noted
on the build page.

Held at [eamonmckiernan.co.uk/model testing gallery](https://eamonmckiernan.uk/gallery.html).
