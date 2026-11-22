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
      <ItemPhoto item={item} />
      <div className="tag-body">
        <h3>{item.name}</h3>
        <p className="tag-meta">
          {item.placeFound}
          <br />
          Found {fmtDate(item.dateFound)}
        </p>
        <StatusBadge status={item.status} />
      </div>
    </Link>
  );
}
