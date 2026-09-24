'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { useI18nStore } from '@/store/i18nStore';

interface Machine {
  id: number;
  machine_code: string;
  type: string;
  model: string;
  status: string;
}

export default function MaquinariaPage() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(true);
  const { t } = useI18nStore();

  useEffect(() => {
    const fetchMachines = async () => {
      try {
        const res = await api.get('/machines/');
        setMachines(res.data);
      } catch (err) {
        console.error('Error fetching machines', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMachines();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'OPERATING':
        return <Badge className="bg-emerald-600">{t('machineryPage.operating')}</Badge>;
      case 'IDLE':
        return <Badge variant="secondary">{t('machineryPage.idle')}</Badge>;
      case 'MAINTENANCE':
        return <Badge variant="destructive">{t('machineryPage.maintenance')}</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">{t('machineryPage.title')}</h2>
      
      <Card>
        <CardHeader>
          <CardTitle>{t('machineryPage.listTitle')}</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>{t('workersPage.loading')}</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('workersPage.id')}</TableHead>
                  <TableHead>{t('workersPage.code')}</TableHead>
                  <TableHead>{t('machineryPage.type')}</TableHead>
                  <TableHead>{t('machineryPage.model')}</TableHead>
                  <TableHead>{t('machineryPage.statusCol')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {machines.map((machine) => (
                  <TableRow key={machine.id}>
                    <TableCell>{machine.id}</TableCell>
                    <TableCell className="font-medium">{machine.machine_code}</TableCell>
                    <TableCell>{machine.type}</TableCell>
                    <TableCell>{machine.model}</TableCell>
                    <TableCell>{getStatusBadge(machine.status)}</TableCell>
                  </TableRow>
                ))}
                {machines.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-4">{t('machineryPage.empty')}</TableCell>
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
