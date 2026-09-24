import { create } from 'zustand';
import { es } from '@/locales/es';
import { en } from '@/locales/en';

type LocaleType = 'es' | 'en';

const dictionaries: Record<LocaleType, any> = {
  es,
  en
};

interface I18nState {
  locale: LocaleType;
  setLocale: (locale: LocaleType) => void;
  t: (key: string) => string;
  translateMessage: (msg: string) => string;
}

export const useI18nStore = create<I18nState>((set, get) => ({
  locale: 'es',
  setLocale: (locale) => set({ locale }),
  t: (key) => {
    const { locale } = get();
    const keys = key.split('.');
    let value = dictionaries[locale];
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return key; // Fallback to key if not found
      }
    }
    
    return value as string;
  },
  translateMessage: (msg: string) => {
    const { locale } = get();
    if (locale === 'es') return msg;
    
    // Si el mensaje viene estructurado del backend (ej: "Riesgo ALTO (ML): ...")
    let translated = msg;
    translated = translated.replace('Riesgo ALTO', 'HIGH Risk');
    translated = translated.replace('Riesgo MEDIO', 'MEDIUM Risk');
    translated = translated.replace('Riesgo BAJO', 'LOW Risk');
    
    translated = translated.replace('SEGURO', 'SECURE');
    translated = translated.replace('INCIPIENTE', 'INCIPIENT');
    translated = translated.replace('INMINENTE', 'IMMINENT');
    translated = translated.replace('RIESGO AMBIENTAL', 'ENVIRONMENTAL RISK');
    translated = translated.replace('MANIOBRA PELIGROSA', 'DANGEROUS MANEUVER');
    
    // PF Messages
    translated = translated.replace('Operación normal proyectada', 'Normal projected operation');
    translated = translated.replace('Frenado de emergencia LHD recomendado', 'LHD emergency braking recommended');
    translated = translated.replace('Precaución: Trayectoria convergente detectada', 'Caution: Converging trajectory detected');
    
    return translated;
  }
}));
