import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function Layout() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [installEvent, setInstallEvent] = useState(null);

  // PWA: ipapakita lang ang "Install app" kapag pwedeng i-install ng browser.
  useEffect(() => {
    const onPrompt = (e) => {
      e.preventDefault();
      setInstallEvent(e);
    };
    const onInstalled = () => setInstallEvent(null);
    window.addEventListener('beforeinstallprompt', onPrompt);
    window.addEventListener('appinstalled', onInstalled);
    return () => {
      window.removeEventListener('beforeinstallprompt', onPrompt);
      window.removeEventListener('appinstalled', onInstalled);
    };
  }, []);

  const handleInstall = async () => {
    if (!installEvent) return;
    installEvent.prompt();
    await installEvent.userChoice;
    setInstallEvent(null);
  };

  const handleSignOut = () => {
    signOut();
    navigate('/');
  };

  return (
    <div className="shell">
      <header className="site-header">
        <div className="site-header-inner">
          <Link to="/" className="brand">
            <img className="brand-logo" src="/logo.png" alt="" width="48" height="48" />
            <span className="brand-text">
              <span className="brand-name">Lost &amp; Found Log</span>
              <span className="brand-sub">Office of the Student Affairs and Services</span>
            </span>
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
        <div className="stripe" aria-hidden="true" />
      </header>
      <main className="main">
        <Outlet />
      </main>
      <footer className="site-footer">
        <p>Found something? Bring it to the OSAS office so it can be posted here.</p>
      </footer>
    </div>
  );
}
