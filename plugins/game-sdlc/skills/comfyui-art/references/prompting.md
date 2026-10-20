# Prompting Z-Image Turbo: what we paid for

Z-Image Turbo follows long, concrete English descriptions well and ignores negative prompts
(it runs at cfg 1, so the negative text has no effect — say what you want, not what you don't).
Its seed variety is low: four seeds of one prompt are variations, not alternatives. To explore,
change the prompt.

## It draws what you name

| Wrote | Got | Write instead |
|---|---|---|
| "warm lantern light from the left" | a lantern object in every image | "lit warmly from the left side, as if by an unseen lantern" |
| "lantern and moonlight" rim lighting | a painted lantern and moon in the background | "light falls only on the character: a warm orange rim along his left edge, a cool pale blue rim along his right" + "no objects in the background" |
| "a cabin boy who drowned a century ago" | a teenager | the visible result: "a man in his mid-forties, grey at the temples, crow's feet" |
| "hard to trust / ancient eyes" + "rebuilt by the sea" | glowing white zombie eyes | "ordinary grey-green eyes, a steady unreadable gaze that could be kindness or calculation" |
| "brass telescope" | binoculars about half the time | "one long single-tube brass telescope, a single cylinder with one eyepiece" |
| "holds a telescope" (sprite) | one at the eye *and* one in the hand | "holds exactly one closed brass telescope, in his right hand, at his side" |
| "gouache on toned paper, art-direction sheet" | borders and fake painter's signatures | "one full-bleed painting that fills the whole frame, with plain unmarked corners" |
| "long coat" | a modern double-breasted trench coat | the era's cut: "long-skirted 18th-century frock coat with wide turned-back cuffs and a single row of small buttons" |
| "faded madder-red coat" | a clean bright red coat | "faded to a dusty brick-brown red, sun-bleached at the shoulders, elbows patched with mismatched brown cloth, frayed hem" |
| "bright red coat" (pixel) | orange after palette snapping | "dark wine-red (a deep muted red, not bright)" |

## Subtle strangeness

"Weird" details (barnacles, dripping seawater) fade out as the costume gets more precise — the
model spends its attention on what is described in most detail. Make the strange detail specific,
visible and placed: "a crust of grey-white barnacles covers the back of his left hand and wrist,
clearly visible"; "his coat is soaking wet and dripping seawater onto the dry deck". Even then it
may land somewhere else (a cuff, a collar); judge whether it still reads.

## Style words

- "Painted character concept art, gouache and oil, loose visible brushstrokes, soft edges,
  limited muted palette" → a painting. Without the medium you get a film still.
- The style can drift toward classical oil portraiture as the costume gets historical; if the
  loose concept-art look matters, repeat the medium words and "loose".
- For pixel art, trait words beat game names: view, head-to-body ratio, outline type, tones per
  material, "no anti-aliasing, no dithering, no gradients".

## Backgrounds

Ask for "plain flat solid pure magenta background, completely empty, no ground, no shadow".
It is honoured most of the time, not always: expect gradients, a darker ground-shadow ellipse,
and occasionally white or a colour taken from the subject. The flood-fill key handles the first
two; regenerate for the rest.

## Composition

State framing explicitly: "full body, feet near the bottom", "head and shoulders filling the
frame", "centred". For assets placed on a canvas, give percentages down the frame and how much of
the canvas the subject may occupy.
