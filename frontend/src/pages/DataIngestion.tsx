import React from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PageHeader, Card, Button, Badge, ProgressBar, InsightCard } from '../components/UI';
import {
  Shuffle,
  ArrowRight,
  Database,
  Cpu,
  Layers,
  Sparkles,
  RefreshCw,
  Play,
  Server,
  Zap,
  Activity,
  CheckCircle2,
  Target,
  Cloud
} from 'lucide-react';

export const DataIngestion: React.FC = () => {
  const { ingestionJobs, datasets, runIngestion } = usePlatform();

  // Job counts
  const totalInbound = ingestionJobs.length;
  const runningCount = ingestionJobs.filter((j) => j.status === 'RUNNING').length;
  const successCount = ingestionJobs.filter((j) => j.status === 'SUCCESS').length;

  return (
    <div id="data-ingestion-page-container" className="space-y-8 animate-fadeIn">
      <PageHeader
        id="ingestion-header-block"
        title="Data Ingestion Orchestrator"
        description="Monitor stream-batch ingestion hooks translating incoming source rows into compressed Snappy Parquet partitions."
      />

      {/* Ingestion Status Grid */}
      <div id="ingestion-status-grid" className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card id="ingestion-kpi-total" className="flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Total Ingest Runs</span>
            <span className="text-3xl font-extrabold text-slate-900 dark:text-white font-mono block">{totalInbound}</span>
          </div>
          <div className="p-2.5 bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 rounded-lg border border-blue-100 dark:border-blue-900/30">
            <Shuffle className="w-4 h-4" />
          </div>
        </Card>
        <Card id="ingestion-kpi-running" className="flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Active Workers</span>
            <span className="text-3xl font-extrabold text-slate-900 dark:text-white mt-1 font-mono block">{runningCount}</span>
          </div>
          <div className="p-2.5 bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 rounded-lg border border-amber-100 dark:border-amber-900/30">
            <RefreshCw className={`w-4 h-4 ${runningCount > 0 ? 'animate-spin' : ''}`} />
          </div>
        </Card>
        <Card id="ingestion-kpi-success" className="flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Conformed Succeeds</span>
            <span className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1 font-mono block">{successCount}</span>
          </div>
          <div className="p-2.5 bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 rounded-lg border border-emerald-100 dark:border-emerald-900/30">
            <CheckCircle2 className="w-4 h-4" />
          </div>
        </Card>
      </div>

      {/* Interactive Flow Map */}
      <Card id="pipeline-diagram-card">
        <div className="space-y-1 mb-6">
          <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
            Automated Physical Ingestion Pipeline
          </h3>
          <p className="text-xs text-slate-400">
            Visualizing the live validation and compression flow as raw telemetry logs land in S3 directories.
          </p>
        </div>

        <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-slate-50/50 dark:bg-[#0B1329]/50 p-6 rounded-xl border border-slate-200/60 dark:border-slate-850/60 relative">
          
          {/* Node 1 */}
          <div className="flex-1 w-full bg-white dark:bg-[#1E293B]/60 border border-slate-200 dark:border-slate-800 p-4 rounded-xl flex flex-col items-center text-center space-y-2 shadow-xs transition-all hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 duration-200 group">
            <div className="p-2 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg">
              <Database className="w-4 h-4 group-hover:scale-110 transition-transform" />
            </div>
            <span className="text-xs font-bold text-slate-850 dark:text-white">Raw Source Land</span>
            <span className="text-[10px] text-slate-400 font-mono">S3/MinIO Bronze Bucket</span>
          </div>

          {/* Connection 1 */}
          <div className="flex items-center justify-center text-slate-400 dark:text-slate-600 rotate-90 md:rotate-0 flex-shrink-0">
            <ArrowRight className="w-4 h-4 text-blue-500 animate-pulse" />
          </div>

          {/* Node 2 */}
          <div className="flex-1 w-full bg-white dark:bg-[#1E293B]/60 border border-slate-200 dark:border-slate-800 p-4 rounded-xl flex flex-col items-center text-center space-y-2 shadow-xs transition-all hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 duration-200 group">
            <div className="p-2 bg-amber-500/10 text-amber-600 dark:text-amber-450 rounded-lg">
              <RefreshCw className="w-4 h-4 animate-spin-slow group-hover:scale-110 transition-transform" />
            </div>
            <span className="text-xs font-bold text-slate-850 dark:text-white">Format & Type Validator</span>
            <span className="text-[10px] text-slate-400 font-mono">Schema Validation Rules</span>
          </div>

          {/* Connection 2 */}
          <div className="flex items-center justify-center text-slate-400 dark:text-slate-600 rotate-90 md:rotate-0 flex-shrink-0">
            <ArrowRight className="w-4 h-4 text-blue-500 animate-pulse" />
          </div>

          {/* Node 3 */}
          <div className="flex-1 w-full bg-white dark:bg-[#1E293B]/60 border border-slate-200 dark:border-slate-800 p-4 rounded-xl flex flex-col items-center text-center space-y-2 shadow-xs transition-all hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 duration-200 group">
            <div className="p-2 bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 rounded-lg">
              <Sparkles className="w-4 h-4 group-hover:scale-110 transition-transform" />
            </div>
            <span className="text-xs font-bold text-slate-850 dark:text-white">Snappy Column Compression</span>
            <span className="text-[10px] text-slate-400 font-mono">Partitioning Optimization</span>
          </div>

          {/* Connection 3 */}
          <div className="flex items-center justify-center text-slate-400 dark:text-slate-600 rotate-90 md:rotate-0 flex-shrink-0">
            <ArrowRight className="w-4 h-4 text-blue-500 animate-pulse" />
          </div>

          {/* Node 4 */}
          <div className="flex-1 w-full bg-white dark:bg-[#1E293B]/60 border border-slate-200 dark:border-slate-800 p-4 rounded-xl flex flex-col items-center text-center space-y-2 shadow-xs transition-all hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 duration-200 group">
            <div className="p-2 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-lg">
              <Layers className="w-4 h-4 group-hover:scale-110 transition-transform" />
            </div>
            <span className="text-xs font-bold text-slate-850 dark:text-white">Silver Zone Parquet</span>
            <span className="text-[10px] text-slate-400 font-mono">Deduplicated Delta Tables</span>
          </div>

        </div>
      </Card>

      {/* Ingestion Jobs Monitor list */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <Card id="ingestion-jobs-list-card">
            <div className="mb-6">
              <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                Active Ingestion Pipeline Executions
              </h3>
              <p className="text-xs text-slate-400">
                Continuous job workers landing and validating raw incoming directories.
              </p>
            </div>

            <div className="space-y-4">
              {ingestionJobs.map((job) => {
                const matchingDataset = datasets.find((d) => d.name === job.datasetName);

                return (
                  <div
                    key={job.id}
                    className="p-4 bg-slate-50 dark:bg-[#0f172a]/20 border border-slate-200/60 dark:border-slate-800 rounded-lg space-y-4"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-white dark:bg-[#1E293B] rounded text-slate-500 border border-slate-200/50 dark:border-slate-700/60">
                          <Shuffle className="w-4 h-4 text-blue-500" />
                        </div>
                        <div>
                          <span className="text-xs font-bold text-slate-900 dark:text-white font-mono block">
                            job_trigger_ingest_{job.datasetName}
                          </span>
                          <span className="text-[10px] text-slate-400 font-mono mt-0.5 block">
                            Job Worker ID: <strong className="text-slate-600 dark:text-slate-300 font-mono">{job.id}</strong> • Landed: {job.timestamp}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Badge
                          id={`ingest-status-${job.id}`}
                          content={job.status}
                          variant={
                            job.status === 'SUCCESS'
                              ? 'success'
                              : job.status === 'RUNNING'
                              ? 'warning'
                              : job.status === 'QUEUED'
                              ? 'neutral'
                              : 'danger'
                          }
                        />
                        {job.status === 'QUEUED' && matchingDataset && (
                          <Button
                            id={`run-queued-ingest-${job.id}`}
                            variant="success"
                            size="sm"
                            icon={<Play className="w-3 h-3 text-white fill-white" />}
                            onClick={() => runIngestion(matchingDataset.id)}
                          >
                            Trigger
                          </Button>
                        )}
                      </div>
                    </div>

                    {/* Progress grid details */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                      <div className="bg-white dark:bg-[#1E293B] p-2.5 rounded border border-slate-100 dark:border-slate-800/80">
                        <span className="text-[9px] uppercase font-bold text-slate-400 block">Records Parsed</span>
                        <p className="text-sm font-bold font-mono text-slate-800 dark:text-slate-200 mt-1">
                          {job.recordsIngested.toLocaleString()}
                        </p>
                      </div>
                      <div className="bg-white dark:bg-[#1E293B] p-2.5 rounded border border-slate-100 dark:border-slate-800/80">
                        <span className="text-[9px] uppercase font-bold text-slate-400 block">Execution Span</span>
                        <p className="text-sm font-bold font-mono text-slate-800 dark:text-slate-200 mt-1">
                          {job.duration}
                        </p>
                      </div>
                      <div className="bg-white dark:bg-[#1E293B] p-2.5 rounded border border-slate-100 dark:border-slate-800/80">
                        <span className="text-[9px] uppercase font-bold text-slate-400 block">Parquet Compression</span>
                        <p className="text-sm font-bold font-mono text-blue-500 mt-1">Snappy columnar</p>
                      </div>
                    </div>

                    {job.status === 'RUNNING' && (
                      <ProgressBar
                        id={`ingest-progress-${job.id}`}
                        progress={job.progress}
                        statusLabel="Streaming partitions into silver landing folders..."
                      />
                    )}
                  </div>
                );
              })}
            </div>
          </Card>
        </div>

        {/* Validation configurations */}
        <div className="space-y-6">
          <Card id="ingestion-metrics-summary-card">
            <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider mb-4 font-sans">
              Gateway Schema Handshakes
            </h3>
            <div className="space-y-1.5">
              <div className="flex justify-between items-center py-2 border-b border-slate-50 dark:border-slate-800 text-xs">
                <span className="text-slate-400 dark:text-slate-500 font-sans">Schema Strict Check</span>
                <span className="font-mono font-bold text-emerald-500">True (Auto-Reject)</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-50 dark:border-slate-800 text-xs">
                <span className="text-slate-400 dark:text-slate-500 font-sans">Format Outlier Policy</span>
                <span className="font-mono font-bold text-amber-500">Quarantine Directory</span>
              </div>
              <div className="flex justify-between items-center py-2 text-xs">
                <span className="text-slate-400 dark:text-slate-500 font-sans">Stream Commit Type</span>
                <span className="font-mono font-bold text-blue-500">Append Only Partition</span>
              </div>
            </div>
          </Card>

          <div className="space-y-4 font-sans">
            <h3 className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider font-sans">
              Ingestion Architecture Map
            </h3>
            
            {/* Card 1: Pipeline Overview */}
            <div className="bg-white dark:bg-[#1E293B]/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex gap-3 items-start">
              <div className="p-1.5 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg flex-shrink-0">
                <Shuffle className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-850 dark:text-slate-200">1. Pipeline Overview</span>
                  <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded border border-blue-500/20">Active Orchestration</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  Automatically triggers schema checks and columns layout optimizations upon landing raw S3 feeds.
                </p>
              </div>
            </div>

            {/* Card 2: Enterprise Purpose */}
            <div className="bg-white dark:bg-[#1E293B]/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex gap-3 items-start">
              <div className="p-1.5 bg-amber-500/10 text-amber-600 dark:text-amber-450 rounded-lg flex-shrink-0">
                <Target className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-850 dark:text-slate-200">2. Enterprise Purpose</span>
                  <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-amber-500/10 text-amber-600 dark:text-amber-450 rounded border border-amber-500/20">Isolation</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  Decouples production online databases from heavy analytic loads to prevent user performance lags.
                </p>
              </div>
            </div>

            {/* Card 3: Azure Mapping */}
            <div className="bg-white dark:bg-[#1E293B]/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex gap-3 items-start">
              <div className="p-1.5 bg-sky-500/10 text-sky-600 dark:text-sky-400 rounded-lg flex-shrink-0">
                <Cloud className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-850 dark:text-slate-200">3. Azure Mapping</span>
                  <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-sky-500/10 text-sky-600 dark:text-sky-400 rounded border border-sky-500/20">Synapse / ADF</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  Maps directly to Azure Data Factory or Azure Event Hubs streaming events to ADLS containers.
                </p>
              </div>
            </div>

            {/* Card 4: Data Flow Diagram */}
            <div className="bg-white dark:bg-[#1E293B]/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex gap-3 items-start">
              <div className="p-1.5 bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded-lg flex-shrink-0">
                <Activity className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-850 dark:text-slate-200">4. Data Flow Diagram</span>
                  <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded border border-purple-500/20">Linear Ingest</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed font-mono">
                  Source Logs → S3 landing → Schema validation → Snappy Parquet partitions.
                </p>
              </div>
            </div>

            {/* Card 5: Best Practice */}
            <div className="bg-white dark:bg-[#1E293B]/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex gap-3 items-start border-l-4 border-l-emerald-500 dark:border-l-emerald-500">
              <div className="p-1.5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-lg flex-shrink-0">
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-850 dark:text-slate-200">5. Best Practice</span>
                  <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded border border-emerald-500/20">Schema Guard</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed italic">
                  Always enforce strict types on load and route outliers to quarantine folders.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
