import { useMemo, useState } from 'react';
import * as api from '../../api/api';
import Modal from '../../components/Modal.jsx';
import Notice from '../../components/Notice.jsx';
import { fmtDateTime, useLoad } from '../../utils.js';

export default function HistoryPage() {
  const { data: claims, loading, error } = useLoad(() => api.listClaims(), []);
  const [q, setQ] = useState('');
  const [photo, setPhoto] = useState(null);

  const decided = useMemo(() => {
    const words = q.toLowerCase().split(/\s+/).filter(Boolean);
    return (claims || [])
      .filter((c) => c.status !== 'Pending')
      .filter((c) => {
        if (!words.length) return true;
        const text = `${c.itemName} ${c.verifiedName} ${c.verifiedStudentNo}`.toLowerCase();
        return words.every((w) => text.includes(w));
      })
      .sort((a, b) => b.decidedAt.localeCompare(a.decidedAt));
  }, [claims, q]);

  return (
    <>
      <div className="toolbar">
        <p className="muted">Every decided claim, with the details OSAS checked on the ID.</p>
        <div className="field toolbar-search">
          <label htmlFor="h-q">Search history</label>
          <input id="h-q" type="search" placeholder="Name, student number, or item" value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
      </div>
      <Notice kind="error">{error}</Notice>
      {loading && <p className="muted">Loading history…</p>}
      {!loading && !error && decided.length === 0 && (
        <div className="empty">
          <h2>{q ? 'No records match your search' : 'No decided claims yet'}</h2>
          <p>{q ? 'Try a different name, student number, or item.' : 'Approved and rejected claims are listed here.'}</p>
        </div>
      )}
      {decided.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Decided</th>
                <th scope="col">Item</th>
                <th scope="col">Name on ID</th>
                <th scope="col">Student number</th>
                <th scope="col">Decision</th>
                <th scope="col">Handover photo</th>
              </tr>
            </thead>
            <tbody>
              {decided.map((c) => (
                <tr key={c.id}>
                  <td>{fmtDateTime(c.decidedAt)}</td>
                  <td>{c.itemName}</td>
                  <td>{c.verifiedName}</td>
                  <td>{c.verifiedStudentNo}</td>
                  <td>
                    <span className={`status status-${c.status === 'Approved' ? 'claimed' : 'rejected'}`}>{c.status}</span>
                  </td>
                  <td>
                    {c.handoverPhoto ? (
                      <button type="button" className="thumb-button" onClick={() => setPhoto(c)} aria-label={`Open handover photo for ${c.itemName}`}>
                        <img className="thumb" src={c.handoverPhoto} alt="" />
                      </button>
                    ) : (
                      <span className="muted">None</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {photo && (
        <Modal title={`Handover: ${photo.itemName}`} onClose={() => setPhoto(null)}>
          <img className="photo-large" src={photo.handoverPhoto} alt={`Handover of ${photo.itemName}`} />
          <p>
            Released to {photo.verifiedName} ({photo.verifiedStudentNo}) on {fmtDateTime(photo.decidedAt)} by {photo.decidedBy}.
          </p>
        </Modal>
      )}
    </>
  );
}
