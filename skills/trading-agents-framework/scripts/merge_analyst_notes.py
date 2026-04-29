#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser(); p.add_argument('notes', nargs='+'); p.add_argument('--out', default='./analyst_bundle.json'); args = p.parse_args()
    bundle = [json.loads(Path(x).read_text()) for x in args.notes]
    Path(args.out).write_text(json.dumps({'notes': bundle}, ensure_ascii=False, indent=2))
    print(args.out)

if __name__ == '__main__':
    main()
