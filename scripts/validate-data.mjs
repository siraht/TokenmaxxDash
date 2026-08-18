import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const root = path.resolve(import.meta.dirname, '..');
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, 'src', 'data', name), 'utf8'));
const plans = read('plans.json');
const benchmarks = read('benchmarks.json');
const sources = read('sources.json');
const summary = read('summary.json');
const models = read('models.json');
const qualityRoutes = read('quality-routes.json');
const taskEstimates = read('subscription-task-estimates.json');
const leaders = read('leaders.json');
const candidates = read('candidates.json');
const schema = JSON.parse(fs.readFileSync(path.join(root, 'public', 'schema', 'community-benchmark-submission.schema.json'), 'utf8'));

const errors = [];
const unique = (rows, label) => {
  const seen = new Set();
  for (const row of rows) {
    if (!row.id) errors.push(`${label}: missing id`);
    if (seen.has(row.id)) errors.push(`${label}: duplicate id ${row.id}`);
    seen.add(row.id);
  }
  return seen;
};

const planIds = unique(plans, 'plan');
const benchmarkIds = unique(benchmarks, 'benchmark');
const sourceIds = unique(sources, 'source');
const modelIds = unique(models, 'model');
const qualityRouteIds = unique(qualityRoutes, 'quality route');
const taskEstimateIds = unique(taskEstimates, 'task estimate');
unique(candidates, 'candidate');

const validStatuses = new Set(['exact', 'derived', 'measured-range', 'partial', 'provider-hidden', 'secondary', 'unverified-candidate', 'legacy']);
const validCoverage = new Set(['direct-agent-and-model', 'direct-agent', 'direct-model', 'no-external-benchmark', 'catalog-only']);

for (const plan of plans) {
  for (const id of plan.sourceIds || []) if (!sourceIds.has(id)) errors.push(`plan ${plan.id}: missing source ${id}`);
  for (const id of plan.modelCoverageIds || []) if (!modelIds.has(id)) errors.push(`plan ${plan.id}: missing model coverage ${id}`);
  if (!validStatuses.has(plan.calculationStatus)) errors.push(`plan ${plan.id}: unsupported calculation status ${plan.calculationStatus}`);
  if (plan.calculationStatus === 'opaque') errors.push(`plan ${plan.id}: legacy opaque status survived enrichment`);
  if (String(plan.valueDisplay || '').toLowerCase() === 'unresolved') errors.push(`plan ${plan.id}: unresolved value display survived enrichment`);
  if (plan.calculationStatus === 'provider-hidden' && plan.valueMultiple != null) errors.push(`plan ${plan.id}: provider-hidden plan has numeric value multiple`);
  if (plan.valueMultiple != null && (!Number.isFinite(plan.valueMultiple) || plan.valueMultiple < 0)) errors.push(`plan ${plan.id}: invalid value multiple`);
  if (plan.valueMultipleLow != null && plan.valueMultipleHigh != null && plan.valueMultipleLow > plan.valueMultipleHigh) errors.push(`plan ${plan.id}: reversed value range`);
  if (plan.priceMonthly != null && plan.priceMonthly < 0) errors.push(`plan ${plan.id}: negative price`);
  if (!validCoverage.has(plan.benchmarkCoverage)) errors.push(`plan ${plan.id}: invalid benchmark coverage ${plan.benchmarkCoverage}`);
  const advertised = plan.models || [];
  if (advertised.length !== (plan.modelCoverageIds || []).length) errors.push(`plan ${plan.id}: ${advertised.length} advertised model labels but ${(plan.modelCoverageIds || []).length} coverage ids`);
}

for (const row of benchmarks) {
  if (!sourceIds.has(row.sourceId)) errors.push(`benchmark ${row.id}: missing source ${row.sourceId}`);
  if (row.score == null || !Number.isFinite(row.score) || row.score < 0) errors.push(`benchmark ${row.id}: invalid score`);
  if (row.kind === 'model-intelligence' && row.score > 0 && row.blendedPricePerMUsd > 0) {
    if (!(row.blendedUsdPerIntelligencePoint > 0)) errors.push(`benchmark ${row.id}: missing $/intelligence-point metric`);
  }
  if (row.kind === 'coding-agent' && row.benchmark === 'Artificial Analysis Coding Agent Index' && row.apiCostPerTaskUsd > 0 && row.score > 0) {
    if (!(row.apiUsdPerExpectedPass > 0)) errors.push(`benchmark ${row.id}: missing API $/expected pass`);
  }
}

