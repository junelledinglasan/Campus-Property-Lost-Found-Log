import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function Layout() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = () => {
    signOut();
    navigate('/');
  };

  return (
    <>
      <header className="site-header">
        <div className="site-header-inner">
          <Link to="/" className="brand">
            <span className="brand-name">Lost &amp; Found Log</span>
            <span className="brand-sub">Office of Student Affairs and Services</span>
          </Link>
          <nav className="site-nav" aria-label="Main">
            <NavLink to="/" end>
              Found items
            </NavLink>
            {user ? (
              <>
                <NavLink to="/admin">OSAS desk</NavLink>
                <button type="button" className="nav-button" onClick={handleSignOut}>
                  Sign out
                </button>
              </>
            ) : (
              <NavLink to="/admin/login">OSAS staff sign in</NavLink>
            )}
          </nav>
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="site-footer">
        <p>Found something? Bring it to the OSAS office so it can be posted here.</p>
      </footer>
    </>
  );
}
