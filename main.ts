// Passport-spread entry (Node 22, standard library only): the image is the
// entry.png beside this file, and the program copies it to the output
// directory as entry.png. The gate takes a whole PNG of at most 1 MiB
// and 1024 by 1024 pixels, and the judge sees exactly the bytes copied.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const src = new URL('./entry.png', import.meta.url);

// Validate the entry file before copying, so a bad image fails loudly
// instead of reaching the grader as a valid-looking copy.
const stat = statSync(src);
if (stat.size > 1048576) {
  throw new Error(`entry.png is ${stat.size} bytes, over the 1 MiB limit`);
}
const bytes = readFileSync(src);
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (bytes.length < 33 || !bytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error('entry.png does not start with the 8-byte PNG magic');
}
if (bytes.toString('latin1', 12, 16) !== 'IHDR') {
  throw new Error('entry.png has no IHDR chunk where the PNG header belongs');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
}
copyFileSync(src, join(outDir, 'entry.png'));
