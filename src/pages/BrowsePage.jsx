import { useMemo, useState } from 'react';
import * as api from '../api/api';
import ItemCard from '../components/ItemCard.jsx';
import Notice from '../components/Notice.jsx';
import { useLoad } from '../utils.js';

export default function BrowsePage() {
  const { data: items, loading, error } = useLoad(() => api.listItems(), []);
  const [q, setQ] = useState('');
  const [category, setCategory] = useState('');
  const [place, setPlace] = useState('');
  const [since, setSince] = useState('');
  const [showClaimed, setShowClaimed] = useState(false);

  const places = useMemo(() => [...new Set((items || []).map((i) => i.placeFound))].sort(), [items]);

  const filtered = useMemo(() => {
    const words = q.toLowerCase().split(/\s+/).filter(Boolean);
    return (items || [])
      .filter((i) => {
        if (!showClaimed && i.status === 'Claimed') return false;
        if (category && i.category !== category) return false;
        if (place && i.placeFound !== place) return false;
        if (since && i.dateFound < since) return false;
        if (words.length) {
          const text = `${i.name} ${i.description} ${i.category} ${i.placeFound}`.toLowerCase();
          if (!words.every((w) => text.includes(w))) return false;
        }
        return true;
      })
      .sort((a, b) => b.dateFound.localeCompare(a.dateFound) || b.id - a.id);
  }, [items, q, category, place, since, showClaimed]);

  const clearFilters = () => {
    setQ('');
    setCategory('');
    setPlace('');
    setSince('');
    setShowClaimed(false);
  };

  const hasFilters = q || category || place || since || showClaimed;

  return (
    <>
      <section className="hero">
        <div className="hero-inner">
          <h1>Lost something on campus? See what OSAS has found.</h1>
          <p className="lead">
            Search the items turned in to the office. If one is yours, send a claim here, then bring your school ID to
            OSAS to get it.
          </p>
          <form className="filters" role="search" onSubmit={(e) => e.preventDefault()}>
            <div className="field field-wide">
              <label htmlFor="q">Search</label>
              <input
                id="q"
                type="search"
                placeholder="Wallet, umbrella, calculator…"
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="category">Category</label>
              <select id="category" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="">All categories</option>
                {api.CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="place">Place found</label>
              <select id="place" value={place} onChange={(e) => setPlace(e.target.value)}>
                <option value="">Anywhere</option>
                {places.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="since">Found on or after</label>
              <input id="since" type="date" value={since} onChange={(e) => setSince(e.target.value)} />
            </div>
            <div className="filters-foot">
              <label className="check">
                <input type="checkbox" checked={showClaimed} onChange={(e) => setShowClaimed(e.target.checked)} />
                Include items already claimed
              </label>
              {hasFilters && (
                <button type="button" className="btn btn-quiet" onClick={clearFilters}>
                  Clear filters
                </button>
              )}
            </div>
          </form>
        </div>
      </section>

      <section className="page">
        <Notice kind="error">{error}</Notice>
        {loading && <p className="muted">Loading found items…</p>}
        {!loading && !error && (
          <>
            <p className="result-count" aria-live="polite">
              {filtered.length} {filtered.length === 1 ? 'item' : 'items'} shown
            </p>
            {filtered.length === 0 ? (
              <div className="empty">
                <h2>No items match your search</h2>
                <p>
                  Try fewer words or clear the filters. If your item is not listed, it may not have been turned in yet.
                  Check again later or ask at the OSAS office.
                </p>
              </div>
            ) : (
              <ul className="tag-grid">
                {filtered.map((item) => (
                  <li key={item.id}>
                    <ItemCard item={item} />
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </section>
    </>
  );
}
