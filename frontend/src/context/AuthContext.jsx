import React, { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => authService.getUser());
  const [token, setToken] = useState(() => authService.getToken());
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalTab, setAuthModalTab] = useState('login'); // 'login' | 'signup'

  // Validate session on mount
  useEffect(() => {
    let isMounted = true;
    const verifySession = async () => {
      const storedToken = authService.getToken();
      if (storedToken) {
        try {
          const profile = await authService.getMe();
          if (isMounted && profile) {
            setUser(profile);
            authService.setUser(profile);
          }
        } catch (err) {
          // Token expired or invalid
          if (isMounted) {
            authService.logout();
            setUser(null);
            setToken(null);
          }
        }
      }
      if (isMounted) setIsLoading(false);
    };

    verifySession();
    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (email, password) => {
    const res = await authService.login({ email, password });
    if (res?.access_token) {
      setToken(res.access_token);
      setUser(res.user);
      setIsAuthModalOpen(false);
      return res.user;
    }
    throw new Error('Authentication failed.');
  };

  const signup = async (fullName, email, password) => {
    const res = await authService.signup({
      full_name: fullName,
      email,
      password
    });
    if (res?.access_token) {
      setToken(res.access_token);
      setUser(res.user);
      setIsAuthModalOpen(false);
      return res.user;
    }
    throw new Error('Signup failed.');
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setToken(null);
  };

  const openAuthModal = (tab = 'login') => {
    setAuthModalTab(tab);
    setIsAuthModalOpen(true);
  };

  const closeAuthModal = () => {
    setIsAuthModalOpen(false);
  };

  const value = {
    user,
    token,
    isAuthenticated: Boolean(user),
    isLoading,
    login,
    signup,
    logout,
    isAuthModalOpen,
    authModalTab,
    setAuthModalTab,
    openAuthModal,
    closeAuthModal
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
