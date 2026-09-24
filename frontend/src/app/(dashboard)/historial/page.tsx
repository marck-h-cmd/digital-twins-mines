'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { useI18nStore } from '@/store/i18nStore';

interface AlertLog {
  id: number;
  interaction_id: number;
  alert_level: string;
  message: string;
  status: string;
  created_at: string;
}

export default function HistorialPage() {
  const [alerts, setAlerts] = useState<AlertLog[]>([]);
  const [loading, setLoading] = useState(true);
  const { t, translateMessage } = useI18nStore();

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await api.get('/alerts/');
        setAlerts(res.data);
      } catch (err) {
        console.error('Error fetching alerts', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">{t('historyPage.title')}</h2>
      
      <Card>
        <CardHeader>
          <CardTitle>{t('historyPage.listTitle')}</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>{t('workersPage.loading')}</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('historyPage.date')}</TableHead>
                  <TableHead>{t('historyPage.risk')}</TableHead>
                  <TableHead>{t('historyPage.message')}</TableHead>
                  <TableHead>{t('historyPage.interactionId')}</TableHead>
                  <TableHead>{t('historyPage.status')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {alerts.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell>{format(new Date(alert.created_at), 'dd/MM/yyyy HH:mm:ss')}</TableCell>
                    <TableCell>
                      <Badge variant={alert.alert_level === 'ALTO' ? 'destructive' : 'default'} className={alert.alert_level === 'MEDIO' ? 'bg-amber-500 text-black' : ''}>
                        {alert.alert_level === 'ALTO' ? t('levels.high') : alert.alert_level === 'MEDIO' ? t('levels.medium') : t('levels.low')}
                      </Badge>
                    </TableCell>
                    <TableCell>{translateMessage(alert.message)}</TableCell>
                    <TableCell>#{alert.interaction_id}</TableCell>
                    <TableCell>{alert.status}</TableCell>
                  </TableRow>
                ))}
                {alerts.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-4">{t('historyPage.empty')}</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
