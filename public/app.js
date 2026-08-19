(() => {
  const buyerTable = document.querySelector('[data-buyer-table]');
  if (buyerTable) {
    const rows = [...buyerTable.querySelectorAll('[data-buyer-row]')];
    const search = document.querySelector('[data-buyer-search]');
    const mix = document.querySelector('[data-buyer-mix]');
    const quality = document.querySelector('[data-buyer-quality]');
    const budget = document.querySelector('[data-buyer-budget]');
    const evidence = document.querySelector('[data-buyer-evidence]');
    const sort = document.querySelector('[data-buyer-sort]');
    const hideOwned = document.querySelector('[data-buyer-owned]');
    const count = document.querySelector('[data-buyer-count]');
    const empty = document.querySelector('[data-buyer-empty]');
    const body = buyerTable.querySelector('tbody');
    const metric = (row, key, mixId, fallback = 999999) => {
      const value = Number(row.dataset[`${mixId}${key}`]);
      return Number.isFinite(value) ? value : fallback;
    };
    const updateVisibleMetricText = (row, mixId) => {
      row.querySelectorAll('[data-metric-standard]').forEach((element) => {
        element.textContent = element.getAttribute(`data-metric-${mixId}`) || '—';
      });
    };
    const applyBuyer = () => {
      const query = (search?.value || '').trim().toLowerCase();
      const mixId = mix?.value || 'standard';
      const minimumQuality = Number(quality?.value || 0);
      const maximumPrice = Number(budget?.value || 10000);
      const evidenceMode = evidence?.value || 'all';
      const shouldHideOwned = Boolean(hideOwned?.checked);
      const sortBy = sort?.value || 'quality-cost';
      const visible = rows.filter((row) => {
        const confidence = row.dataset.confidence || '';
        const primary = ['official', 'derived', 'official-partial', 'measured', 'measured-low'].includes(confidence);
        const matchesEvidence = evidenceMode === 'all' || (evidenceMode === 'official' ? confidence === 'official' : primary);
        return (!query || row.dataset.search?.includes(query))
          && Number(row.dataset.intelligence || -1) >= minimumQuality
          && Number(row.dataset.price || 999999) <= maximumPrice
          && (!shouldHideOwned || row.dataset.owned !== 'true')
          && matchesEvidence;
      });
      visible.sort((a, b) => {
        if (sortBy === 'intelligence') return Number(b.dataset.intelligence || -1) - Number(a.dataset.intelligence || -1);
        if (sortBy === 'coding') return Number(b.dataset.coding || -1) - Number(a.dataset.coding || -1);
        if (sortBy === 'route-rate') return metric(a, 'Rate', mixId) - metric(b, 'Rate', mixId);
        if (sortBy === 'tokens') return metric(b, 'Tokens', mixId, -1) - metric(a, 'Tokens', mixId, -1);
        if (sortBy === 'token-cost') return metric(a, 'Cost', mixId) - metric(b, 'Cost', mixId);
        if (sortBy === 'task-cost') return metric(a, 'TaskCost', mixId) - metric(b, 'TaskCost', mixId);
        if (sortBy === 'price') return Number(a.dataset.price || 999999) - Number(b.dataset.price || 999999);
        return metric(a, 'QualityCost', mixId) - metric(b, 'QualityCost', mixId);
      });
      rows.forEach((row) => { row.hidden = true; });
      visible.forEach((row, index) => {
        row.hidden = false;
        updateVisibleMetricText(row, mixId);
        const rank = row.querySelector('[data-row-rank]');
        if (rank) rank.textContent = String(index + 1);
        body?.appendChild(row);
      });
      if (count) count.textContent = `${visible.length} of ${rows.length} comparable subscription/model routes`;
      empty?.classList.toggle('is-visible', visible.length === 0);
    };
    [search, mix, quality, budget, evidence, sort, hideOwned].forEach((control) => {
      control?.addEventListener('input', applyBuyer);
      control?.addEventListener('change', applyBuyer);
    });
    applyBuyer();
  }

  const planGrid = document.querySelector('[data-plan-grid]');
  if (planGrid) {
    const cards = [...planGrid.querySelectorAll('[data-plan-card]')];
    const search = document.querySelector('[data-plan-search]');
    const provider = document.querySelector('[data-plan-provider]');
    const evidence = document.querySelector('[data-plan-evidence]');
    const quantified = document.querySelector('[data-plan-quantified]');
    const sort = document.querySelector('[data-plan-sort]');
    const count = document.querySelector('[data-plan-count]');
    const empty = document.querySelector('[data-plan-empty]');
    const applyPlans = () => {
      const query = (search?.value || '').trim().toLowerCase();
      const providerValue = provider?.value || 'all';
      const evidenceValue = evidence?.value || 'all';
      const quantifiedValue = quantified?.value || 'all';
      const sortValue = sort?.value || 'provider';
      const primary = new Set(['official', 'derived', 'official-partial', 'measured', 'measured-low']);
      const visible = cards.filter((card) => {
        const confidence = card.dataset.confidence || '';
        const evidenceMatch = evidenceValue === 'all'
          || (evidenceValue === 'official' && confidence === 'official')
          || (evidenceValue === 'primary' && primary.has(confidence))
          || (evidenceValue === 'secondary' && !primary.has(confidence));
        return (!query || card.dataset.search?.includes(query))
          && (providerValue === 'all' || card.dataset.provider === providerValue)
          && (quantifiedValue === 'all' || card.dataset.quantified === quantifiedValue)
          && evidenceMatch;
      });
      visible.sort((a, b) => {
        if (sortValue === 'price') return Number(a.dataset.price) - Number(b.dataset.price);
        if (sortValue === 'quality-cost') return Number(a.dataset.qualityCost) - Number(b.dataset.qualityCost);
        return (a.dataset.provider || '').localeCompare(b.dataset.provider || '') || Number(a.dataset.price) - Number(b.dataset.price);
      });
      cards.forEach((card) => { card.hidden = true; });
      visible.forEach((card) => { card.hidden = false; planGrid.appendChild(card); });
      if (count) count.textContent = `${visible.length} of ${cards.length} plans`;
      empty?.classList.toggle('is-visible', visible.length === 0);
    };
    [search, provider, evidence, quantified, sort].forEach((control) => {
      control?.addEventListener('input', applyPlans);
      control?.addEventListener('change', applyPlans);
    });
    applyPlans();
  }
})();
