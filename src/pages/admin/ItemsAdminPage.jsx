import { useState } from 'react';
import { Link } from 'react-router-dom';
import * as api from '../../api/api';
import Modal from '../../components/Modal.jsx';
import Notice from '../../components/Notice.jsx';
import PhotoInput from '../../components/PhotoInput.jsx';
import StatusBadge from '../../components/StatusBadge.jsx';
import { fmtDate, today, useFlash, useLoad } from '../../utils.js';

export default function ItemsAdminPage() {
  const { data: items, loading, error, reload } = useLoad(() => api.listItems(), []);
  const [editing, setEditing] = useState(null); // null = sarado, {} = bago, item = i-edit
  const [flash, setFlash] = useFlash();
  const [actionError, setActionError] = useState('');

  const places = [...new Set((items || []).map((i) => i.placeFound))].sort();
  const sorted = [...(items || [])].sort((a, b) => b.dateFound.localeCompare(a.dateFound) || b.id - a.id);

  const handleSaved = (message) => {
    setEditing(null);
    setFlash(message);
    reload();
  };

  const handleDelete = async (item) => {
    const warning =
      item.status === 'Pending'
        ? `"${item.name}" has a claim waiting for review. Deleting it also deletes that claim. Delete anyway?`
        : `Delete "${item.name}"? This also deletes its claim records.`;
    if (!window.confirm(warning)) return;
    setActionError('');
    try {
      await api.deleteItem(item.id);
      setFlash('Item deleted');
      reload();
    } catch (err) {
      setActionError(err.message);
    }
  };

  return (
    <>
      <div className="toolbar">
        <p className="muted">Post every item that is turned in to the office, so owners can find it.</p>
        <button type="button" className="btn btn-primary" onClick={() => setEditing({})}>
          Post found item
        </button>
      </div>
      <Notice kind="success">{flash}</Notice>
      <Notice kind="error">{error || actionError}</Notice>
      {loading && <p className="muted">Loading items…</p>}
      {!loading && sorted.length === 0 && (
        <div className="empty">
          <h2>No items posted yet</h2>
          <p>Select Post found item to add the first one.</p>
        </div>
      )}
      {sorted.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Item</th>
                <th scope="col">Category</th>
                <th scope="col">Place found</th>
                <th scope="col">Date found</th>
                <th scope="col">Status</th>
                <th scope="col">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((item) => (
                <tr key={item.id}>
                  <td>
                    <div className="cell-item">
                      {item.photo ? (
                        <img className="thumb" src={item.photo} alt="" />
                      ) : (
                        <span className="thumb thumb-empty" aria-hidden="true" />
                      )}
                      <Link to={`/items/${item.id}`}>{item.name}</Link>
                    </div>
                  </td>
                  <td>{item.category}</td>
                  <td>{item.placeFound}</td>
                  <td>{fmtDate(item.dateFound)}</td>
                  <td>
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="actions">
                    <button type="button" className="btn btn-quiet" onClick={() => setEditing(item)}>
                      Edit
                    </button>
                    <button type="button" className="btn btn-danger-quiet" onClick={() => handleDelete(item)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {editing && (
        <ItemFormModal
          item={editing}
          places={places}
          onClose={() => setEditing(null)}
          onSaved={handleSaved}
        />
      )}
    </>
  );
}

function ItemFormModal({ item, places, onClose, onSaved }) {
  const isNew = !item.id;
  const [form, setForm] = useState({
    name: item.name || '',
    category: item.category || api.CATEGORIES[0],
    description: item.description || '',
    photo: item.photo || null,
    dateFound: item.dateFound || today(),
    placeFound: item.placeFound || '',
  });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      if (isNew) {
        await api.createItem(form);
        onSaved('Item posted');
      } else {
        await api.updateItem(item.id, form);
        onSaved('Changes saved');
      }
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  return (
    <Modal title={isNew ? 'Post found item' : 'Edit item'} onClose={onClose}>
      <form onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="f-name">Item name</label>
          <input id="f-name" value={form.name} onChange={set('name')} required />
        </div>
        <div className="field">
          <label htmlFor="f-category">Category</label>
          <select id="f-category" value={form.category} onChange={set('category')}>
            {api.CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="f-desc">Description</label>
          <p className="hint">Describe it so the owner can recognize it, but keep one detail back to check against their claim.</p>
          <textarea id="f-desc" rows="3" value={form.description} onChange={set('description')} />
        </div>
        <div className="grid-2">
          <div className="field">
            <label htmlFor="f-date">Date found</label>
            <input id="f-date" type="date" max={today()} value={form.dateFound} onChange={set('dateFound')} required />
          </div>
          <div className="field">
            <label htmlFor="f-place">Place found</label>
            <input id="f-place" list="places" value={form.placeFound} onChange={set('placeFound')} required />
            <datalist id="places">
              {places.map((p) => (
                <option key={p} value={p} />
              ))}
            </datalist>
          </div>
        </div>
        <PhotoInput label="Photo" value={form.photo} onChange={(photo) => setForm((f) => ({ ...f, photo }))} />
        <Notice kind="error">{error}</Notice>
        <div className="modal-actions">
          <button type="button" className="btn btn-quiet" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={busy}>
            {busy ? 'Saving…' : isNew ? 'Post item' : 'Save changes'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
