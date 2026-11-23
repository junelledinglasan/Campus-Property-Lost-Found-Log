import { createContext, useContext, useEffect, useState } from 'react';
import * as api from '../api/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => api.currentUser());

  // Kapag nag-expire ang session habang nasa OSAS desk, ibabalik sa sign in.
  useEffect(() => {
    const onExpired = () => setUser(null);
    window.addEventListener('lf:session-expired', onExpired);
    return () => window.removeEventListener('lf:session-expired', onExpired);
  }, []);

  const signIn = async (username, password) => {
    const u = await api.login(username, password);
    setUser(u);
  };

  const signOut = () => {
    api.logout();
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, signIn, signOut }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
