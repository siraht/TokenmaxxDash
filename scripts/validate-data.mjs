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
const finitePositive = (value) => Number.isFinite(value) && value > 0;

const planIds = unique(plans, 'plan');
const benchmarkIds = unique(benchmarks, 'benchmark');
const sourceIds = unique(sources, 'source');
const modelIds = unique(models, 'model');
const routeIds = unique(qualityRoutes, 'quality route');
const taskIds = unique(taskEstimates, 'task estimate');
unique(candidates, 'candidate');

const validStatuses = new Set(['exact', 'derived', 'measured-range', 'partial', 'provider-hidden', 'secondary', 'unverified-candidate', 'legacy']);
const validCoverage = new Set(['direct-agent-and-model', 'direct-agent', 'direct-model', 'no-external-benchmark', 'catalog-only']);

for (const plan of plans) {
  for (const id of plan.sourceIds || []) if (!sourceIds.has(id)) errors.push(`plan ${plan.id}: missing source ${id}`);
  for (const id of plan.modelCoverageIds || []) if (!modelIds.has(id)) errors.push(`plan ${plan.id}: missing model ${id}`);
  if (!validStatuses.has(plan.calculationStatus)) errors.push(`plan ${plan.id}: unsupported status ${plan.calculationStatus}`);
  if (String(plan.valueDisplay || '').toLowerCase() === 'unresolved') errors.push(`plan ${plan.id}: unresolved display leaked into output`);
  if (plan.calculationStatus === 'provider-hidden' && plan.valueMultiple != null) errors.push(`plan ${plan.id}: provider-hidden plan has numeric multiple`);
  if (plan.valueMultiple != null && (!Number.isFinite(plan.valueMultiple) || plan.valueMultiple < 0)) errors.push(`plan ${plan.id}: invalid multiple`);
  if (plan.valueMultipleLow != null && plan.valueMultipleHigh != null && plan.valueMultipleLow > plan.valueMultipleHigh) errors.push(`plan ${plan.id}: reversed range`);
  if (plan.priceMonthly != null && plan.priceMonthly < 0) errors.push(`plan ${plan.id}: negative price`);
  if (!validCoverage.has(plan.benchmarkCoverage)) errors.push(`plan ${plan.id}: invalid benchmark coverage`);
  if ((plan.models || []).length !== (plan.modelCoverageIds || []).length) errors.push(`plan ${plan.id}: advertised model labels and coverage ids differ`);
}

for (const row of benchmarks) {
  if (!sourceIds.has(row.sourceId)) errors.push(`benchmark ${row.id}: missing source ${row.sourceId}`);
  if (!finitePositive(row.score)) errors.push(`benchmark ${row.id}: invalid score`);
  if (row.kind === 'model-intelligence' && row.blendedPricePerMUsd > 0 && !finitePositive(row.blendedUsdPerIntelligencePoint)) {
    errors.push(`benchmark ${row.id}: priced model missing $/intelligence metric`);
  }
  if (row.benchmark === 'Artificial Analysis Coding Agent Index' && row.apiCostPerTaskUsd > 0 && !finitePositive(row.apiUsdPerExpectedPass)) {
    errors.push(`benchmark ${row.id}: agent row missing $/expected pass`);
  }
}

for (const model of models) {
  if (!validCoverage.has(model.benchmarkCoverage)) errors.push(`model ${model.id}: invalid coverage`);
  for (const id of model.planIds || []) if (!planIds.has(id)) errors.push(`model ${model.id}: missing plan ${id}`);
  for (const id of model.directModelBenchmarkIds || []) if (!benchmarkIds.has(id)) errors.push(`model ${model.id}: missing model benchmark ${id}`);
  for (const id of model.directAgentBenchmarkIds || []) if (!benchmarkIds.has(id)) errors.push(`model ${model.id}: missing agent benchmark ${id}`);
  const direct = (model.directModelBenchmarkIds?.length || 0) + (model.directAgentBenchmarkIds?.length || 0) > 0;
  if (model.rankingEligible !== direct) errors.push(`model ${model.id}: ranking eligibility disagrees with direct evidence`);
  if (!direct && !model.exclusionReason) errors.push(`model ${model.id}: unbenchmarked route lacks exclusion reason`);
}

