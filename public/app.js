(() => {
  const planTable = document.querySelector('[data-plan-table]');
  if (planTable) {
    const rows = [...planTable.querySelectorAll('tbody tr[data-plan-row]')];
    const search = document.querySelector('[data-filter-search]');
    const status = document.querySelector('[data-filter-status]');
    const provider = document.querySelector('[data-filter-provider]');
    const sort = document.querySelector('[data-sort-plans]');
    const count = document.querySelector('[data-results-count]');
    const empty = document.querySelector('[data-empty-state]');

    const apply = () => {
      const query = (search?.value || '').trim().toLowerCase();
      const statusValue = status?.value || 'all';
      const providerValue = provider?.value || 'all';
      const visible = rows.filter((row) => {
        const matchesQuery = !query || row.dataset.search?.includes(query);
        const matchesStatus = statusValue === 'all' || row.dataset.status === statusValue;
        const matchesProvider = providerValue === 'all' || row.dataset.provider === providerValue;
        return matchesQuery && matchesStatus && matchesProvider;
      });

      const sortValue = sort?.value || 'value-desc';
      visible.sort((a, b) => {
        const av = Number(a.dataset.value || '-1');
        const bv = Number(b.dataset.value || '-1');
        const ap = Number(a.dataset.price || '999999');
        const bp = Number(b.dataset.price || '999999');
        if (sortValue === 'price-asc') return ap - bp;
        if (sortValue === 'price-desc') return bp - ap;
        if (sortValue === 'provider') return (a.dataset.provider || '').localeCompare(b.dataset.provider || '');
        return bv - av;
      });

      rows.forEach((row) => { row.hidden = true; });
      const body = planTable.querySelector('tbody');
      visible.forEach((row) => { row.hidden = false; body?.appendChild(row); });
      if (count) count.textContent = `${visible.length} of ${rows.length} plan tiers`;
      empty?.classList.toggle('is-visible', visible.length === 0);
    };
    [search, status, provider, sort].forEach((control) => control?.addEventListener('input', apply));
    apply();
  }

  const benchmarkTable = document.querySelector('[data-benchmark-table]');
  if (benchmarkTable) {
    const rows = [...benchmarkTable.querySelectorAll('tbody tr[data-benchmark-row]')];
    const query = document.querySelector('[data-benchmark-search]');
    const agent = document.querySelector('[data-benchmark-agent]');
    const apply = () => {
      const q = (query?.value || '').trim().toLowerCase();
      const a = agent?.value || 'all';
      rows.forEach((row) => {
        row.hidden = !((!q || row.dataset.search?.includes(q)) && (a === 'all' || row.dataset.agent === a));
      });
    };
    [query, agent].forEach((control) => control?.addEventListener('input', apply));
    apply();
  }

  const modelTable = document.querySelector('[data-model-table]');
  if (modelTable) {
    const rows = [...modelTable.querySelectorAll('tbody tr[data-model-row]')];
    const search = document.querySelector('[data-model-search]');
    const coverage = document.querySelector('[data-model-coverage]');
    const provider = document.querySelector('[data-model-provider]');
    const sort = document.querySelector('[data-model-sort]');
    const count = document.querySelector('[data-model-results-count]');
    const empty = document.querySelector('[data-model-empty]');

    const apply = () => {
      const q = (search?.value || '').trim().toLowerCase();
      const coverageValue = coverage?.value || 'all';
      const providerValue = provider?.value || 'all';
      const visible = rows.filter((row) => {
        const coverageMatch = coverageValue === 'all'
          || (coverageValue === 'ranked' && row.dataset.ranked === 'true')
          || row.dataset.coverage === coverageValue;
        const providerMatch = providerValue === 'all' || (row.dataset.providers || '').split('|').includes(providerValue);
        return (!q || row.dataset.search?.includes(q)) && coverageMatch && providerMatch;
      });

      const sortValue = sort?.value || 'intelligence-desc';
      visible.sort((a, b) => {
        if (sortValue === 'price-density') return Number(a.dataset.density || 999999) - Number(b.dataset.density || 999999);
        if (sortValue === 'speed-desc') return Number(b.dataset.speed || -1) - Number(a.dataset.speed || -1);
        if (sortValue === 'name') return (a.dataset.name || '').localeCompare(b.dataset.name || '');
        return Number(b.dataset.intelligence || -1) - Number(a.dataset.intelligence || -1);
      });

      rows.forEach((row) => { row.hidden = true; });
      const body = modelTable.querySelector('tbody');
      visible.forEach((row) => { row.hidden = false; body?.appendChild(row); });
      if (count) count.textContent = `${visible.length} of ${rows.length} model labels`;
      empty?.classList.toggle('is-visible', visible.length === 0);
    };
    [search, coverage, provider, sort].forEach((control) => control?.addEventListener('input', apply));
    apply();
  }
})();
