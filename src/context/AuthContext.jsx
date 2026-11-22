import { createContext, useContext, useState } from 'react';
import * as api from '../api/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => api.currentUser());

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
