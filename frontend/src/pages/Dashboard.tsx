import React from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PlatformHealth } from '../components/PlatformHealth';
import { PageHeader, StatCard, Card, Badge, InsightCard } from '../components/UI';
import {
  Database,
  HardDrive,
  Cpu,
  CheckCircle2,
  Calendar,
  Layers,
  ArrowRight,
  TrendingUp,
  Workflow,
  Sparkles,
  Search,
  BookOpen,
  ArrowUpRight,
  History,
  ShieldAlert,
  Server,
  Terminal,
  Activity,
  Tags
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { datasets, ingestionJobs, sparkJobs, deltaTables, setActivePage } = usePlatform();

  // Metrics Calculations
  const totalDatasetsCount = datasets.length;
  const storageUsedStr = '2.62 GB';
  const activeSparkJobsCount = sparkJobs.filter((j) => j.status === 'RUNNING').length;
  const totalPipelineRuns = ingestionJobs.length;
  const aiReadyTablesCount = deltaTables.length;
  const metadataAssetsCount = datasets.length + deltaTables.length; // unified metadata items

  // Storage data distribution
  const storageZoning = [
    { name: 'Bronze (Raw Landing)', size: 1.2, color: '#3b82f6', percent: 45 },
    { name: 'Silver (Processed Enriched)', size: 0.9, color: '#10b981', percent: 35 },
    { name: 'Gold (Curated Analytical)', size: 0.52, color: '#8b5cf6', percent: 20 },
  ];

  return (
    <div id="dashboard-page-container" className="space-y-8 animate-fadeIn font-sans">
      
      {/* 1. PREMIUM WELCOME BANNER & PLATFORM STATUS */}
      <div className="bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white rounded-2xl p-6 md:p-8 border border-slate-800/25 shadow-lg relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="absolute right-0 top-0 opacity-10 pointer-events-none">
          <Server className="w-80 h-80 -translate-y-16 translate-x-16 text-slate-400" />
        </div>
        <div className="space-y-2.5 relative z-10 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="text-[9px] bg-blue-500/10 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded font-bold uppercase tracking-wider font-mono">
              Live Educational Environment
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] text-emerald-400 font-medium tracking-tight">All Spark Clusters Operational</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white font-sans">
            Enterprise AI-Ready Data Platform
          </h2>
          <p className="text-xs md:text-sm text-slate-300 leading-relaxed font-sans font-light">
            An interactive playground demonstrating enterprise-grade Medallion architecture. Process POS terminal streams, run Spark deduplications, commit Delta ACID logs, and enforce PII masking for Generative AI prompting.
          </p>
        </div>

        {/* Quick Actions Panel */}
        <div className="relative z-10 flex flex-col sm:flex-row md:flex-col lg:flex-row gap-2">
          <button
            onClick={() => setActivePage('ingestion')}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg shadow-sm transition-all active:scale-[0.985] cursor-pointer"
          >
            <Workflow className="w-3.5 h-3.5" /> Trigger Ingestion Pipeline
          </button>
          <button
            onClick={() => setActivePage('architecture')}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/15 border border-white/10 hover:border-white/20 text-white text-xs font-medium rounded-lg transition-all active:scale-[0.985] cursor-pointer"
          >
            <BookOpen className="w-3.5 h-3.5 text-slate-300" /> View Tech Mapping
          </button>
        </div>
      </div>

      {/* 2. SIX PREMIUM KPI CARDS */}
      <div id="dashboard-kpi-grid" className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard
          id="stat-storage"
          title="Lake Storage"
          value={storageUsedStr}
          subtitle="MinIO S3 Buckets"
          trend={{ value: 'Within Quota', isPositive: true }}
          icon={<HardDrive className="w-4 h-4" />}
          onClick={() => setActivePage('lake')}
        />
        <StatCard
          id="stat-datasets"
          title="Registered Feeds"
          value={`${totalDatasetsCount} Sources`}
          subtitle="Bronze Landings"
          trend={{ value: '+1 Today', isPositive: true }}
          icon={<Database className="w-4 h-4" />}
          onClick={() => setActivePage('sources')}
        />
        <StatCard
          id="stat-pipelines"
          title="Active Pipelines"
          value={`${totalPipelineRuns} Runs`}
          subtitle="SLA Target 100%"
          trend={{ value: '98.5% Success', isPositive: true }}
          icon={<Workflow className="w-4 h-4" />}
          onClick={() => setActivePage('ingestion')}
        />
        <StatCard
          id="stat-spark"
          title="Spark Compute"
          value={`${activeSparkJobsCount} Active`}
          subtitle="Dynamic Executors"
          trend={{ value: 'Completed 3', isPositive: true }}
          icon={<Cpu className="w-4 h-4" />}
          onClick={() => setActivePage('spark')}
        />
        <StatCard
          id="stat-tables"
          title="AI-Ready Tables"
          value={`${aiReadyTablesCount} Curated`}
          subtitle="Delta Lake Format"
          trend={{ value: 'ACID Enforced', isPositive: true }}
          icon={<Layers className="w-4 h-4" />}
          onClick={() => setActivePage('delta')}
        />
        <StatCard
          id="stat-metadata"
          title="Metadata Assets"
          value={`${metadataAssetsCount} Cataloged`}
          subtitle="Unified Lineages"
          trend={{ value: 'PII Shielded', isPositive: true }}
          icon={<Tags className="w-4 h-4" />}
          onClick={() => setActivePage('metadata')}
        />
      </div>

      {/* 3. STORAGE TOPOLOGY & PIPELINE STATUS OVERVIEW */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Storage Space Map */}
        <Card id="dashboard-storage-card" className="flex flex-col justify-between">
          <div className="space-y-1">
            <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
              Storage Density Topology
            </h3>
            <p className="text-xs text-slate-400">
              Space utilization mapping across physical Medallion S3 storage zones.
            </p>
          </div>

          <div className="space-y-6 my-6">
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-slate-900 dark:text-white font-mono">
                {storageUsedStr}
              </span>
              <span className="text-xs text-slate-400 font-sans">used / 50.00 GB max</span>
            </div>

             {/* Layout bar stack */}
            <div className="h-4 w-full rounded-lg overflow-hidden flex bg-muted border border-border">
              {storageZoning.map((item, idx) => (
                <div
                  key={idx}
                  style={{ width: `${item.percent}%`, backgroundColor: item.color }}
                  className="h-full transition-all hover:opacity-90 relative"
                  title={`${item.name}: ${item.size} GB`}
                />
              ))}
            </div>

            {/* Legend block */}
            <div className="space-y-2 pt-2">
              {storageZoning.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs font-sans">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: item.color }} />
                    <span className="text-muted-foreground font-medium">{item.name}</span>
                  </div>
                  <span className="font-mono font-bold text-foreground/90">
                    {item.size} GB ({item.percent}%)
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-border">
            <button
              onClick={() => setActivePage('lake')}
              className="text-xs font-bold text-blue-600 dark:text-blue-400 hover:text-blue-700 flex items-center gap-1 cursor-pointer"
            >
              Analyze storage directories <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </Card>

        {/* Dynamic Spark Executor Topology & Status */}
        <Card id="dashboard-spark-monitor-card" className="lg:col-span-2 flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <div className="space-y-1">
              <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                Active Spark Compute Cluster
              </h3>
              <p className="text-xs text-slate-400">
                Live monitoring of dynamic Spark executors writing to conformed Silver/Gold levels.
              </p>
            </div>
            <button
              onClick={() => setActivePage('spark')}
              className="text-xs font-bold text-blue-600 dark:text-blue-400 flex items-center gap-1 cursor-pointer"
            >
              Open executor logs <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3.5 my-6">
            {sparkJobs.map((job) => (
              <div
                key={job.id}
                className="flex items-center justify-between p-3.5 bg-muted/45 border border-border rounded-lg transition-all duration-150 hover:bg-muted/80"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-md ${
                    job.status === 'RUNNING'
                      ? 'bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400'
                      : 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400'
                  }`}>
                    <Cpu className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-foreground font-mono block">
                      {job.name}
                    </span>
                    <div className="flex items-center gap-2 mt-0.5 text-[10px] text-muted-foreground font-sans">
                      <span>Cores: <strong className="text-foreground/80 font-mono">{job.cores}</strong></span>
                      <span>•</span>
                      <span>RAM: <strong className="text-foreground/80 font-mono">{job.memory}</strong></span>
                      <span>•</span>
                      <span>Type: <strong className="text-foreground/80 uppercase">{job.type}</strong></span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  {job.status === 'RUNNING' ? (
                    <div className="text-right">
                      <span className="text-[11px] font-bold text-blue-600 dark:text-blue-400 animate-pulse flex items-center justify-end gap-1 font-sans">
                        Running ({job.progress}%)
                      </span>
                      <span className="text-[9px] text-muted-foreground block font-mono">Deduplicating logs</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                      <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 font-sans">
                        Completed
                      </span>
                    </div>
                  )}
                  <span className="text-[10px] font-mono text-muted-foreground font-bold bg-muted px-2 py-0.5 rounded border border-border">
                    {job.duration}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-4 border-t border-border">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider font-sans">
              Cluster Utilization: 28 Cores / 112 GB Total Active Memory
            </span>
          </div>
        </Card>
      </div>

      {/* 4. RECENT DATASETS, PIPELINES & PLATFORM EVENT TIMELINE */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Recent Registered Datasets */}
        <Card id="dashboard-recent-datasets-card" className="lg:col-span-1">
          <div className="flex justify-between items-center mb-5">
            <h3 className="text-xs font-bold text-foreground uppercase tracking-wider font-sans">
              Recent Data Sources
            </h3>
            <button
              onClick={() => setActivePage('sources')}
              className="text-xs font-bold text-blue-600 dark:text-blue-400 hover:text-blue-700 flex items-center gap-1 cursor-pointer font-sans"
            >
              Browse catalog <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-border">
            {datasets.slice(0, 4).map((dataset) => (
              <div key={dataset.id} className="py-3 flex items-center justify-between text-xs font-sans">
                <div className="space-y-0.5 max-w-[150px]">
                  <span className="font-mono font-bold text-foreground block truncate">
                    {dataset.name}
                  </span>
                  <span className="text-[10px] text-muted-foreground block">{dataset.source}</span>
                </div>
                <div className="flex items-center gap-2.5">
                  <span className="text-[10px] font-mono bg-muted text-muted-foreground px-1.5 py-0.5 rounded border border-border">
                    {dataset.format}
                  </span>
                  <Badge
                    id={`badge-${dataset.id}`}
                    content={dataset.status}
                    variant={
                      dataset.status === 'Curated'
                        ? 'success'
                        : dataset.status === 'Processed'
                        ? 'primary'
                        : dataset.status === 'Ingesting'
                        ? 'warning'
                        : 'neutral'
                    }
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Recent Pipeline Ingestions */}
        <Card id="dashboard-recent-ingestion-card" className="lg:col-span-1">
          <div className="flex justify-between items-center mb-5">
            <h3 className="text-xs font-bold text-foreground uppercase tracking-wider font-sans">
              Recent Ingestion Logs
            </h3>
            <button
              onClick={() => setActivePage('ingestion')}
              className="text-xs font-bold text-blue-600 dark:text-blue-400 hover:text-blue-700 flex items-center gap-1 cursor-pointer font-sans"
            >
              Inspect pipelines <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-border">
            {ingestionJobs.slice(0, 4).map((job) => (
              <div key={job.id} className="py-3 flex items-center justify-between text-xs font-sans">
                <div className="space-y-0.5">
                  <span className="font-mono font-bold text-foreground block">
                    {job.datasetName}
                  </span>
                  <span className="text-[10px] text-muted-foreground block">Records: {job.recordsIngested.toLocaleString()}</span>
                </div>
                <div className="text-right space-y-0.5">
                  <span className="text-[10px] text-muted-foreground font-mono block">Duration: {job.duration}</span>
                  <Badge
                    id={`job-badge-${job.id}`}
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
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Dynamic Activity Timeline */}
        <Card id="dashboard-timeline-card" className="lg:col-span-1">
          <div className="space-y-1 mb-5">
            <h3 className="text-xs font-bold text-foreground uppercase tracking-wider font-sans flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-blue-500" /> Platform Event Feed
            </h3>
            <p className="text-xs text-muted-foreground">
              Recent real-time diagnostic logs from Aether.
            </p>
          </div>

          <div className="relative border-l-2 border-border pl-4 space-y-4">
            <div className="relative">
              <div className="absolute -left-[21px] mt-1.5 w-2 h-2 rounded-full bg-emerald-500 border border-card" />
              <div className="text-xs font-sans">
                <div className="font-bold text-foreground">RAG Grounding Cache Primed</div>
                <p className="text-[11px] text-muted-foreground mt-0.5">Gold transaction tables referenced successfully.</p>
                <span className="text-[9px] font-mono text-muted-foreground block mt-1">2026-07-02 04:00</span>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -left-[21px] mt-1.5 w-2 h-2 rounded-full bg-amber-500 border border-card" />
              <div className="text-xs font-sans">
                <div className="font-bold text-foreground">Data Quality Rule Evaluated</div>
                <p className="text-[11px] text-muted-foreground mt-0.5">Warning: customer_master country_not_null_warning active.</p>
                <span className="text-[9px] font-mono text-muted-foreground block mt-1">2026-07-02 03:05</span>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -left-[21px] mt-1.5 w-2 h-2 rounded-full bg-blue-500 border border-card" />
              <div className="text-xs font-sans">
                <div className="font-bold text-foreground">Spark Stream job "iot_sensor_stream"</div>
                <p className="text-[11px] text-muted-foreground mt-0.5">Bootstrapped continuous telemetry feed aggregation.</p>
                <span className="text-[9px] font-mono text-muted-foreground block mt-1">2026-07-02 03:00</span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* 5. PLATFORM HEALTH & SERVICE STATUS */}
      <PlatformHealth />

      {/* 6. ARCHITECTURE INSIGHT */}
      <InsightCard
        id="dashboard-architecture-insight"
        title="Medallion Unified Analytics"
        description="This educational controller centralizes structural ingestion pipelines and Apache Spark compute transformations. Processing datasets progressively through bronze (raw raw directories), silver (cleaned deduped data), and gold (business conformed metrics) guarantees clean data schemas ready for generative prompting."
        azureMapping={{
          openSource: 'Medallion Architecture Standard (Spark, S3, Delta Lake)',
          azureEquivalent: 'Azure Synapse Analytics & Azure Databricks Workspace',
          description: 'A complete environment coupling scalable spark workloads with hierarchical delta parquet storage engines.'
        }}
      />
    </div>
  );
};
