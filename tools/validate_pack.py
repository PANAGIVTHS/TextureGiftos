#!/usr/bin/env python3
"""Static resource-pack cross-reference/animation validator (stdlib only)."""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
errors = []
warnings = []


def parse_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        errors.append(f'Invalid JSON {path.relative_to(ROOT)}: {exc}')
        return {}


def model_path(ref):
    ns, _, path = ref.partition(':')
    if not path:
        ns, path = 'minecraft', ns
    return ASSETS / ns / 'models' / (path + '.json'), ns


def texture_path(ref):
    ns, _, path = ref.partition(':')
    if not path:
        ns, path = 'minecraft', ns
    return ASSETS / ns / 'textures' / (path + '.png'), ns


def check_model_node(node, path):
    if isinstance(node, dict):
        if node.get('type') == 'minecraft:model':
            ref = node.get('model')
            if not isinstance(ref, str):
                errors.append(f'{path}: minecraft:model missing model string')
            elif model_path(ref)[1] != 'minecraft' and not model_path(ref)[0].is_file():
                warnings.append(f'{path}: missing custom model {ref}')
        for v in node.values():
            check_model_node(v, path)
    elif isinstance(node, list):
        for v in node:
            check_model_node(v, path)


def check_png(path):
    try:
        with path.open('rb') as f:
            header = f.read(24)
        if len(header) < 24 or header[:8] != b'\x89PNG\r\n\x1a\n':
            raise ValueError('invalid PNG header')
        return struct.unpack('>II', header[16:24])
    except (OSError, ValueError) as exc:
        errors.append(f'Invalid PNG {path.relative_to(ROOT)}: {exc}')
        return None


def main():
    parse_json(ROOT / 'pack.mcmeta')
    for path in ASSETS.rglob('*.json'):
        doc = parse_json(path)
        if '/models/item/' in path.as_posix():
            tex = doc.get('textures', {})
            for key, ref in tex.items():
                if not isinstance(ref, str):
                    errors.append(f'{path.relative_to(ROOT)}: invalid texture {key}')
                    continue
                resolved, namespace = texture_path(ref)
                if namespace != 'minecraft' and not resolved.is_file():
                    errors.append(f'{path.relative_to(ROOT)}: missing texture {key}={ref}')
            for i, el in enumerate(doc.get('elements', [])):
                for face, face_doc in el.get('faces', {}).items():
                    selector = face_doc.get('texture', '')
                    if not selector.startswith('#') or selector[1:] not in tex:
                        errors.append(f'{path.relative_to(ROOT)} element {i} face {face}: missing texture selector {selector}')
        if '/items/' in path.as_posix():
            check_model_node(doc.get('model'), path.relative_to(ROOT))
    for png in ASSETS.rglob('*.png'):
        size = check_png(png)
        meta_path = png.with_name(png.name + '.mcmeta')
        if not meta_path.exists():
            continue
        meta = parse_json(meta_path)
        if size:
            w, h = size
            anim = meta.get('animation')
            if not isinstance(anim, dict):
                errors.append(f'{meta_path.relative_to(ROOT)}: missing animation object')
            else:
                width = anim.get('width', w)
                height = anim.get('height', width)
                if width <= 0 or height <= 0 or w % width or h % height:
                    errors.append(f'{meta_path.relative_to(ROOT)}: invalid frame dimensions for {w}x{h} PNG')
                elif 'frames' in anim:
                    frames = anim['frames']
                    count = (w // width) * (h // height)
                    if any((f.get('index', -1) if isinstance(f, dict) else f) not in range(count) for f in frames):
                        errors.append(f'{meta_path.relative_to(ROOT)}: frame index out of bounds')
    for w in warnings:
        print('WARNING:', w)
    for e in errors:
        print('ERROR:', e)
    print(f'Validated {len(list(ASSETS.rglob("*.json")))} JSONs and {len(list(ASSETS.rglob("*.png")))} textures.')
    print(f'{len(errors)} errors, {len(warnings)} warnings.')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
