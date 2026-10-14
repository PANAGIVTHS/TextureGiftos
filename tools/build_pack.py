#!/usr/bin/env python3
"""Create an installable resource-pack ZIP without Git/source-only files."""
from pathlib import Path
import argparse
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'dist' / 'TextureGiftos_1.21.11.zip')
    args = parser.parse_args()
    check = subprocess.run([sys.executable, str(ROOT / 'tools' / 'validate_pack.py')], check=False)
    if check.returncode:
        print('Pack validation failed; not packaging.', file=sys.stderr)
        return 1
    out = args.output.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    inputs = [ROOT / 'pack.mcmeta', ROOT / 'pack.png']
    inputs += [p for p in (ROOT / 'assets').rglob('*') if p.is_file()]
    with ZipFile(out, 'w', ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(inputs):
            z.write(f, f.relative_to(ROOT).as_posix())
    print(f'Pack created: {out} ({len(inputs)} files)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
