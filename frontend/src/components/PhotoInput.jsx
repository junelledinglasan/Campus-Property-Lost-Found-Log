import { useId, useState } from 'react';
import { fileToDataUrl } from '../utils.js';

export default function PhotoInput({ label, value, onChange, hint }) {
  const id = useId();
  const [error, setError] = useState('');

  const handleFile = async (e) => {
    const file = e.target.files && e.target.files[0];
    e.target.value = '';
    if (!file) return;
    try {
      setError('');
      onChange(await fileToDataUrl(file));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {hint && <p className="hint">{hint}</p>}
      {value && <img className="photo-preview" src={value} alt="Selected" />}
      <div className="row">
        <input id={id} type="file" accept="image/*" capture="environment" onChange={handleFile} />
        {value && (
          <button type="button" className="btn btn-quiet" onClick={() => onChange(null)}>
            Remove photo
          </button>
        )}
      </div>
      {error && (
        <p className="field-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
