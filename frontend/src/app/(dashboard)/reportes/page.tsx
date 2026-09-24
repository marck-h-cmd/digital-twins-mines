'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  FileText, Download, Sparkles, Send, Bot, Eye, Maximize2, Minimize2,
  ZoomIn, ZoomOut, RotateCcw, Copy, Check, Code, FileCode, Sliders, ShieldCheck
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useI18nStore } from '@/store/i18nStore';

interface ChatMessage {
  role: 'user' | 'bot';
  text: string;
}

export default function ReportesPage() {
  const { t, locale, language } = useI18nStore();
  const activeLang = locale || language || 'es';

  // Configurator state (Defaulted to Operational Worker Mode)
  const [evaluatorName, setEvaluatorName] = useState('Ing. SANTOS FERNANDEZ JUAN PEDRO');
  const [technicalNotes, setTechnicalNotes] = useState(
    activeLang === 'en'
      ? 'Continuous telemetric monitoring at M-11 extraction fronts. Operational proximity and fatigue alert log.'
      : 'Monitoreo telemétrico continuo en frentes de extracción M-11. Registro de alertas operacionales de proximidad y fatiga.'
  );
  const [includeFriedman, setIncludeFriedman] = useState(false);
  const [includeMetrics, setIncludeMetrics] = useState(false);
  
  // Keep technical notes synchronized if it hasn't been edited
  useEffect(() => {
    const esDefault = 'Monitoreo telemétrico continuo en frentes de extracción M-11. Registro de alertas operacionales de proximidad y fatiga.';
    const enDefault = 'Continuous telemetric monitoring at M-11 extraction fronts. Operational proximity and fatigue alert log.';
    if (technicalNotes === esDefault || technicalNotes === enDefault || !technicalNotes.trim()) {
      setTechnicalNotes(activeLang === 'en' ? enDefault : esDefault);
    }
  }, [activeLang]);

  // UI Preview controls state
  const [zoomLevel, setZoomLevel] = useState(100);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [activeTab, setActiveTab] = useState<'preview' | 'chat'>('preview');

  // Modals & Blob states
  const [pdfModalOpen, setPdfModalOpen] = useState(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loadingPdf, setLoadingPdf] = useState(false);

  const [jsonModalOpen, setJsonModalOpen] = useState(false);
  const [markdownModalOpen, setMarkdownModalOpen] = useState(false);
  const [copiedText, setCopiedText] = useState(false);

  // File Generation State
  const [generating, setGenerating] = useState(false);
  const [generatedFile, setGeneratedFile] = useState<string | null>(null);

  // Chat State
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'bot', text: t('reportsPage.chatInitial') }
  ]);

  // Sync initial bot message on language change if there is only 1 message
  useEffect(() => {
    setMessages(prev => {
      if (prev.length === 1 && prev[0].role === 'bot') {
        return [{ role: 'bot', text: t('reportsPage.chatInitial') }];
      }
      return prev;
    });
  }, [activeLang]);

  // Mock Metadata for JSON viewer
  const mockMetadata = {
    system: t('a4Preview.systemTitle'),
    institution: t('a4Preview.institution'),
    evaluator: evaluatorName,
    notes: technicalNotes,
    timestamp: new Date().toISOString(),
    champion_model: {
      name: "RandomForestClassifier",
      accuracy: 0.9985,
      f1_macro: 0.9982,
      precision_macro: 0.9976,
      recall_macro: 0.9988,
      auc_roc: 1.0000,
      hyperparameters: { n_estimators: 200, max_depth: 12, random_state: 42 }
    },
    statistical_tests: {
      friedman_test_included: includeFriedman,
      friedman_stat: 19.04,
      friedman_p_value: 0.00077,
      nemenyi_critical_distance: 2.728,
      pairwise_wilcoxon: [
        { comparison: "RandomForest vs XGBoost", p_value: 0.36689, h0_rejected: false },
        { comparison: "RandomForest vs MLP_NeuralNet", p_value: 0.00001, h0_rejected: true }
      ]
    },
    telemetry_summary: {
      total_evaluations: 20,
      high_risk: 7,
      medium_risk: 12,
      low_risk: 1
    }
  };

  // Mock Markdown text
  const generateMarkdownContent = () => `
# ${t('a4Preview.systemTitle')}
**${t('a4Preview.systemSubtitle')}**

---
- **${t('historyPage.date')}:** ${new Date().toLocaleString()}
- **${t('reportsPage.evaluator')}:** ${evaluatorName}
- **${t('a4Preview.institution')}**

---
## ${t('a4Preview.execSummary')}
- **${t('a4Preview.totalRecords')}:** 20
- **${t('a4Preview.riskHigh')}:** 7 (35.0%)
- **${t('a4Preview.riskMedium')}:** 12 (60.0%)
- **${t('a4Preview.riskLow')}:** 1 (5.0%)

---
## ${t('a4Preview.notesTitle')}
${technicalNotes}

---
${includeFriedman ? `
## ${t('a4Preview.statTitle')}
- **Friedman Stat:** 19.04 (p = 0.00077 < 0.05 -> ${t('a4Preview.reject')})
- **Nemenyi CD:** 2.728
- **RandomForest vs XGBoost:** p = 0.36689 (${t('a4Preview.notReject')})
- **RandomForest vs MLP:** p = 0.00001 (${t('a4Preview.reject')})
` : ''}

---
*${t('a4Preview.footerCopy')} ${new Date().getFullYear()} - ${t('a4Preview.footerDoc')}*
`;

  // Handlers
  const handleGenerateReport = async (format: string = 'pdf') => {
    setGenerating(true);
    try {
      const res = await api.post(`/reports?format=${format}&evaluator_name=${encodeURIComponent(evaluatorName)}&technical_notes=${encodeURIComponent(technicalNotes)}&include_friedman=${includeFriedman}&lang=${activeLang}`);
      setGeneratedFile(res.data.filename);
      return res.data.filename;
    } catch (err) {
      console.error('Error generando reporte:', err);
      return null;
    } finally {
      setGenerating(false);
    }
  };

  const handlePdfIframePreview = async () => {
    setLoadingPdf(true);
    setPdfModalOpen(true);
    try {
      const filename = await handleGenerateReport('pdf');
      if (filename) {
        const response = await api.get(`/reports/${filename}/download`, { responseType: 'blob' });
        const blobUrl = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
        setPdfUrl(blobUrl);
      }
    } catch (err) {
      console.error('Error en vista previa de PDF:', err);
    } finally {
      setLoadingPdf(false);
    }
  };

  const handleDownloadFile = async (fmt: string) => {
    setGenerating(true);
    try {
      const filename = await handleGenerateReport(fmt);
      if (filename) {
        const response = await api.get(`/reports/${filename}/download`, { responseType: 'blob' });
        const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = blobUrl;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(blobUrl);
      }
    } catch (err) {
      console.error('Error descargando archivo:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleCopyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  const handleChat = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const userMsg = chatInput.trim();
    setChatInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setChatLoading(true);

    try {
      const res = await api.post('/gemini/chat', { message: userMsg });
      setMessages(prev => [...prev, { role: 'bot', text: res.data.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: t('reportsPage.chatError') }]);
    } finally {
      setChatLoading(false);
    }
  }, [chatInput, chatLoading, t]);

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-foreground">
            {t('reportsPage.title')}
          </h2>
          <p className="text-sm text-muted-foreground">
            {t('reportsPage.desc')}
          </p>
        </div>
        
        {/* Navigation Tabs */}
        <div className="flex gap-2 bg-muted p-1 rounded-lg border border-border">
          <Button
            size="sm"
            variant={activeTab === 'preview' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('preview')}
            className="gap-2"
          >
            <FileText className="h-4 w-4" />
            {t('reportsPage.tabPreview')}
          </Button>
          <Button
            size="sm"
            variant={activeTab === 'chat' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('chat')}
            className="gap-2"
          >
            <Bot className="h-4 w-4" />
            {t('reportsPage.tabChat')}
          </Button>
        </div>
      </div>

      {activeTab === 'preview' && (
        <div className="grid gap-6 lg:grid-cols-12">
          {/* Configurator Side Panel (4 cols) */}
          <Card className="lg:col-span-4 h-fit border-border bg-card shadow-sm">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-base font-semibold">
                <Sliders className="h-4 w-4 text-primary" />
                {t('reportsPage.configTitle')}
              </CardTitle>
              <CardDescription className="text-xs">
                {t('reportsPage.configDesc')}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">{t('reportsPage.evaluator')}</label>
                <Input
                  value={evaluatorName}
                  onChange={(e) => setEvaluatorName(e.target.value)}
                  className="bg-background border-border text-sm"
                  placeholder={t('reportsPage.evaluatorPlh')}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground">{t('reportsPage.notes')}</label>
                <textarea
                  value={technicalNotes}
                  onChange={(e) => setTechnicalNotes(e.target.value)}
                  rows={4}
                  className="w-full rounded-md border border-border bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  placeholder={t('reportsPage.notesPlh')}
                />
              </div>

              <div className="space-y-3 pt-2 border-t border-border">
                <div className="flex justify-between items-center">
                  <p className="text-xs font-semibold text-muted-foreground">{t('reportsPage.options')}</p>
                  <Badge variant="outline" className="text-[10px] text-amber-600 border-amber-300">{t('reportsPage.workerMode')}</Badge>
                </div>
                <p className="text-[11px] text-muted-foreground italic">
                  {t('reportsPage.workerModeDesc')}
                </p>

                <label className="flex items-center gap-2 cursor-pointer text-xs">
                  <input
                    type="checkbox"
                    checked={includeFriedman}
                    onChange={(e) => setIncludeFriedman(e.target.checked)}
                    className="rounded border-border text-primary focus:ring-primary"
                  />
                  <span>{t('reportsPage.includeStats')}</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer text-xs">
                  <input
                    type="checkbox"
                    checked={includeMetrics}
                    onChange={(e) => setIncludeMetrics(e.target.checked)}
                    className="rounded border-border text-primary focus:ring-primary"
                  />
                  <span>{t('reportsPage.includeMetrics')}</span>
                </label>
              </div>

              <div className="pt-3 border-t border-border space-y-2">
                <p className="text-xs font-semibold text-muted-foreground mb-2">{t('reportsPage.tools')}</p>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePdfIframePreview}
                  className="w-full justify-start gap-2 text-xs"
                >
                  <Eye className="h-4 w-4 text-blue-500" />
                  {t('reportsPage.pdfModalBtn')}
                </Button>

                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setJsonModalOpen(true)}
                    className="justify-start gap-1.5 text-xs"
                  >
                    <Code className="h-3.5 w-3.5 text-emerald-500" />
                    {t('reportsPage.jsonBtn')}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setMarkdownModalOpen(true)}
                    className="justify-start gap-1.5 text-xs"
                  >
                    <FileCode className="h-3.5 w-3.5 text-amber-500" />
                    {t('reportsPage.mdBtn')}
                  </Button>
                </div>
              </div>

              {/* Download Buttons Section */}
              <div className="pt-4 border-t border-border space-y-2">
                <p className="text-xs font-semibold text-muted-foreground">{t('reportsPage.export')}</p>
                <div className="grid grid-cols-3 gap-2">
                  <Button
                    onClick={() => handleDownloadFile('pdf')}
                    disabled={generating}
                    size="sm"
                    className="w-full bg-red-600 hover:bg-red-700 text-white font-medium"
                  >
                    <Download className="h-3.5 w-3.5 mr-1" /> PDF
                  </Button>

                  <Button
                    onClick={() => handleDownloadFile('word')}
                    disabled={generating}
                    size="sm"
                    variant="outline"
                    className="w-full border-blue-500/30 text-blue-600 hover:bg-blue-500/10 font-medium"
                  >
                    <Download className="h-3.5 w-3.5 mr-1" /> Word
                  </Button>

                  <Button
                    onClick={() => handleDownloadFile('excel')}
                    disabled={generating}
                    size="sm"
                    variant="outline"
                    className="w-full border-emerald-500/30 text-emerald-600 hover:bg-emerald-500/10 font-medium"
                  >
                    <Download className="h-3.5 w-3.5 mr-1" /> Excel
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* A4 Live Document Sheet Viewer (8 cols) */}
          <div className="lg:col-span-8 space-y-3">
            {/* Toolbar for A4 Document */}
            <div className="flex items-center justify-between bg-card border border-border px-4 py-2 rounded-lg shadow-sm">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="gap-1 border-primary/40 text-primary">
                  <ShieldCheck className="h-3.5 w-3.5" /> {t('reportsPage.a4Title')}
                </Badge>
                <span className="text-xs text-muted-foreground hidden sm:inline">
                  (210 mm x 297 mm)
                </span>
              </div>

              {/* Zoom & FullScreen Controls */}
              <div className="flex items-center gap-1.5">
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-8 w-8"
                  onClick={() => setZoomLevel(prev => Math.max(prev - 10, 50))}
                  title={t('reportsPage.zoomOut')}
                >
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <span className="text-xs font-mono w-10 text-center">{zoomLevel}%</span>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-8 w-8"
                  onClick={() => setZoomLevel(prev => Math.min(prev + 10, 150))}
                  title={t('reportsPage.zoomIn')}
                >
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-8 w-8"
                  onClick={() => setZoomLevel(100)}
                  title={t('reportsPage.resetZoom')}
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                </Button>

                <div className="h-4 w-px bg-border mx-1" />

                <Button
                  size="icon"
                  variant="ghost"
                  className="h-8 w-8"
                  onClick={() => setIsFullScreen(!isFullScreen)}
                  title={isFullScreen ? t('reportsPage.exitFullscreen') : t('reportsPage.fullscreen')}
                >
                  {isFullScreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            {/* A4 Sheet Container */}
            <div className={`overflow-auto flex justify-center p-4 bg-muted/40 rounded-lg border border-border min-h-[750px] ${
              isFullScreen ? 'fixed inset-0 z-50 bg-background p-8 rounded-none border-none overflow-y-auto' : ''
            }`}>
              {isFullScreen && (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => setIsFullScreen(false)}
                  className="fixed top-4 right-6 z-50 gap-2 shadow-lg"
                >
                  <Minimize2 className="h-4 w-4" /> {t('reportsPage.exitFullscreen')}
                </Button>
              )}

              {/* The Styled A4 Paper */}
              <div
                style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center' }}
                className="transition-transform duration-150 ease-out bg-white text-slate-900 shadow-2xl rounded-sm p-8 border border-slate-300 w-[794px] min-h-[1123px] font-sans text-xs space-y-6 select-text"
              >
                {/* Header Section */}
                <div className="border-b-2 border-slate-900 pb-4 flex justify-between items-start">
                  <div>
                    <h1 className="text-xl font-bold tracking-tight text-slate-950 uppercase">
                      {t('a4Preview.systemTitle')}
                    </h1>
                    <p className="text-sm font-semibold text-slate-700">
                      {t('a4Preview.systemSubtitle')}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {t('a4Preview.institution')} {new Date().toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="px-2.5 py-1 bg-slate-900 text-white font-mono text-[10px] uppercase font-bold rounded">
                      {t('a4Preview.format')}
                    </span>
                    <p className="text-[11px] text-slate-600 mt-2 font-medium">
                      {t('a4Preview.evaluator')} <span className="text-slate-900 font-bold">{evaluatorName || t('a4Preview.unassigned')}</span>
                    </p>
                  </div>
                </div>

                {/* Resumen Ejecutivo KPI Grid */}
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-slate-900 border-l-4 border-slate-900 pl-2">
                    {t('a4Preview.execSummary')}
                  </h3>
                  <div className="grid grid-cols-4 gap-3 text-center">
                    <div className="p-2.5 bg-slate-100 rounded border border-slate-200">
                      <p className="text-[10px] text-slate-500 font-bold uppercase">{t('a4Preview.totalRecords')}</p>
                      <p className="text-lg font-extrabold text-slate-900">20</p>
                    </div>
                    <div className="p-2.5 bg-red-50 rounded border border-red-200">
                      <p className="text-[10px] text-red-600 font-bold uppercase">{t('a4Preview.riskHigh')}</p>
                      <p className="text-lg font-extrabold text-red-700">7 <span className="text-xs font-normal">(35%)</span></p>
                    </div>
                    <div className="p-2.5 bg-amber-50 rounded border border-amber-200">
                      <p className="text-[10px] text-amber-600 font-bold uppercase">{t('a4Preview.riskMedium')}</p>
                      <p className="text-lg font-extrabold text-amber-700">12 <span className="text-xs font-normal">(60%)</span></p>
                    </div>
                    <div className="p-2.5 bg-emerald-50 rounded border border-emerald-200">
                      <p className="text-[10px] text-emerald-600 font-bold uppercase">{t('a4Preview.riskLow')}</p>
                      <p className="text-lg font-extrabold text-emerald-700">1 <span className="text-xs font-normal">(5%)</span></p>
                    </div>
                  </div>
                </div>

                {/* Technical Notes */}
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-slate-900 border-l-4 border-slate-900 pl-2">
                    {t('a4Preview.notesTitle')}
                  </h3>
                  <div className="p-3 bg-slate-50 rounded border border-slate-200 text-slate-700 italic leading-relaxed text-xs">
                    "{technicalNotes || t('a4Preview.noNotes')}"
                  </div>
                </div>

                {/* Sample Telemetry Table */}
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-slate-900 border-l-4 border-slate-900 pl-2">
                    {t('a4Preview.sampleTitle')}
                  </h3>
                  <table className="w-full text-[11px] border-collapse border border-slate-300">
                    <thead>
                      <tr className="bg-slate-900 text-white font-semibold">
                        <th className="p-1.5 border border-slate-400 text-center">{t('a4Preview.colId')}</th>
                        <th className="p-1.5 border border-slate-400 text-left">{t('a4Preview.colEntity')}</th>
                        <th className="p-1.5 border border-slate-400 text-center">{t('a4Preview.colDist')}</th>
                        <th className="p-1.5 border border-slate-400 text-center">{t('a4Preview.colTtc')}</th>
                        <th className="p-1.5 border border-slate-400 text-center">{t('a4Preview.colFatigue')}</th>
                        <th className="p-1.5 border border-slate-400 text-center">{t('a4Preview.colRisk')}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                      <tr>
                        <td className="p-1.5 text-center font-mono font-medium">#1001</td>
                        <td className="p-1.5">{t('a4Preview.sampleWorker1')}</td>
                        <td className="p-1.5 text-center font-mono">3.20 m</td>
                        <td className="p-1.5 text-center font-mono">1.10 s</td>
                        <td className="p-1.5 text-center font-mono">0.82</td>
                        <td className="p-1.5 text-center font-bold text-red-600 bg-red-50">{t('a4Preview.riskHigh').replace(' 🔴','')} 🔴</td>
                      </tr>
                      <tr>
                        <td className="p-1.5 text-center font-mono font-medium">#1002</td>
                        <td className="p-1.5">{t('a4Preview.sampleWorker2')}</td>
                        <td className="p-1.5 text-center font-mono">11.50 m</td>
                        <td className="p-1.5 text-center font-mono">3.40 s</td>
                        <td className="p-1.5 text-center font-mono">0.45</td>
                        <td className="p-1.5 text-center font-bold text-amber-600 bg-amber-50">{t('a4Preview.riskMedium').replace(' 🟡','')} 🟡</td>
                      </tr>
                      <tr>
                        <td className="p-1.5 text-center font-mono font-medium">#1003</td>
                        <td className="p-1.5">{t('a4Preview.sampleWorker3')}</td>
                        <td className="p-1.5 text-center font-mono">38.40 m</td>
                        <td className="p-1.5 text-center font-mono">7.20 s</td>
                        <td className="p-1.5 text-center font-mono">0.12</td>
                        <td className="p-1.5 text-center font-bold text-emerald-600 bg-emerald-50">{t('a4Preview.riskLow').replace(' 🟢','')} 🟢</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* 4. Physical Visualizations & Telemetry Charts */}
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-slate-900 border-l-4 border-slate-900 pl-2">
                    {t('a4Preview.visTitle')}
                  </h3>
                  <div className="grid grid-cols-2 gap-3 p-3 bg-slate-50 rounded border border-slate-200">
                    <div className="space-y-1.5 bg-white p-2.5 rounded border border-slate-200">
                      <p className="text-[10px] font-bold text-slate-700 uppercase text-center">{t('a4Preview.distTitle')}</p>
                      <div className="space-y-1.5 pt-1">
                        <div>
                          <div className="flex justify-between text-[10px] text-slate-600 font-medium mb-0.5"><span>{t('a4Preview.riskHigh')}</span><span>7 (35%)</span></div>
                          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden"><div className="bg-red-500 h-full rounded-full w-[35%]" /></div>
                        </div>
                        <div>
                          <div className="flex justify-between text-[10px] text-slate-600 font-medium mb-0.5"><span>{t('a4Preview.riskMedium')}</span><span>12 (60%)</span></div>
                          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden"><div className="bg-amber-500 h-full rounded-full w-[60%]" /></div>
                        </div>
                        <div>
                          <div className="flex justify-between text-[10px] text-slate-600 font-medium mb-0.5"><span>{t('a4Preview.riskLow')}</span><span>1 (5%)</span></div>
                          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden"><div className="bg-emerald-500 h-full rounded-full w-[5%]" /></div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-1.5 bg-white p-2.5 rounded border border-slate-200 flex flex-col justify-between">
                      <p className="text-[10px] font-bold text-slate-700 uppercase text-center">{t('a4Preview.matrixTitle')}</p>
                      <div className="grid grid-cols-2 gap-2 text-center text-[10px] pt-1">
                        <div className="p-1.5 bg-slate-100 rounded border border-slate-200">
                          <span className="block text-slate-500 font-semibold">{t('a4Preview.thresholdDist')}</span>
                          <span className="font-mono font-bold text-slate-900">&lt; 5.0 m</span>
                        </div>
                        <div className="p-1.5 bg-slate-100 rounded border border-slate-200">
                          <span className="block text-slate-500 font-semibold">{t('a4Preview.thresholdTtc')}</span>
                          <span className="font-mono font-bold text-slate-900">&lt; 2.5 s</span>
                        </div>
                        <div className="p-1.5 bg-slate-100 rounded border border-slate-200">
                          <span className="block text-slate-500 font-semibold">{t('a4Preview.thresholdFatigue')}</span>
                          <span className="font-mono font-bold text-slate-900">0.85 / 1.0</span>
                        </div>
                        <div className="p-1.5 bg-slate-100 rounded border border-slate-200">
                          <span className="block text-slate-500 font-semibold">{t('a4Preview.thresholdGas')}</span>
                          <span className="font-mono font-bold text-slate-900">45.0 PPM</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Champion Model Metrics Section (Optional) */}
                {includeMetrics && (
                  <div className="space-y-2">
                    <h3 className="text-sm font-bold text-slate-900 border-l-4 border-slate-900 pl-2">
                      {t('a4Preview.modelTitle')}
                    </h3>
                    <table className="w-full text-[11px] border-collapse border border-slate-300">
                      <thead>
                        <tr className="bg-slate-800 text-white font-semibold">
                          <th className="p-1.5 border border-slate-400 text-left">{t('a4Preview.colMetric')}</th>
                          <th className="p-1.5 border border-slate-400 text-center">{t('a4Preview.colValue')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="bg-slate-50"><td className="p-1.5 border">{t('a4Preview.acc')}</td><td className="p-1.5 border text-center font-bold text-slate-900">99.85%</td></tr>
                        <tr><td className="p-1.5 border">{t('a4Preview.f1')}</td><td className="p-1.5 border text-center font-bold text-slate-900">0.9982</td></tr>
                        <tr className="bg-slate-50"><td className="p-1.5 border">{t('a4Preview.prec')}</td><td className="p-1.5 border text-center font-bold text-slate-900">0.9976</td></tr>
                        <tr><td className="p-1.5 border">{t('a4Preview.rec')}</td><td className="p-1.5 border text-center font-bold text-slate-900">0.9988</td></tr>
                        <tr className="bg-slate-50"><td className="p-1.5 border">{t('a4Preview.auc')}</td><td className="p-1.5 border text-center font-bold text-slate-900">1.0000</td></tr>
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Friedman & Wilcoxon Section */}
                {includeFriedman && (
                  <div className="space-y-2">
                    <h3 className="text-sm font-bold text-slate-900 border-l-4 border-slate-900 pl-2">
                      {t('a4Preview.statTitle')}
                    </h3>
                    <table className="w-full text-[10px] border-collapse border border-slate-300">
                      <thead>
                        <tr className="bg-slate-900 text-white">
                          <th className="p-1 border border-slate-400">{t('a4Preview.colComp')}</th>
                          <th className="p-1 border border-slate-400 text-center">{t('a4Preview.colDiff')}</th>
                          <th className="p-1 border border-slate-400 text-center">{t('a4Preview.colTstat')}</th>
                          <th className="p-1 border border-slate-400 text-center">{t('a4Preview.colPval')}</th>
                          <th className="p-1 border border-slate-400 text-center">{t('a4Preview.colH0')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td className="p-1 border font-medium">RandomForest vs XGBoost</td>
                          <td className="p-1 border text-center font-mono">0.0012</td>
                          <td className="p-1 border text-center font-mono">1.02</td>
                          <td className="p-1 border text-center font-mono">0.36689</td>
                          <td className="p-1 border text-center font-bold text-slate-700">{t('a4Preview.notReject')}</td>
                        </tr>
                        <tr className="bg-slate-50">
                          <td className="p-1 border font-medium">RandomForest vs MLP_NeuralNet</td>
                          <td className="p-1 border text-center font-mono">0.0523</td>
                          <td className="p-1 border text-center font-mono">26.40</td>
                          <td className="p-1 border text-center font-mono text-red-600 font-bold">0.00001</td>
                          <td className="p-1 border text-center font-bold text-red-600">{t('a4Preview.reject')}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Footer */}
                <div className="pt-6 border-t border-slate-300 flex justify-between items-center text-[10px] text-slate-400">
                  <p>{t('a4Preview.footerCopy')} {new Date().getFullYear()}</p>
                  <p>{t('a4Preview.footerDoc')}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: AI Chatbot */}
      {activeTab === 'chat' && (
        <Card className="flex flex-col min-h-[550px] border-border bg-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              {t('reportsPage.chatTitle')}
              <Badge variant="outline" className="text-xs ml-auto border-primary/30 text-primary">Gemini 3.6 Flash</Badge>
            </CardTitle>
            <CardDescription>
              {t('reportsPage.chatDesc')}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col flex-1 gap-3">
            <div className="flex-1 overflow-y-auto space-y-3 max-h-[380px] pr-2">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`rounded-2xl px-4 py-2.5 max-w-[85%] text-sm ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-tr-sm'
                      : 'bg-muted text-foreground rounded-tl-sm border border-border'
                  }`}>
                    {msg.role === 'bot' ? (
                      <div className="prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-headings:my-1">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>
                    ) : (
                      <p>{msg.text}</p>
                    )}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm text-muted-foreground animate-pulse">
                    {t('reportsPage.chatProcessing')}
                  </div>
                </div>
              )}
            </div>

            <form onSubmit={handleChat} className="flex gap-2 mt-auto pt-2">
              <Input
                placeholder={t('reportsPage.chatPlaceholder')}
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                disabled={chatLoading}
                className="flex-1 bg-background"
              />
              <Button type="submit" disabled={!chatInput.trim() || chatLoading}>
                <Send className="h-4 w-4 mr-1" /> {t('reportsPage.chatSend')}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* PDF Visor Modal (iframe) */}
      {pdfModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-card border border-border w-full max-w-5xl rounded-xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
            <div className="p-4 border-b border-border flex items-center justify-between bg-muted/40">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-red-500" />
                <h3 className="font-semibold text-base">{t('reportsPage.pdfModalTitle')}</h3>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setPdfModalOpen(false)}>
                {t('reportsPage.close')}
              </Button>
            </div>

            <div className="flex-1 bg-slate-900 p-2 flex items-center justify-center min-h-[600px]">
              {loadingPdf ? (
                <div className="flex flex-col items-center gap-3 text-muted-foreground">
                  <span className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                  <p className="text-sm">{t('reportsPage.pdfCompiling')}</p>
                </div>
              ) : pdfUrl ? (
                <iframe
                  src={pdfUrl}
                  className="w-full h-[75vh] rounded border border-border"
                  title="Vista Previa de Reporte PDF"
                />
              ) : (
                <p className="text-sm text-red-400">{t('reportsPage.pdfError')}</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* JSON Inspection Modal */}
      {jsonModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-card border border-border w-full max-w-3xl rounded-xl shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
            <div className="p-4 border-b border-border flex items-center justify-between bg-muted/40">
              <div className="flex items-center gap-2">
                <Code className="h-5 w-5 text-emerald-500" />
                <h3 className="font-semibold text-base">{t('reportsPage.jsonModalTitle')}</h3>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleCopyToClipboard(JSON.stringify(mockMetadata, null, 2))}
                  className="gap-1.5 text-xs"
                >
                  {copiedText ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
                  {copiedText ? t('reportsPage.copied') : t('reportsPage.copyJson')}
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setJsonModalOpen(false)}>
                  {t('reportsPage.close')}
                </Button>
              </div>
            </div>
            <div className="p-4 overflow-y-auto max-h-[65vh] bg-slate-950 text-slate-200 font-mono text-xs rounded-b-xl">
              <pre>{JSON.stringify(mockMetadata, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}

      {/* Markdown Inspection Modal */}
      {markdownModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-card border border-border w-full max-w-3xl rounded-xl shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
            <div className="p-4 border-b border-border flex items-center justify-between bg-muted/40">
              <div className="flex items-center gap-2">
                <FileCode className="h-5 w-5 text-amber-500" />
                <h3 className="font-semibold text-base">{t('reportsPage.mdModalTitle')}</h3>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleCopyToClipboard(generateMarkdownContent())}
                  className="gap-1.5 text-xs"
                >
                  {copiedText ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
                  {copiedText ? t('reportsPage.copied') : t('reportsPage.copyMd')}
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setMarkdownModalOpen(false)}>
                  {t('reportsPage.close')}
                </Button>
              </div>
            </div>
            <div className="p-4 overflow-y-auto max-h-[65vh] bg-slate-950 text-slate-200 font-mono text-xs rounded-b-xl whitespace-pre-wrap">
              {generateMarkdownContent()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
