#!/usr/bin/env python3
"""Convert sample PDF pages to images and run pipeline detection on each page.

Requires poppler (system package) for pdf2image. If poppler isn't installed,
the script will print instructions.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PDF = ROOT.parent / 'sample_pid8.pdf'
OUT_DIR = ROOT / 'sample_output'

def main():
    if not SAMPLE_PDF.exists():
        print(f'Sample PDF not found at {SAMPLE_PDF}. Place the PDF at the repository root as sample_pid8.pdf')
        sys.exit(1)

    try:
        from pdf2image import convert_from_path
    except Exception as e:
        print('pdf2image is not available or poppler not installed. Install poppler (system) and pdf2image (pip).')
        print('On Ubuntu: sudo apt-get install poppler-utils')
        print('Then: pip install pdf2image')
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print('Converting PDF to images...')
    images = convert_from_path(str(SAMPLE_PDF))

    results = []
    for i, img in enumerate(images):
        img_path = OUT_DIR / f'page_{i+1}.png'
        img.save(img_path, format='PNG')
        print(f'Running detection on {img_path}...')
        # Import detect_pipelines dynamically
        sys.path.insert(0, str(ROOT))
        from pid.utils import detect_pipelines
        pipes = detect_pipelines(str(img_path), visualize=True)
        if isinstance(pipes, tuple):
            pipelines, visualization = pipes
        else:
            pipelines = pipes
            visualization = None
        out = {
            'page': i+1,
            'image': str(img_path),
            'pipelines': pipelines,
        }
        if visualization:
            out['visualization'] = visualization
        results.append(out)

    out_file = OUT_DIR / 'output.json'
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=2)

    print('Results written to', out_file)


if __name__ == '__main__':
    main()
