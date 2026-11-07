# Prompting SDXL (profile `sdxl-fast`): starting notes

These are starting notes, not lessons paid for like `prompting.md`'s: nobody has made a project's
assets with this profile yet. When a round teaches you something, add a "wrote X, got Y, write
instead" row here, the way `prompting.md` does.

What carries over from `prompting.md` unchanged: the project's art rules come first, framing is
stated explicitly, and the flat-background trick and its failure modes apply.

## How it differs from Z-Image Turbo

- **Short, front-loaded prompts.** SDXL reads prompts through CLIP text encoders, which take about
  75 tokens at a time and weigh the start most. Lead with subject, view and medium; follow with
  comma-separated details. Long descriptive sentences dilute rather than add.
- **Negative prompts still do nothing here.** The DMD2 LoRA runs at cfg 1, like Z-Image Turbo. Say
  what you want.
- **The checkpoint sets the style more than the prompt does.** Base SDXL is a generalist; a
  fine-tune trained on one medium (painterly, anime, flat vector, rendered 3D) draws that medium
  far better than prompt words can push base SDXL toward it. Choose the checkpoint per art
  direction, and record its exact file in the style guide with the profile name.
- **Weaker at counts, positions and text.** "Exactly two", "on the left", lettering on signs: expect
  misses more often than with Z-Image. Compose those in a later step (img2img, a hand edit) rather
  than prompting harder.
- **Seeds vary more.** Four seeds of one prompt are real alternatives, so a round explores more on
  its own.

## Sizes

Generate near one megapixel: 1024×1024, 896×1152, 1152×896, 832×1216, 1216×832. Below about 768
on the short side, quality falls off quickly. For small assets, generate at one of these sizes and
downscale.

## Pixel art

Base SDXL draws "pixel art" as fine detail with soft edges. A pixel-art fine-tune or LoRA usually
does better here (unlike Z-Image, where the one tried was rejected): try one round with and one
without, judge both after palette cleanup at true size, and record which you kept.

## Black images on older cards

The SDXL VAE overflows in half precision on some cards, GTX 16-series above all, and the result is
a black or noise image. Pass an fp16-fixed SDXL VAE with `--vae`, or start ComfyUI with
`comfy.py start --fp32-vae`.
