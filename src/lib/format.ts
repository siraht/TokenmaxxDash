export function number(value: unknown, maximumFractionDigits = 2): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '—';
  return new Intl.NumberFormat('en-US', { maximumFractionDigits }).format(value);
}

export function money(value: unknown, digits = 3): string {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '—';
  if (value < 0.01) return `$${value.toFixed(5)}`;
  if (value < 1) return `$${value.toFixed(digits)}`;
  return `$${value.toFixed(2)}`;
}

export function planLabel(plan: any): string {
  return `${plan.provider} ${plan.plan}`;
}

export function confidenceLabel(value: string): string {
  return ({
    official: 'Official',
    measured: 'Measured',
    'measured-low': 'Measured · low confidence',
    secondary: 'Secondary estimate',
    derived: 'Derived',
    'official-partial': 'Official · incomplete'
  } as Record<string, string>)[value] || value;
}