for (const route of qualityRoutes) {
  if (!planIds.has(route.planId)) errors.push(`route ${route.id}: missing plan ${route.planId}`);
  if (!modelIds.has(route.modelId)) errors.push(`route ${route.id}: missing model ${route.modelId}`);
  if (route.rankingEligible && !finitePositive(route.modelIntelligenceIndex) && !finitePositive(route.codingAgentIndex)) errors.push(`route ${route.id}: ranked without model or native-agent quality evidence`);
  if (route.nativeTaskEconomicsEligible && !route.nativeAgentBenchmarkId) errors.push(`route ${route.id}: native task eligible without benchmark`);
}

for (const row of taskEstimates) {
  if (!planIds.has(row.planId)) errors.push(`task ${row.id}: missing plan ${row.planId}`);
  if (!routeIds.has(row.routeId)) errors.push(`task ${row.id}: missing route ${row.routeId}`);
  if (!benchmarkIds.has(row.benchmarkId)) errors.push(`task ${row.id}: missing benchmark ${row.benchmarkId}`);
  for (const key of ['expectedBenchmarkPassesPerAverageMonthLow', 'expectedBenchmarkPassesPerAverageMonthHigh', 'subscriptionUsdPerExpectedPassLow', 'subscriptionUsdPerExpectedPassHigh', 'evidenceAdjustedSubscriptionUsdPerExpectedPassHigh']) {
    if (!finitePositive(row[key])) errors.push(`task ${row.id}: invalid ${key}`);
  }
  if (row.expectedBenchmarkPassesPerAverageMonthLow > row.expectedBenchmarkPassesPerAverageMonthHigh) errors.push(`task ${row.id}: reversed pass range`);
  if (row.subscriptionUsdPerExpectedPassLow > row.subscriptionUsdPerExpectedPassHigh) errors.push(`task ${row.id}: reversed cost range`);
}

const fableModel = models.find((row) => row.name === 'Claude Fable 5');
if (!fableModel) errors.push('Claude Fable 5 model route missing');
else {
  if (fableModel.benchmarkCoverage !== 'direct-agent-and-model') errors.push('Fable 5 lacks direct model + agent evidence');
  if (!finitePositive(fableModel.bestModelIntelligenceScore) || !finitePositive(fableModel.bestCodingAgentScore)) errors.push('Fable 5 direct scores missing');
}
for (const id of ['aa-model-claude-fable-5-max', 'aa-agent-claude-code-fable-5-max-fallback', 'terminal-bench-2-1-claude-code-fable-5-xhigh']) {
  if (!benchmarkIds.has(id)) errors.push(`Fable benchmark row missing: ${id}`);
}

const claudePlanIds = ['claude-code-pro', 'claude-code-max-5x', 'claude-code-max-20x'];
for (const id of claudePlanIds) {
  const plan = plans.find((row) => row.id === id);
  if (!plan) { errors.push(`Claude plan missing: ${id}`); continue; }
  for (const key of ['weeklyRawTokensBillionLow', 'weeklyRawTokensBillionHigh', 'subscriptionUsdPerMillionRawTokensLow', 'subscriptionUsdPerMillionRawTokensHigh', 'averageMonthlyApiEquivalentUsdLow', 'averageMonthlyApiEquivalentUsdHigh']) {
    if (!finitePositive(plan.quotas?.[key])) errors.push(`${id}: missing ${key}`);
  }
  const categories = plan.details?.modelCategoryTokenEconomics;
  if (!Array.isArray(categories) || categories.length !== 20) errors.push(`${id}: expected 20 Claude model/category rows`);
  if (!Array.isArray(plan.details?.modelAccess) || plan.details.modelAccess.length !== 4) errors.push(`${id}: model access table incomplete`);
}
const claudePro = plans.find((row) => row.id === 'claude-code-pro');
const max5 = plans.find((row) => row.id === 'claude-code-max-5x');
const max20 = plans.find((row) => row.id === 'claude-code-max-20x');
const access = (plan, model) => plan?.details?.modelAccess?.find((row) => row.model === model);
if (access(claudePro, 'Claude Fable 5')?.accessMode !== 'payg-only') errors.push('Claude Pro Fable must be PAYG-only');
for (const plan of [max5, max20]) {
  const row = access(plan, 'Claude Fable 5');
  if (row?.accessMode !== 'included-capped' || row?.weeklyMeterShareMaxPct !== 50) errors.push(`${plan?.id}: Fable must be included-capped at 50%`);
}
if (taskEstimates.filter((row) => row.model === 'Claude Fable 5').length !== 2) errors.push('Expected exactly two included Fable task estimates on Max tiers');
if (taskEstimates.some((row) => row.planId === 'claude-code-pro' && row.model === 'Claude Fable 5')) errors.push('Claude Pro must not receive included Fable task estimate');

