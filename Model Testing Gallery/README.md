# Model Testing Gallery

The builds behind [eamonmckiernan.im/gallery.html](https://eamonmckiernan.im/gallery.html) —
99 self-contained browser demos written by AI models, published unedited, defects and all.

This repo mirrors the website: every published build is here. A withdrawn build keeps its file
here but no longer has a card on the page.
Organised by model. Prompts live in [`prompts/`](prompts) and are quoted verbatim, typos included.

## Builds

| Model | Builds | Prompt |
|---|---|---|
| Qwen 4 Max — DeepSeek Harness | `Qwen 4 Max/{basalt-organ,blue-hour-dry-dock,breadfruit-cay,glass-tide,mangrove-after-dark,medieval-village,rain-cathedral,salt-mirror,the-bleaching-green,the-castle,the-last-light,the-pagoda,torchlight-depths}.html` | `prompts/{the-basalt-organ,blue-hour-dry-dock,the-glass-tide,mangrove-after-dark,medieval-village,the-rain-cathedral,salt-mirror,the-castle,the-last-light,the-pagoda,torchlight-depths,breadfruit-cay,linen-on-the-bleaching-green}.md` |
| Hy4 Flash — DeepSeek Harness | `Hy4 Flash/{BLUE_HOUR_DRY_DOCK,BREADFRUIT_CAY,LINEN_ON_THE_BLEACHING_GREEN,MANGROVE_AFTER_DARK,SALT_MIRROR,THE_BASALT_ORGAN,THE_GLASS_TIDE,THE_LAST_LIGHT,THE_RAIN_CATHEDRAL,TWO_SHORES,castle,medieval-village,pagoda}.html` | same briefs as Qwen 4 Max, quoted in `prompts/` |
| Hy4 Flash - Maya (served by Maya) | `Hy4 Flash Maya M/{breadfruit_cay,linen_bleaching_green}.html` | `prompts/{breadfruit-cay,linen-on-the-bleaching-green}.md` |
| Qwen3.8 Flash-Next (Strata) | `Qwen3.8 Flash-Next/{sky-temple,sky-temple-agent,living-city,neon-drift,pulse-engine,cloth-lab,basalt-organ,mangrove-after-dark,rain_cathedral,sky_temple}.html` | `prompts/legacy-*.md` |
| Qwen3.8-27B (llama.cpp, four serving configs) | `Qwen3.8-27B/{DFlash2/pagoda,DSpine/THE-PAGODA,MTP/sky-temple,Plain/pagoda}.html` | `prompts/pagoda.md` |
| Qwen 4 Preview — DeepSeek Harness | `Qwen 4 Preview/{liberty-1886,medieval-village,the-pagoda,torchlight-depths}.html` | `prompts/{liberty,village,pagoda,torchlight}.md` |
| Qwen 4 Preview — Qwen Code | `QwenCode/{sky-temple,medieval-village,liberty-1886}.html` | `prompts/{pagoda,village,liberty}.md` |
| DeepSeek V4.1 Flash | `DeepSeek-V4.1-Flash-1017/{THE-CASTLE,breadfruit-cay,linen-on-the-bleaching-green}.html` | `prompts/{castle,breadfruit-cay,linen-on-the-bleaching-green}.md` |
| HY4 | `HY4/THE-CASTLE.html` | `prompts/castle.md` |

`serving.json` holds the per-build provenance the page shows — provider, harness, model, and the
serving config where one was recorded. Builds with no recorded provider are not shipped.

## Method

- **One-shot, mostly.** One message and one file, with follow-ups only where the session log
  records them. Qwen3.8-27B restarted sessions on its context limit; those count as follow-ups.
- **Self-contained.** Each file opens by double-click with no network access, except three.js
  import maps where the prompt allowed it.
- **Judged in a real browser** at 1920×1080 from `file://`. A 2D canvas faking depth is a failure.

## Provenance

DeepSeek Harness sessions (`C:\Users\Eamon\.dsh\sessions`) hold the first prompt and every
follow-up for the Qwen and DeepSeek builds. The Qwen3.8 Flash-Next prompts were recovered from
the earlier prompt-indexed pages of the site. Nothing here was reconstructed by guesswork.
