'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Info } from 'lucide-react';
import { SimulateButton } from '@/components/dashboard/SimulateButton';
import { useI18nStore } from '@/store/i18nStore';

interface InfoPanelProps {
  activeAlert: any | null;
}

export default function InfoPanel3D({ activeAlert }: InfoPanelProps) {
  const { t, translateMessage } = useI18nStore();
  const pf = activeAlert?.particle_filter_30s;
  const hmmState = activeAlert?.hmm_state || 'SEGURO';

  // Utilizar directamente el nivel de riesgo predicho por el modelo ML del backend (o fallback por score si no está disponible)
  const rawScore = activeAlert?.risk_score != null 
    ? (activeAlert.risk_score > 1 ? activeAlert.risk_score : activeAlert.risk_score * 100)
    : 0;

  const calculatedRiskLevel = activeAlert?.risk_level || activeAlert?.level || (
    rawScore >= 80 ? 'ALTO' : rawScore >= 50 ? 'MEDIO' : 'BAJO'
  );
  
  const getTranslatedHmmState = (state: string) => {
    if (state.includes('SEGURO')) return t('hmm.secure');
    if (state.includes('INCIPIENTE')) return t('hmm.incipient');
    if (state.includes('INMINENTE')) return t('hmm.imminent');
    if (state.includes('AMBIENTAL')) return t('hmm.environmental');
    if (state.includes('MANIOBRA')) return t('hmm.maneuver');
    return state;
  };

  let riskBadgeStyle = 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold';
  if (calculatedRiskLevel === 'ALTO') {
    riskBadgeStyle = 'bg-red-600 hover:bg-red-700 text-white font-bold';
  } else if (calculatedRiskLevel === 'MEDIO') {
    riskBadgeStyle = 'bg-amber-500 hover:bg-amber-600 text-black font-bold';
  }

  return (
    <div className="absolute top-4 right-4 w-96 z-10 pointer-events-none">
      <Card className="bg-card/95 backdrop-blur-md shadow-2xl pointer-events-auto border-primary/20">
        <CardHeader className="pb-2 border-b">
          <CardTitle className="text-base flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Info className="h-5 w-5 text-primary" />
              {t('digitalTwin.title')}
            </span>
            <Badge variant="outline" className="font-mono text-xs">
              {t('digitalTwin.liveWs')}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-3 space-y-3">
          <div className="pt-1 pb-2 border-b border-border/50 flex justify-between items-center">
            <span className="text-xs text-muted-foreground">{t('digitalTwin.telemetryTest')}</span>
            <SimulateButton size="xs" variant="secondary" />
          </div>

          {!activeAlert ? (
            <div className="text-xs text-muted-foreground">
              {t('digitalTwin.normalMonitoring')}
            </div>
          ) : (
            <>
              {/* Nivel de Riesgo ML y HMM */}
              <div className="flex justify-between items-center bg-muted/40 p-2 rounded-lg">
                <div>
                  <span className="text-xs text-muted-foreground block">{t('digitalTwin.mlRisk')} ({activeAlert?.model_name || 'RandomForest'}):</span>
                  <Badge className={riskBadgeStyle}>
                    {calculatedRiskLevel === 'ALTO' ? t('levels.high') : calculatedRiskLevel === 'MEDIO' ? t('levels.medium') : t('levels.low')} ({rawScore.toFixed(1)}%)
                  </Badge>
                </div>
                <div className="text-right">
                  <span className="text-xs text-muted-foreground block">{t('digitalTwin.hmmState')}:</span>
                  <Badge className={
                    hmmState.includes('INMINENTE') || hmmState === 'INMINENTE'
                      ? 'bg-red-600 hover:bg-red-700 text-white font-bold'
                      : hmmState.includes('AMBIENTAL') || hmmState.includes('MANIOBRA') || hmmState === 'INCIPIENTE'
                      ? 'bg-amber-500 hover:bg-amber-600 text-black font-bold'
                      : 'bg-emerald-600 hover:bg-emerald-700 text-white font-bold'
                  }>
                    {getTranslatedHmmState(hmmState)}
                  </Badge>
                </div>
              </div>

              {/* Barometric Proximity & TTC Bar */}
              {activeAlert.distance_3d != null && (
                <div className="bg-muted/50 border border-primary/20 p-2.5 rounded-lg space-y-1.5">
                  <div className="flex justify-between items-center text-xs font-semibold">
                    <span className="text-muted-foreground flex items-center gap-1">
                      {t('digitalTwin.distance3d')}
                    </span>
                    <span className={activeAlert.distance_3d < 15 ? 'text-red-400 font-extrabold font-mono' : 'text-emerald-400 font-mono'}>
                      {activeAlert.distance_3d.toFixed(1)}m (TTC: {(activeAlert.ttc || activeAlert.distance_3d / 5).toFixed(1)}s)
                    </span>
                  </div>
                  {/* Proximity progress bar (0m to 50m) */}
                  <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 rounded-full ${
                        activeAlert.distance_3d < 15 ? 'bg-red-500 animate-pulse' :
                        activeAlert.distance_3d < 30 ? 'bg-amber-500' :
                        'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(100, Math.max(5, (activeAlert.distance_3d / 50) * 100))}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Predicción Filtro de Partículas +30s */}
              {pf && (
                <div className="border border-amber-500/40 bg-amber-500/10 p-2 rounded-lg space-y-1">
                  <div className="flex items-center justify-between text-xs font-semibold text-amber-500">
                    <span className="flex items-center gap-1">
                      <AlertTriangle className="h-3.5 w-3.5" />
                      {t('digitalTwin.pf30s')}
                    </span>
                    <span>{pf.collision_probability_30s}% {t('digitalTwin.risk')}</span>
                  </div>
                  <p className="text-[11px] text-foreground leading-tight">
                    {pf.suggested_action_30s}
                  </p>
                </div>
              )}

              {/* Telemetría Biométrica y Ambiental */}
              <div className="grid grid-cols-3 gap-1.5 text-[11px] bg-muted/30 p-2 rounded">
                <div>
                  <span className="text-muted-foreground block">{t('digitalTwin.biometrics')}</span>
                  <span className="font-semibold">{activeAlert.worker_bpm ? `${Math.round(activeAlert.worker_bpm)} BPM` : '85 BPM'}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">{t('digitalTwin.fatigueIndex')}</span>
                  <span className={`font-semibold ${(activeAlert.fatigue_index || 0.2) > 0.5 ? 'text-red-500' : 'text-emerald-500'}`}>
                    {(activeAlert.fatigue_index || 0.2).toFixed(2)}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground block">{t('digitalTwin.gasCo')}</span>
                  <span className="font-semibold">{activeAlert.gas_co_ppm ? `${activeAlert.gas_co_ppm.toFixed(1)} ppm` : '10 ppm'}</span>
                </div>
              </div>

              {/* Mensaje original */}
              <div className="text-[11px] text-muted-foreground border-t pt-1 font-mono">
                {translateMessage(activeAlert.message)}
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
