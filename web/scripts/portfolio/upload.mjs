#!/usr/bin/env node

// Uploads the media the Portfolio site shows to R2 and records it in Portfolio's
// media-manifest.json. How it works: Portfolio/scripts/upload-media.mjs.
// `--compare` uploads nothing and writes portfolio-compare.html instead.
import { fileURLToPath } from "node:url";
import { uploadMedia } from "../../../../../Portfolio/scripts/upload-media.mjs";
import { stillUploads } from "../../../../../Portfolio/scripts/capture-stills.mjs";
import { STILLS } from "./stills.mjs";

// stills.mjs writes portfolio-stills/ under the repo root.
process.chdir(fileURLToPath(new URL("../../..", import.meta.url)));
uploadMedia({
  ...stillUploads(STILLS),
  "portfolio-media/data-ink-ratio.webp": "data-analysis/data-ink-ratio.webp",
});
