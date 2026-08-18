(() => {
  const table = document.querySelector('[data-plan-table]');
  if (table) {
    const rows = [...table.querySelectorAll('tbody tr[data-plan-row]')];
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
      let visible = rows.filter((row) => {
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
      const body = table.querySelector('tbody');
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
      const q = (query?.value || '').toLowerCase();
      const a = agent?.value || 'all';
      rows.forEach((row) => {
        row.hidden = !((!q || row.dataset.search?.includes(q)) && (a === 'all' || row.dataset.agent === a));
      });
    };
    [query, agent].forEach((control) => control?.addEventListener('input', apply));
  }
})();
