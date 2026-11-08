# Godot Compatibility renderer: colour and drawing traps

Measured in Godot 4.7.1 while porting the catalog's looks, each against a browser frame of the
same scene. The Compatibility renderer (OpenGL; web exports and low-end devices) differs from
Forward+ in where colour is decoded and encoded, so a shader that is right in one is wrong in the
other. Each entry's `godot.md` cites these by number and adds only its own.

Branch inside a shader with `#if CURRENT_RENDERER == RENDERER_COMPATIBILITY`, and test every look
in the renderer the game ships with.

## Colour space

1. **Unshaded output skips the sRGB encode.** In Compatibility the base pass works on sRGB values
   as they are: an unshaded `ALBEDO` or an `EMISSION` reaches the screen without the encode Forward+
   applies (an emission of 0.214 shows as 54/255, not 128). A flat colour looks right; any maths on
   it (lighting, fog, tints, alpha) happens in the wrong space. Decode to linear yourself, do the
   maths, and encode before writing, under the Compatibility branch only.
2. **Lit `ALBEDO` is treated as sRGB and linearised after `fragment()`.** Writing 0.5 lights the
   face as 0.214. Compute albedo in linear and hand Compatibility `to_srgb(albedo)`.
3. **`fragment()` colours come from `source_color` uniforms; `light()` colours are linear `vec3`.**
   A plain `vec3` uniform used as albedo comes out as if decoded twice (about albedo squared). A
   `source_color` uniform read in `light()` is not linearised. So: albedo and anything else mixed in
   `fragment()` is `source_color`, set from a `Color`; key, fill, rim and fog colours used in
   `light()` are plain `vec3`s holding linear values, set from GDScript as a `Vector3`.
4. **`source_color` textures arrive undecoded in some paths** (unshaded materials, HDR 2D
   SubViewports). Decode them in the shader under the Compatibility branch.
5. **Vertex colours are linearised on their way into `fragment()`;** in `vertex()` they are raw in
   both renderers. Read data stored in vertex colours (a smoothed normal, a mask) in `vertex()`.
6. **Sky shaders run in sRGB** in Compatibility and in linear in Forward+; a gradient blends
   differently. Branch on the renderer.
7. **Dark tones lose a level or two.** The 3D image passes through an 8-bit linear buffer whatever
   the HDR 2D and MSAA settings: very dark palette colours land one or two codes off. Codes above
   about 124 come through exactly. Don't store data in dark codes.

## Lights, ambient and fog

8. **Environment ambient plus a shadow-casting light brightens every lit face**, even with
   `StandardMaterial3D`. Keep the Environment's ambient black and add the fill inside `light()`.
9. **Environment fog is applied in both passes**, so distant objects wash out. Mix fog in the shader
   and leave the Environment's fog off.
10. **Each shadowed spot or omni light is an additive pass that adds sRGB-encoded light** (two
    lights of 0.107 make 184/255, not 127). No per-pass correction works with two shadowed lights:
    render the shadow maps yourself and light everything in one pass, or use one shadowed light.
11. **Faint additive blending disappears and strong additive blending overshoots,** because it adds
    in sRGB. Mix toward the light colour instead (opacity × about 2.5 for faint shafts), or scale a
    strong addition by about 0.7.
12. **`DirectionalLight3D.shadow_blur` does nothing.** The shadow atlas size and
    `directional_shadow_max_distance` are the only levers on the penumbra.
13. **`shadow_normal_bias` around 1.0 darkens lit faces slightly** (a face shadows itself through the
    filter); 2.0 removes it.
14. **Writing `ALPHA` moves every material using that shader to the transparent pass.** Give
    see-through things (rings, markers, overlays) a shader of their own.

## Textures

15. **Mipmaps are averaged in sRGB** (the importer, and `Image.generate_mipmaps()` on 8-bit images),
    and textures are filtered before the decode, so contrasty or finely hatched maps darken as they
    shrink. Convert to linear once at load (`Image.srgb_to_linear()` or a half-float image), build
    the mipmaps from the linear values, and sample raw.
16. **Data textures must stay exact.** Index maps, slot maps and pixel art: import Lossless, no
    mipmaps unless the style wants them, `detect_3d/compress_to = Disabled` (Godot otherwise
    switches a texture to VRAM compression the first time it's used in 3D), and GLB images embedded
    uncompressed. Sample with `filter_nearest` and without `source_color`.
17. **Nearest close up, smooth far away** has no separate magnification filter: use
    `filter_nearest_mipmap` (or `_anisotropic`) with mipmaps on.

## 2D drawing

18. **No 2D antialiasing.** `msaa_2d` and `Line2D.antialiased` change nothing in Compatibility (Forward+
    honours MSAA): polygon and line edges come out stair-stepped, and a thin line straddling a pixel
    edge fills two whole pixels. Either supersample (draw into a 2× SubViewport and filter down) or
    feather by hand: fill the shape shrunk by half a pixel and ring it with a one-pixel band fading
    to transparent.
19. **Transparent SubViewports hold premultiplied colour.** Composite them with
    `BLEND_MODE_PREMULT_ALPHA` and write blur results with `blend_premul_alpha`, or edges darken.
20. **A `CanvasGroup` with an ADD `CanvasItemMaterial` draws white rectangles** in a transparent
    SubViewport. Add the group with a shader that reads its backbuffer and adds its colour.
21. **Separate additive strokes stack where a path overlaps itself.** Draw a path's strokes opaque
    inside a `CanvasGroup` and add the group once.
22. **`draw_colored_polygon()` draws nothing for a polygon that crosses itself or is degenerate**
    ("Invalid polygon data"). Union a jittered outline with a rectangle well inside it, and fall back
    to the true shape when an inset one won't triangulate.

## Text

23. **Text scaled by a node transform is rasterised at the original size and stretched.** Draw it at
    the target resolution instead.
24. **Measured widths are rounded up to whole pixels** (`Font.get_string_size()`, `TextLine`) while
    glyphs sit at fractional advances, so chained layouts drift. Sum the shaped glyph advances from
    the `TextServer` when positions depend on widths, and use `HINTING_NONE` with subpixel
    positioning for fractional advances.
25. **Bundle every font as a `FontFile`.** A `SystemFont` or an OS fallback for missing glyphs picks a
    different face, size and baseline per platform. Name a symbol face for marks the text face lacks.
