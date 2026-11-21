// Velmora passport spread — Node 22, no dependencies.
//
// The artwork lives in entry.png next to this file. This program checks
// that the PNG is whole and within the bounty limits, then places a copy
// at <output>/entry.png, where <output> is /output inside the grading
// container or MAKEFUN_OUTPUT_DIR when run by hand:
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//
// Nothing here draws anything: the picture is produced by draw_entry.py
// (Pillow, run on the author's machine) and committed beside this file,
// so the program stays small and needs no network and no extra packages.

import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const MAX_BYTES = 1048576;
const MAX_SIDE = 1024;
const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function die(message) {
  throw new Error(`passport entry: ${message}`);
}

function readPng(path) {
  const info = statSync(path);
  if (info.size > MAX_BYTES) {
    die(`entry.png is ${info.size} bytes, above the ${MAX_BYTES} byte cap`);
  }
  return readFileSync(path);
}

function checkPng(bytes) {
  if (bytes.length < 33) {
    die('entry.png is too short to hold a PNG header');
  }
  for (let i = 0; i < PNG_SIGNATURE.length; i += 1) {
    if (bytes[i] !== PNG_SIGNATURE[i]) {
      die('entry.png does not begin with the PNG signature');
    }
  }
  if (bytes.toString('latin1', 12, 16) !== 'IHDR') {
    die('entry.png has no IHDR chunk in the expected place');
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== MAX_SIDE || height !== MAX_SIDE) {
    die(`entry.png is ${width}x${height}, expected ${MAX_SIDE}x${MAX_SIDE}`);
  }
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const here = new URL('./entry.png', import.meta.url);

const png = readPng(here);
checkPng(png);

mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, 'entry.png'), png);
