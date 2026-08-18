import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const root = path.resolve(import.meta.dirname, '..');
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, 'src', 'data', name), 'utf8'));
const benchmarks = read('benchmarks.json');
const sources = read('sources.json');
const summary = read('summary.json');
const leaders = read('leaders.json');

const errors = [];
const ids = new Set(benchmarks.map((row) => row.id));
const sourceIds = new Set(sources.map((row) => row.id));
const cursorBenchRows = benchmarks.filter((row) => row.benchmark === 'CursorBench' && row.version === '3.2');

if (cursorBenchRows.length !== 12) errors.push(`Expected 12 CursorBench 3.2 rows, found ${cursorBenchRows.length}`);
if (!sourceIds.has('cursorbench-3-2')) errors.push('CursorBench 3.2 source record is missing');
for (const id of [
  'cursorbench-3-2-fable-5-max',
  'cursorbench-3-2-opus-5-max',
  'cursorbench-3-2-gpt-5-6-sol-max',
  'cursorbench-3-2-grok-4-5-high'
]) {
  if (!ids.has(id)) errors.push(`Required CursorBench row is missing: ${id}`);
}

for (const row of cursorBenchRows) {
  const passRate = row.score / 100;
  const expectedCost = row.apiCostPerTaskUsd / passRate;
  const expectedTokens = row.tokensPerTask / passRate;
  const expectedSteps = row.stepsPerTask / passRate;
  if (!Number.isFinite(row.apiUsdPerExpectedPass) || Math.abs(row.apiUsdPerExpectedPass - expectedCost) > 1e-6) {
    errors.push(`${row.id}: API cost per expected pass is inconsistent`);
  }
  if (!Number.isFinite(row.tokensPerExpectedPass) || Math.abs(row.tokensPerExpectedPass - expectedTokens) > 0.02) {
    errors.push(`${row.id}: tokens per expected pass is inconsistent`);
  }
  if (!Number.isFinite(row.stepsPerExpectedPass) || Math.abs(row.stepsPerExpectedPass - expectedSteps) > 0.001) {
    errors.push(`${row.id}: steps per expected pass is inconsistent`);
  }
}

const fableRows = benchmarks.filter((row) => /fable/i.test(`${row.id} ${row.model || ''}`));
if (fableRows.length < 8) errors.push(`Expected at least 8 Fable benchmark rows, found ${fableRows.length}`);
if (summary.externalBenchmarkRows !== benchmarks.length) errors.push('Summary benchmark count does not match generated rows');
if (summary.fableBenchmarkRowCount !== fableRows.length) errors.push('Summary Fable count does not match generated rows');
if ((leaders.fableRelevantBenchmarkIds || []).length !== fableRows.length) errors.push('Leader metadata omits Fable benchmark rows');

if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log(`Validated ${cursorBenchRows.length} CursorBench 3.2 rows and ${fableRows.length} total Fable benchmark rows.`);
