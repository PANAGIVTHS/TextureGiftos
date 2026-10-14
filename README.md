# TextureGiftos — resource-pack source

This repository branch contains the **modern Java item-definition version** of
TextureGiftos. Its `pack.mcmeta` declares resource-pack format **69–75**
(Minecraft **1.21.9–1.21.11**, with the main target being **1.21.11**).
It is **not compatible with Java 1.20.1** without a separate legacy conversion.

## Install

Build an installable ZIP using:

```sh
python3 tools/build_pack.py
```

It writes `dist/TextureGiftos_1.21.11.zip` with `pack.mcmeta`, `pack.png`
and `assets/` at the **ZIP root**, excluding Git and source-only files.

In the game, enable the pack via Options → Resource Packs and reload with F3+T.

## Dragonslayer

The model is at `assets/mcd/models/item/swords/dragonslayer.json`.
It uses **vanilla** Minecraft block textures for most geometry and the two
included **custom** textures:

- `mcd:item/swords/under_fix`: fixed patch texture (static, 256×256)
- `mcd:item/swords/handle_wraps`: animated ribbon (16×48 pixels: 3 frames of
  16×16, 10 ticks/frame, interpolated), defined by `handle_wraps.png.mcmeta`

There are **two independent ways** to use it in Minecraft 1.21.11:

1. Direct model selection (no renaming or client mods required):

   ```mcfunction
   /give @s minecraft:netherite_sword[minecraft:item_model="mcd:swords/dragonslayer"]
   ```

   This also works on other compatible items via the `item_model` component,
   subject to modded-item custom renderers.

2. Give yourself a normal Netherite Sword and rename it to **Dragonslayer**
   (or **Dragon Slayer**) using an anvil. The name-selection rule lives in
   `assets/minecraft/items/netherite_sword.json`.

The reusable item definition is located at
`assets/mcd/items/swords/dragonslayer.json`.

## Other existing items

- `minecraft:netherite_sword` custom names: `Guts' Sword`, `Aatrox`,
  `Tenryū’s Shriek`, `Dragonslayer`, `Dragon Slayer`.
- `minecraft:ender_eye` name: `Ender's Wrath`.
- `assets/mcd/items/` also contains standalone item-model definitions for
  `guts`, `aatrox`, `agsheath`, `varus` and `scanner_detector`.

## Known incomplete feature

`assets/minecraft/items/bow.json` references **four** missing model files:
`mcd:item/bows/elite_power_bow` and
`elite_power_bow_pulling_0/1/2`. They were already absent in the supplied
repository. Rather than silently change the intended "Elite Power Bow"
appearance to another weapon, those references were left untouched.
You need the missing models (and any textures they require) to finish that feature.

## Validate

Run the included validator in the repository root:

```sh
python3 tools/validate_pack.py
```

It checks JSON, referenced custom model/texture files, unresolved model faces
and PNG animation metadata. It reports pre-existing missing bow models as
warnings rather than confusing them with fixed Dragonslayer issues.
This is a **static check**, not a Minecraft client rendering test.
