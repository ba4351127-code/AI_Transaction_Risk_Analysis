import React, { createContext, useContext, useState, useEffect } from 'react';

const PersonaContext = createContext();

export const PersonaProvider = ({ children }) => {
  // Read stored preference or default to everyday
  const [persona, setPersona] = useState(() => {
    const saved = localStorage.getItem('tg_persona');
    return saved === 'analyst' ? 'analyst' : 'everyday';
  });

  useEffect(() => {
    localStorage.setItem('tg_persona', persona);
  }, [persona]);

  const togglePersona = () => {
    setPersona((prev) => (prev === 'everyday' ? 'analyst' : 'everyday'));
  };

  const isAnalyst = persona === 'analyst';

  return (
    <PersonaContext.Provider value={{ persona, setPersona, togglePersona, isAnalyst }}>
      {children}
    </PersonaContext.Provider>
  );
};

export const usePersona = () => {
  const context = useContext(PersonaContext);
  if (!context) {
    throw new Error('usePersona must be used within a PersonaProvider');
  }
  return context;
};