for (const model of models) {
  if (!validCoverage.has(model.benchmarkCoverage)) errors.push(`model ${model.id}: invalid coverage ${model.benchmarkCoverage}`);
  for (const id of model.planIds || []) if (!planIds.has(id)) errors.push(`model ${model.id}: missing plan ${id}`);
  for (const id of model.directModelBenchmarkIds || []) if (!benchmarkIds.has(id)) errors.push(`model ${model.id}: missing model benchmark ${id}`);
  for (const id of model.directAgentBenchmarkIds || []) if (!benchmarkIds.has(id)) errors.push(`model ${model.id}: missing agent benchmark ${id}`);
  const hasDirect = (model.directModelBenchmarkIds?.length || 0) + (model.directAgentBenchmarkIds?.length || 0) > 0;
  if (model.rankingEligible !== hasDirect) errors.push(`model ${model.id}: ranking eligibility does not match direct evidence`);
  if (!hasDirect && !model.exclusionReason) errors.push(`model ${model.id}: unbenchmarked route lacks exclusion reason`);
}

for (const route of qualityRoutes) {
  if (!planIds.has(route.planId)) errors.push(`quality route ${route.id}: missing plan ${route.planId}`);
  if (!modelIds.has(route.modelId)) errors.push(`quality route ${route.id}: missing model ${route.modelId}`);
  if (!(route.intelligenceIndex > 0)) errors.push(`quality route ${route.id}: invalid intelligence score`);
  if (route.rankingEligible && !(route.planValueMultiple >= 0)) errors.push(`quality route ${route.id}: ranking eligible without quantified plan value`);
}

for (const row of taskEstimates) {
  if (!planIds.has(row.planId)) errors.push(`task estimate ${row.id}: missing plan ${row.planId}`);
  if (!benchmarkIds.has(row.benchmarkId)) errors.push(`task estimate ${row.id}: missing benchmark ${row.benchmarkId}`);
  if (!(row.expectedBenchmarkPassesPerAverageMonth > 0)) errors.push(`task estimate ${row.id}: invalid expected passes`);
  if (!(row.subscriptionUsdPerExpectedPass > 0)) errors.push(`task estimate ${row.id}: invalid subscription $/expected pass`);
}

const leaderSets = [
  ['codingAgentCostQualityPareto', benchmarkIds],
  ['codingAgentTimeQualityPareto', benchmarkIds],
  ['codingAgentTokenQualityPareto', benchmarkIds],
  ['modelPriceIntelligencePareto', benchmarkIds],
  ['modelSpeedIntelligencePareto', benchmarkIds],
  ['planModelValueIntelligencePareto', qualityRouteIds],
  ['planAccessPriceIntelligencePareto', qualityRouteIds],
];
for (const [key, ids] of leaderSets) {
  if (!Array.isArray(leaders[key])) errors.push(`leaders.${key}: missing array`);
  else for (const id of leaders[key]) if (!ids.has(id)) errors.push(`leaders.${key}: missing referenced id ${id}`);
}
if (leaders.subscriptionTaskEstimateCount !== taskEstimateIds.size) errors.push('leaders.subscriptionTaskEstimateCount mismatch');

const expectedStatusCounts = plans.reduce((acc, plan) => ((acc[plan.calculationStatus] = (acc[plan.calculationStatus] || 0) + 1), acc), {});
if (summary.planCount !== plans.length) errors.push(`summary.planCount ${summary.planCount} != ${plans.length}`);
if (summary.providerCount !== new Set(plans.map((plan) => plan.providerId)).size) errors.push('summary.providerCount mismatch');
if (summary.externalBenchmarkRows !== benchmarks.length) errors.push('summary.externalBenchmarkRows mismatch');
if (summary.modelRouteCount !== models.length) errors.push('summary.modelRouteCount mismatch');
if (summary.qualityRouteCount !== qualityRoutes.length) errors.push('summary.qualityRouteCount mismatch');
if (summary.subscriptionTaskEstimateCount !== taskEstimates.length) errors.push('summary.subscriptionTaskEstimateCount mismatch');
if (summary.opaqueCount !== 0) errors.push('summary.opaqueCount must be zero');
for (const [status, count] of Object.entries(expectedStatusCounts)) if (summary.statusCounts?.[status] !== count) errors.push(`summary.statusCounts.${status} mismatch`);
for (const key of ['topNormalizedValue', 'topMeasuredFrontierSubsidy']) {
  if (!planIds.has(summary[key]?.planId)) errors.push(`summary.${key}.planId does not exist: ${summary[key]?.planId}`);
}

if (schema.title !== 'Community Coding Benchmark Submission') errors.push('community schema missing or malformed');
const activeWorkflowDir = path.join(root, '.github', 'workflows');
if (fs.existsSync(activeWorkflowDir)) {
  const active = fs.readdirSync(activeWorkflowDir).filter((name) => /\.ya?ml$/i.test(name));
  if (active.length) errors.push(`active GitHub Actions workflows are forbidden for this snapshot: ${active.join(', ')}`);
}

if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log(`Validated ${plans.length} plans, ${models.length} model routes, ${benchmarks.length} external benchmark rows, ${qualityRoutes.length} quality routes, ${taskEstimates.length} task estimates, ${sources.length} sources, and zero active GitHub Actions workflows.`);
