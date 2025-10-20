#!/usr/bin/env python3
"""
Simple script to POST a local sample image to the running API and print JSON response.
Usage:
    python scripts/post_sample.py /path/to/image.png --url http://127.0.0.1:8000/api/pipeline/
"""
import sys
import argparse
import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument('image', help='Path to image file (PNG/JPG)')
    p.add_argument('--url', default='http://127.0.0.1:8000/api/pipeline/', help='API endpoint URL')
    p.add_argument('--visualize', action='store_true', help='Request visualization data URL')
    args = p.parse_args()

    params = {}
    if args.visualize:
        params['visualize'] = 'true'

    with open(args.image, 'rb') as f:
        files = {'image': (args.image, f, 'application/octet-stream')}
        resp = requests.post(args.url, files=files, params=params)

    try:
        resp.raise_for_status()
    except Exception as e:
        print('Request failed:', e)
        print('Status code:', resp.status_code)
        print('Response body:', resp.text)
        sys.exit(1)

    print(resp.json())


if __name__ == '__main__':
    main()
