import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import * as api from '../api/api';
import { ItemPhoto } from '../components/ItemCard.jsx';
import Notice from '../components/Notice.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import { fmtDate, useLoad } from '../utils.js';

export default function ItemDetailPage() {
  const { id } = useParams();
  const { data: item, loading, error, reload } = useLoad(() => api.getItem(id), [id]);

  if (loading && !item) {
    return (
      <section className="page narrow">
        <p className="muted">Loading item…</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="page narrow">
        <Notice kind="error">{error}</Notice>
        <p>
          <Link to="/">Back to found items</Link>
        </p>
      </section>
    );
  }

  return (
    <section className="page">
      <p>
        <Link to="/">← All found items</Link>
      </p>
      <div className="detail">
        <ItemPhoto item={item} className="detail-photo" />
        <div className="detail-main">
          <StatusBadge status={item.status} />
          <h1>{item.name}</h1>
          <dl className="facts">
            <div>
              <dt>Category</dt>
              <dd>{item.category}</dd>
            </div>
            <div>
              <dt>Place found</dt>
              <dd>{item.placeFound}</dd>
            </div>
            <div>
              <dt>Date found</dt>
              <dd>{fmtDate(item.dateFound)}</dd>
            </div>
          </dl>
          {item.description && <p className="description">{item.description}</p>}
          <ClaimPanel item={item} onClaimed={reload} />
        </div>
      </div>
    </section>
  );
}

function ClaimPanel({ item, onClaimed }) {
  const [fullName, setFullName] = useState('');
  const [studentNo, setStudentNo] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);

  if (sent) {
    return (
      <div className="panel panel-success">
        <h2>Claim submitted</h2>
        <p>
          Go to the OSAS office and show your school ID. OSAS will check it against the name and student number you
          entered before releasing the item.
        </p>
      </div>
    );
  }

  if (item.status === 'Pending') {
    return (
      <div className="panel">
        <h2>A claim is being checked</h2>
        <p>Someone has already claimed this item. OSAS is verifying it. If you are the real owner, tell the OSAS staff.</p>
      </div>
    );
  }

  if (item.status === 'Claimed') {
    return (
      <div className="panel">
        <h2>Already returned</h2>
        <p>This item was returned to its owner.</p>
      </div>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await api.submitClaim({ itemId: item.id, fullName, studentNo });
      setSent(true);
      onClaimed();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="panel" onSubmit={handleSubmit} noValidate>
      <h2>Is this yours?</h2>
      <p>
        Enter your details exactly as they appear on your school ID. You do not need an account or a photo. OSAS checks
        your ID when you pick the item up.
      </p>
      <div className="field">
        <label htmlFor="fullName">Full name</label>
        <input
          id="fullName"
          autoComplete="name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />
      </div>
      <div className="field">
        <label htmlFor="studentNo">Student number</label>
        <input id="studentNo" value={studentNo} onChange={(e) => setStudentNo(e.target.value)} required />
      </div>
      <Notice kind="error">{error}</Notice>
      <button type="submit" className="btn btn-primary" disabled={submitting}>
        {submitting ? 'Submitting…' : 'Submit claim'}
      </button>
    </form>
  );
}
