import { useCallback, useEffect, useState } from 'react';

export const fmtDate = (iso) =>
  iso
    ? new Date(iso.length === 10 ? iso + 'T00:00:00' : iso).toLocaleDateString('en-PH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : '';

export const fmtDateTime = (iso) =>
  iso
    ? new Date(iso).toLocaleString('en-PH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
      })
    : '';

export const today = () => new Date().toISOString().slice(0, 10);

// Binabawasan ang laki ng larawan para magkasya sa browser storage.
export function fileToDataUrl(file, max = 800, quality = 0.72) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, max / Math.max(img.width, img.height));
      const canvas = document.createElement('canvas');
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      resolve(canvas.toDataURL('image/jpeg', quality));
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('That file is not an image the browser can read.'));
    };
    img.src = url;
  });
}

// Simpleng loader: tinatawag ang fn at ibinabalik ang data, loading, error, at reload.
export function useLoad(fn, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: '' });
  const run = useCallback(() => {
    setState((s) => ({ ...s, loading: true, error: '' }));
    fn()
      .then((data) => setState({ data, loading: false, error: '' }))
      .catch((e) => setState({ data: null, loading: false, error: e.message }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(run, [run]);
  return { ...state, reload: run };
}

// Mensaheng lumalabas sandali pagkatapos ng isang aksyon.
export function useFlash() {
  const [message, setMessage] = useState('');
  useEffect(() => {
    if (!message) return undefined;
    const t = setTimeout(() => setMessage(''), 5000);
    return () => clearTimeout(t);
  }, [message]);
  return [message, setMessage];
}
