import { Link } from 'react-router-dom';
import StatusBadge from './StatusBadge.jsx';
import { fmtDate } from '../utils.js';

export function ItemPhoto({ item, className = '' }) {
  if (item.photo) {
    return <img className={`photo ${className}`} src={item.photo} alt={item.name} />;
  }
  return (
    <div className={`photo photo-empty ${className}`} role="img" aria-label="No photo">
      <span>{item.category}</span>
    </div>
  );
}

// Hugis claim tag: may butas at pisi sa taas, parang tag sa lost property office.
export default function ItemCard({ item }) {
  return (
    <Link to={`/items/${item.id}`} className="tag">
      <div className="tag-photo">
        <ItemPhoto item={item} />
        <StatusBadge status={item.status} />
      </div>
      <div className="tag-body">
        <h3>{item.name}</h3>
        <dl className="tag-meta">
          <div>
            <dt>Place</dt>
            <dd>{item.placeFound}</dd>
          </div>
          <div>
            <dt>Found</dt>
            <dd>{fmtDate(item.dateFound)}</dd>
          </div>
        </dl>
      </div>
    </Link>
  );
}
