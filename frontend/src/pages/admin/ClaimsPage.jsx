import { useState } from 'react';
import * as api from '../../api/api';
import Modal from '../../components/Modal.jsx';
import Notice from '../../components/Notice.jsx';
import PhotoInput from '../../components/PhotoInput.jsx';
import { fmtDateTime, useFlash, useLoad } from '../../utils.js';

export default function ClaimsPage() {
  const { data: claims, loading, error, reload } = useLoad(() => api.listClaims(), []);
  const [reviewing, setReviewing] = useState(null);
  const [flash, setFlash] = useFlash();

  const pending = (claims || []).filter((c) => c.status === 'Pending');

  const handleDecided = (message) => {
    setReviewing(null);
    setFlash(message);
    reload();
  };

  return (
    <>
      <p className="muted">
        A student sends a claim online, then comes to the office. Check their school ID against the details below
        before you release the item.
      </p>
      <Notice kind="success">{flash}</Notice>
      <Notice kind="error">{error}</Notice>
      {loading && <p className="muted">Loading claims…</p>}
      {!loading && !error && pending.length === 0 && (
        <div className="empty">
          <h2>No claims waiting</h2>
          <p>New claims from students show up here.</p>
        </div>
      )}
      {pending.length > 0 && (
        <ul className="claim-list">
          {pending.map((c) => (
            <li key={c.id} className="claim-row">
              <div>
                <h2 className="claim-item">{c.itemName}</h2>
                <p>
                  <strong>{c.fullName}</strong>, student number {c.studentNo}
                </p>
                <p className="muted">Sent {fmtDateTime(c.submittedAt)}</p>
              </div>
              <button type="button" className="btn btn-primary" onClick={() => setReviewing(c)}>
                Check claim
              </button>
            </li>
          ))}
        </ul>
      )}
      {reviewing && <ReviewModal claim={reviewing} onClose={() => setReviewing(null)} onDecided={handleDecided} />}
    </>
  );
}

const same = (a, b) => a.trim().replace(/\s+/g, ' ').toLowerCase() === b.trim().replace(/\s+/g, ' ').toLowerCase();

function ReviewModal({ claim, onClose, onDecided }) {
  const [verifiedName, setVerifiedName] = useState(claim.fullName);
  const [verifiedStudentNo, setVerifiedStudentNo] = useState(claim.studentNo);
  const [handoverPhoto, setHandoverPhoto] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const differs = !same(verifiedName, claim.fullName) || !same(verifiedStudentNo, claim.studentNo);

  const decide = async (decision) => {
    setError('');
    setBusy(true);
    try {
      await api.decideClaim(claim.id, { decision, verifiedName, verifiedStudentNo, handoverPhoto });
      onDecided(decision === 'Approved' ? 'Claim approved. The item is now marked as claimed.' : 'Claim rejected. The item is available again.');
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  return (
    <Modal title={`Check claim: ${claim.itemName}`} onClose={onClose}>
      <div className="compare">
        <h3>Submitted online</h3>
        <p>
          {claim.fullName}, {claim.studentNo}
        </p>
      </div>
      <div className="field">
        <label htmlFor="v-name">Full name on the ID</label>
        <input id="v-name" value={verifiedName} onChange={(e) => setVerifiedName(e.target.value)} />
      </div>
      <div className="field">
        <label htmlFor="v-no">Student number on the ID</label>
        <input id="v-no" value={verifiedStudentNo} onChange={(e) => setVerifiedStudentNo(e.target.value)} />
      </div>
      {differs && (
        <Notice kind="warning">The ID details differ from what was submitted. Check the ID again before approving.</Notice>
      )}
      <PhotoInput
        label="Handover photo"
        hint="Take a photo of the person receiving the item. It is saved in the claim history."
        value={handoverPhoto}
        onChange={setHandoverPhoto}
      />
      <Notice kind="error">{error}</Notice>
      <div className="modal-actions">
        <button type="button" className="btn btn-danger-quiet" disabled={busy} onClick={() => decide('Rejected')}>
          Reject claim
        </button>
        <button type="button" className="btn btn-primary" disabled={busy} onClick={() => decide('Approved')}>
          Approve and release item
        </button>
      </div>
    </Modal>
  );
}