const leaderArrays = [
  ['codingAgentCostQualityPareto', benchmarkIds],
  ['codingAgentTimeQualityPareto', benchmarkIds],
  ['codingAgentTokenQualityPareto', benchmarkIds],
  ['modelPriceIntelligencePareto', benchmarkIds],
  ['modelSpeedIntelligencePareto', benchmarkIds],
  ['planModelValueIntelligencePareto', routeIds],
  ['planAccessPriceIntelligencePareto', routeIds]
];
for (const [key, allowed] of leaderArrays) {
  if (!Array.isArray(leaders[key])) errors.push(`leaders.${key}: missing array`);
  else for (const id of leaders[key]) if (!allowed.has(id)) errors.push(`leaders.${key}: bad id ${id}`);
}
for (const collection of ['subscriptionTaskParetoByQualityFloor', 'subscriptionTaskBudgetParetoByQualityFloor']) {
  for (const [band, ids] of Object.entries(leaders[collection] || {})) {
    if (!Array.isArray(ids)) errors.push(`leaders.${collection}.${band}: not array`);
    else for (const id of ids) if (!taskIds.has(id)) errors.push(`leaders.${collection}.${band}: bad id ${id}`);
  }
}
if (!leaders.subscriptionTaskProviderParetoByQualityFloor?.frontier?.['Anthropic Claude Code']) errors.push('Claude provider-specific frontier missing');
if (!leaders.subscriptionTaskProviderParetoByQualityFloor?.frontier?.['OpenAI Codex']) errors.push('Codex provider-specific frontier missing');

if (summary.planCount !== plans.length) errors.push('summary plan count mismatch');
if (summary.providerCount !== new Set(plans.map((plan) => plan.providerId)).size) errors.push('summary provider count mismatch');
if (summary.externalBenchmarkRows !== benchmarks.length) errors.push('summary benchmark count mismatch');
if (summary.modelRouteCount !== models.length) errors.push('summary model count mismatch');
if (summary.qualityRouteCount !== qualityRoutes.length) errors.push('summary quality route count mismatch');
if (summary.subscriptionTaskEstimateCount !== taskEstimates.length) errors.push('summary task estimate count mismatch');
if (summary.fableBenchmarkRowCount < 4 || summary.fableSubscriptionRouteCount !== 3) errors.push('summary Fable coverage mismatch');
if (summary.defaultQualityFloor !== 60) errors.push('default quality floor must be 60');
if (schema.title !== 'Community Coding Benchmark Submission') errors.push('community schema malformed');

const activeWorkflowDir = path.join(root, '.github', 'workflows');
if (fs.existsSync(activeWorkflowDir)) {
  const active = fs.readdirSync(activeWorkflowDir).filter((name) => /\.ya?ml$/i.test(name));
  if (active.length) errors.push(`active GitHub Actions workflows forbidden: ${active.join(', ')}`);
}

for (const name of ['plans.json', 'benchmarks.json', 'sources.json', 'summary.json', 'models.json', 'quality-routes.json', 'subscription-task-estimates.json', 'leaders.json']) {
  const src = fs.readFileSync(path.join(root, 'src', 'data', name));
  const pubPath = path.join(root, 'public', 'data', name);
  if (!fs.existsSync(pubPath)) errors.push(`public data copy missing: ${name}`);
  else if (!src.equals(fs.readFileSync(pubPath))) errors.push(`public data copy differs: ${name}`);
}

if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log(`Validated ${plans.length} plans, ${models.length} model labels, ${benchmarks.length} external benchmark rows, ${qualityRoutes.length} routes, ${taskEstimates.length} native task estimates, Claude token economics, Fable access, and zero active GitHub Actions workflows.`);
