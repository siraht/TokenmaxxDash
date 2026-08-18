export function formatNumber(value: unknown, maximumFractionDigits = 2): string {
  if (typeof value !== 'number') return String(value ?? '—');
  return new Intl.NumberFormat('en-US', { maximumFractionDigits }).format(value);
}

export function titleCaseKey(value: string): string {
  return value
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/Usd/g, 'USD')
    .replace(/Api/g, 'API')
    .replace(/Mcp/g, 'MCP')
    .replace(/^./, (char) => char.toUpperCase());
}

export function valueText(plan: any): string {
  return plan.valueDisplay || 'Provider-hidden limit';
}

export function statusLabel(value: string): string {
  return ({
    exact: 'Official exact',
    derived: 'Evidence-derived',
    'measured-range': 'Measured range',
    partial: 'Partially normalized',
    'provider-hidden': 'Provider-hidden',
    secondary: 'Secondary-source',
    'unverified-candidate': 'Unverified candidate',
    legacy: 'Legacy'
  } as Record<string, string>)[value] || value;
}

export function sourceMap(sources: any[]): Map<string, any> {
  return new Map(sources.map((source) => [source.id, source]));
}
