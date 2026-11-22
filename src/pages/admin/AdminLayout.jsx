import { NavLink, Outlet } from 'react-router-dom';

export default function AdminLayout() {
  return (
    <section className="page">
      <h1>OSAS desk</h1>
      <nav className="tabs" aria-label="OSAS desk">
        <NavLink to="/admin/items">Found items</NavLink>
        <NavLink to="/admin/claims">Claims to check</NavLink>
        <NavLink to="/admin/history">Claim history</NavLink>
      </nav>
      <Outlet />
    </section>
  );
}
