(() => {
  const form = document.querySelector('#community-form');
  const preview = document.querySelector('#submission-preview');
  const download = document.querySelector('#download-submission');
  let latest = null;

  const numberOrUndefined = (value) => value === '' ? undefined : Number(value);
  const clean = (object) => JSON.parse(JSON.stringify(object, (_key, value) => value === undefined || value === '' ? undefined : value));

  form?.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    latest = clean({
      schemaVersion: '1.0.0',
      submittedAt: new Date().toISOString(),
      benchmark: {
        name: data.get('benchmarkName'),
        version: data.get('benchmarkVersion'),
        taskSetSha256: data.get('taskHash'),
        harnessUrl: data.get('harnessUrl'),
        harnessCommit: data.get('harnessCommit')
      },
      plan: {
        provider: data.get('provider'),
        planName: data.get('planName'),
        planVersionObservedAt: new Date().toISOString(),
        authenticationMode: data.get('authenticationMode')
      },
      model: {
        advertisedAlias: data.get('modelAlias'),
        resolvedModelId: data.get('resolvedModel'),
        reasoningEffort: data.get('reasoningEffort')
      },
      environment: {
        os: navigator.platform || 'unknown',
        architecture: 'record in environment lock artifact'
      },
      run: {
        taskCount: Number(data.get('taskCount')),
        attemptCount: Number(data.get('attemptCount')),
        passedCount: Number(data.get('passedCount')),
        wallTimeSeconds: Number(data.get('wallTimeSeconds')),
        apiCostEquivalentUsd: numberOrUndefined(String(data.get('apiCostEquivalentUsd') || ''))
      },
      artifacts: [{
        url: data.get('artifactUrl'),
        sha256: data.get('artifactHash'),
        type: 'raw-log'
      }],
      attestations: {
        tasksUnmodified: true,
        allAttemptsIncluded: true,
        secretsRemoved: true,
        notes: data.get('notes')
      }
    });
    if (preview) preview.textContent = JSON.stringify(latest, null, 2);
    if (download) download.disabled = false;
  });

  download?.addEventListener('click', () => {
    if (!latest) return;
    const blob = new Blob([JSON.stringify(latest, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `community-benchmark-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  });
})();
