# <Game title> — art direction

**Chosen:** <date>, direction "<name>". **Frames:** `frames/`. **Palette:** `palette.gpl`.
**Chosen by:** the owner | the critic agent — *assumed*; runners-up in `runners-up/` until the owner confirms.

## The style in one paragraph

<What it looks like, what it feels like, and the one thing that makes it recognizable.>

## Do

- <e.g. two-tone shading, light from top-left>

## Don't

- <e.g. no outlines on props; no pure black>

## References

| Reference | What it contributes |
|---|---|
| <game or image> | <the one thing borrowed> |

## Sizes and canvases

| Asset kind | Canvas (px) | Scale in game | Notes |
|---|---|---|---|
| Character | <…> | <…> | <…> |

## Interface

How the interface looks. What reaches the player, and why, is in the GDD's interface section.

- **Material kit:** <the world's materials every screen is made of>
- **Type roles:** display <face, size, treatment> · body <face, size> · caption <…> · at most two or
  three treatments · source and licence <for each font>
- **Colour jobs:** accent <colour> = <its one job> · <signal colour> = <meaning> · frames and titles
  mid-tone
- **Smallest readable size:** <px at native resolution>
- **Motion:** <how things enter, leave and answer a press; durations; the reduced-motion end state>
- **Loudest moment:** <where it happens, and the space kept for it>
- **Frames:** `frames/<text-heavy screen>.png` (worst-case content) · `frames/<loudest moment>.png`

## Prompt core

The exact text and settings that produced the chosen frames. Every generation starts from these.

- **Generator and model:** <ComfyUI + model / Codex / Meshy model>
- **Settings:** <steps, cfg, sampler, size, seeds used>
- **Prompt core:** <the shared opening of every prompt>
- **Per-kind additions:** character: <…> · prop: <…> · scene: <…> · UI: <…>
