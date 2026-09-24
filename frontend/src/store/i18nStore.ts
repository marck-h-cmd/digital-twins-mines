import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { es } from '@/locales/es';
import { en } from '@/locales/en';

type LocaleType = 'es' | 'en';

const dictionaries: Record<LocaleType, any> = {
  es,
  en
};

interface I18nState {
  locale: LocaleType;
  language: LocaleType;
  setLocale: (locale: LocaleType) => void;
  setLanguage: (language: LocaleType) => void;
  t: (key: string) => string;
  translateMessage: (msg: string) => string;
}

export const useI18nStore = create<I18nState>()(
  persist(
    (set, get) => ({
      locale: 'es',
      language: 'es',
      setLocale: (locale) => set({ locale, language: locale }),
      setLanguage: (language) => set({ locale: language, language }),
      t: (key) => {
        const { locale } = get();
        const keys = key.split('.');
        let value = dictionaries[locale] || dictionaries['es'];
        
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
        if (locale === 'es' || !msg) return msg;
        
        let translated = String(msg);
        
        // Particle Filter Actions (Full sentences)
        translated = translated.replace(
          /EVACUACI[OÓ]N PREVENTIVA:\s*Intersecci[oó]n inminente proyectada a \+30s/gi,
          'PREVENTIVE EVACUATION: Imminent intersection projected at +30s'
        );
        translated = translated.replace(
          /ALERTA PREVENTIVA:\s*Reducir velocidad de equipo LHD a \+30s/gi,
          'PREVENTIVE ALERT: Reduce LHD equipment speed at +30s'
        );
        translated = translated.replace(
          /Operaci[oó]n normal proyectada/gi,
          'Normal projected operation'
        );
        translated = translated.replace(
          /Frenado de emergencia LHD recomendado/gi,
          'LHD emergency braking recommended'
        );
        translated = translated.replace(
          /Precauci[oó]n:\s*Trayectoria convergente detectada/gi,
          'Caution: Converging trajectory detected'
        );
        
        // Partial Action components
        translated = translated.replace(/EVACUACI[OÓ]N PREVENTIVA/gi, 'PREVENTIVE EVACUATION');
        translated = translated.replace(/ALERTA PREVENTIVA/gi, 'PREVENTIVE ALERT');
        translated = translated.replace(/Intersecci[oó]n inminente proyectada a \+30s/gi, 'Imminent intersection projected at +30s');
        translated = translated.replace(/Reducir velocidad de equipo LHD a \+30s/gi, 'Reduce LHD equipment speed at +30s');
        
        // Particle Filter Levels (with and without _30S / (+30s))
        translated = translated.replace(/CR[IÍ]TICO_30S/gi, 'CRITICAL (+30s)');
        translated = translated.replace(/PRECAUCI[OÓ]N_30S/gi, 'CAUTION (+30s)');
        translated = translated.replace(/SEGURO_30S/gi, 'SECURE (+30s)');
        translated = translated.replace(/CR[IÍ]TICO \(\+30s\)/gi, 'CRITICAL (+30s)');
        translated = translated.replace(/PRECAUCI[OÓ]N \(\+30s\)/gi, 'CAUTION (+30s)');
        translated = translated.replace(/SEGURO \(\+30s\)/gi, 'SECURE (+30s)');
        
        // Alert Risk Levels
        translated = translated.replace(/Riesgo ALTO/gi, 'HIGH Risk');
        translated = translated.replace(/Riesgo MEDIO/gi, 'MEDIUM Risk');
        translated = translated.replace(/Riesgo BAJO/gi, 'LOW Risk');
        
        // Standalone levels & states
        translated = translated.replace(/\bALTO\b/g, 'HIGH');
        translated = translated.replace(/\bMEDIO\b/g, 'MEDIUM');
        translated = translated.replace(/\bBAJO\b/g, 'LOW');
        translated = translated.replace(/\bSEGURO\b/g, 'SECURE');
        translated = translated.replace(/\bCR[IÍ]TICO\b/gi, 'CRITICAL');
        translated = translated.replace(/\bPRECAUCI[OÓ]N\b/gi, 'CAUTION');
        
        // HMM and Alert States
        translated = translated.replace(/NOMINAL_SEGURO/gi, 'NOMINAL_SECURE');
        translated = translated.replace(/RIESGO_INMINENTE_COLISI[OÓ]N/gi, 'IMMINENT_COLLISION_RISK');
        translated = translated.replace(/ALERTA_AMBIENTAL/gi, 'ENVIRONMENTAL_ALERT');
        translated = translated.replace(/MANIOBRA_INTERMEDIA/gi, 'INTERMEDIATE_MANEUVER');
        translated = translated.replace(/INCIPIENTE/gi, 'INCIPIENT');
        translated = translated.replace(/INMINENTE/gi, 'IMMINENT');
        translated = translated.replace(/RIESGO AMBIENTAL/gi, 'ENVIRONMENTAL RISK');
        translated = translated.replace(/MANIOBRA PELIGROSA/gi, 'DANGEROUS MANEUVER');
        
        // Operational Statuses
        translated = translated.replace(/\bATENDIDO\b/g, 'ATTENDED');
        translated = translated.replace(/\bEN PROCESO\b/g, 'IN PROGRESS');
        translated = translated.replace(/\bRESUELTO\b/g, 'RESOLVED');
        translated = translated.replace(/\bPENDIENTE\b/g, 'PENDING');
        
        // Telemetry Messages
        translated = translated.replace(/Alerta Cr[ií]tica:\s*Distancia/gi, 'Critical Alert: Distance');
        translated = translated.replace(/Alerta Cr[ií]tica/gi, 'Critical Alert');
        translated = translated.replace(/Alerta Moderada:\s*[IÍ]ndice de Fatiga/gi, 'Moderate Alert: Fatigue Index');
        translated = translated.replace(/Alerta Moderada/gi, 'Moderate Alert');
        translated = translated.replace(/a maquinaria en movimiento/gi, 'to moving machinery');
        translated = translated.replace(/detectado/gi, 'detected');
        translated = translated.replace(/Lecturas telem[eé]tricas estables en Zona Norte/gi, 'Stable telemetry readings in North Zone');
        translated = translated.replace(/Distancia 3D cr[ií]tica/gi, 'Critical 3D distance');
        translated = translated.replace(/con velocidad/gi, 'with speed');
        translated = translated.replace(/Concentraci[oó]n CO/gi, 'CO Concentration');
        translated = translated.replace(/por encima de umbral/gi, 'above threshold');
        translated = translated.replace(/Ritmo Card[ií]aco/gi, 'Heart Rate');
        translated = translated.replace(/en zona restringida/gi, 'in restricted zone');
        translated = translated.replace(/Proximidad a/gi, 'Proximity at');
        translated = translated.replace(/Registro telem[eé]trico/gi, 'Telemetry record');
        translated = translated.replace(/en frente M-11/gi, 'at front M-11');
        
        return translated;
      }
    }),
    {
      name: 'm11-i18n-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ locale: state.locale, language: state.locale } as any),
    }
  )
);
