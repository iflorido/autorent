import { createContext, useContext, useState, type ReactNode } from "react";

interface HeroCtx {
  tieneHeroOscuro: boolean;
  setHeroOscuro: (v: boolean) => void;
}

const HeroContext = createContext<HeroCtx>({
  tieneHeroOscuro: false,
  setHeroOscuro: () => {},
});

export function HeroProvider({ children }: { children: ReactNode }) {
  const [tieneHeroOscuro, setHeroOscuro] = useState(false);
  return (
    <HeroContext.Provider value={{ tieneHeroOscuro, setHeroOscuro }}>
      {children}
    </HeroContext.Provider>
  );
}

export const useHero = () => useContext(HeroContext);
