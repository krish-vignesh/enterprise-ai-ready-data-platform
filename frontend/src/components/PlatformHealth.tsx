import React, { useState } from 'react';
import {
  Server,
  HardDrive,
  Cpu,
  Database,
  Tags,
  Workflow,
  Binary,
  Clock,
  ArrowRight,
  Activity,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  RefreshCw,
  Layers,
  ArrowRightCircle
} from 'lucide-react';
import { Card, Badge } from './UI';

// Define the TS structure to match future FastAPI JSON response
export interface ServiceHealth {
  id: string;
  name: string;
  status: 'healthy' | 'starting' | 'offline' | 'maintenance' | 'not_configured';
  version: string;
  lastCheck: string;
  description: string;
  iconName: 'server' | 'hard-drive' | 'cpu' | 'database' | 'tags' | 'workflow' | 'binary' | 'clock';
}

export interface PipelineStage {
  name: string;
  status: 'waiting' | 'running' | 'completed' | 'failed';
}

export interface PlatformMetrics {
  datasetsCount: number;
  pipelinesCount: number;
  aiTablesCount: number;
  uptime: string;
}

export interface PlatformEvent {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  type: 'info' | 'warning' | 'success' | 'error';
}

export const PlatformHealth: React.FC = () => {
  const [isSimulationMode, setIsSimulationMode] = useState<boolean>(false);

  // --- 1. SYSTEM METRICS DATA ---
  const unconnectedMetrics: PlatformMetrics = {
    datasetsCount: 0,
    pipelinesCount: 0,
    aiTablesCount: 0,
    uptime: '0%',
  };

  const simulationMetrics: PlatformMetrics = {
    datasetsCount: 14,
    pipelinesCount: 38,
    aiTablesCount: 8,
    uptime: '99.94%',
  };

  const currentMetrics = isSimulationMode ? simulationMetrics : unconnectedMetrics;

  // --- 2. SERVICES DATA ---
  const unconnectedServices: ServiceHealth[] = [
    {
      id: 'fastapi',
      name: 'FastAPI Backend',
      status: 'offline',
      version: '1.0',
      lastCheck: 'Never',
      description: 'REST API Gateway hosting control plane, metadata catalogs, and RAG routes.',
      iconName: 'server',
    },
    {
      id: 'minio',
      name: 'MinIO Storage',
      status: 'offline',
      version: '2026.06.01',
      lastCheck: 'Never',
      description: 'S3 object store mapping Medallion raw, process, and curation layers.',
      iconName: 'hard-drive',
    },
    {
      id: 'spark',
      name: 'Apache Spark',
      status: 'offline',
      version: '3.5.1',
      lastCheck: 'Never',
      description: 'Distributed execution clusters merging and processing streaming Parquet data.',
      iconName: 'cpu',
    },
    {
      id: 'delta',
      name: 'Delta Lake',
      status: 'offline',
      version: '3.2.0',
      lastCheck: 'Never',
      description: 'ACID transactional logs safeguarding concurrent schema updates.',
      iconName: 'database',
    },
    {
      id: 'metadata',
      name: 'Metadata Catalog',
      status: 'offline',
      version: '1.2.0',
      lastCheck: 'Never',
      description: 'Central registry cataloging schema lineages, access controls, and table rules.',
      iconName: 'tags',
    },
    {
      id: 'ai-pipeline',
      name: 'AI Ready Pipeline',
      status: 'offline',
      version: '1.5.0',
      lastCheck: 'Never',
      description: 'Feature engineers masking PII data and storing embeddings for prompt retrieval.',
      iconName: 'workflow',
    },
    {
      id: 'vector',
      name: 'Vector Store (Reserved)',
      status: 'not_configured',
      version: 'N/A',
      lastCheck: 'N/A',
      description: 'Semantic vector search space reserved for prompt chunk indexing.',
      iconName: 'binary',
    },
    {
      id: 'scheduler',
      name: 'Scheduler / Airflow (Reserved)',
      status: 'not_configured',
      version: 'N/A',
      lastCheck: 'N/A',
      description: 'Automated workflow DAG compiler executing recurrent quality inspections.',
      iconName: 'clock',
    },
  ];

  const simulationServices: ServiceHealth[] = [
    {
      id: 'fastapi',
      name: 'FastAPI Backend',
      status: 'healthy',
      version: '1.0',
      lastCheck: '10 sec ago',
      description: 'REST API Gateway hosting control plane, metadata catalogs, and RAG routes.',
      iconName: 'server',
    },
    {
      id: 'minio',
      name: 'MinIO Storage',
      status: 'healthy',
      version: '2026.06.01',
      lastCheck: '12 sec ago',
      description: 'S3 object store mapping Medallion raw, process, and curation layers.',
      iconName: 'hard-drive',
    },
    {
      id: 'spark',
      name: 'Apache Spark',
      status: 'starting',
      version: '3.5.1',
      lastCheck: '20 sec ago',
      description: 'Distributed execution clusters merging and processing streaming Parquet data.',
      iconName: 'cpu',
    },
    {
      id: 'delta',
      name: 'Delta Lake',
      status: 'healthy',
      version: '3.2.0',
      lastCheck: '25 sec ago',
      description: 'ACID transactional logs safeguarding concurrent schema updates.',
      iconName: 'database',
    },
    {
      id: 'metadata',
      name: 'Metadata Catalog',
      status: 'healthy',
      version: '1.2.0',
      lastCheck: '30 sec ago',
      description: 'Central registry cataloging schema lineages, access controls, and table rules.',
      iconName: 'tags',
    },
    {
      id: 'ai-pipeline',
      name: 'AI Ready Pipeline',
      status: 'healthy',
      version: '1.5.0',
      lastCheck: '15 sec ago',
      description: 'Feature engineers masking PII data and storing embeddings for prompt retrieval.',
      iconName: 'workflow',
    },
    {
      id: 'vector',
      name: 'Vector Store (Reserved)',
      status: 'maintenance',
      version: '2.4.1-rc1',
      lastCheck: '1 min ago',
      description: 'Semantic vector search space reserved for prompt chunk indexing.',
      iconName: 'binary',
    },
    {
      id: 'scheduler',
      name: 'Scheduler / Airflow (Reserved)',
      status: 'not_configured',
      version: 'N/A',
      lastCheck: 'N/A',
      description: 'Automated workflow DAG compiler executing recurrent quality inspections.',
      iconName: 'clock',
    },
  ];

  const currentServices = isSimulationMode ? simulationServices : unconnectedServices;

  // --- 3. PIPELINE STAGES ---
  const unconnectedPipeline: PipelineStage[] = [
    { name: 'Upload', status: 'waiting' },
    { name: 'Ingestion', status: 'waiting' },
    { name: 'Spark', status: 'waiting' },
    { name: 'Delta', status: 'waiting' },
    { name: 'Metadata', status: 'waiting' },
    { name: 'AI Ready', status: 'waiting' },
    { name: 'Consumers', status: 'waiting' },
  ];

  const simulationPipeline: PipelineStage[] = [
    { name: 'Upload', status: 'completed' },
    { name: 'Ingestion', status: 'completed' },
    { name: 'Spark', status: 'running' },
    { name: 'Delta', status: 'waiting' },
    { name: 'Metadata', status: 'waiting' },
    { name: 'AI Ready', status: 'waiting' },
    { name: 'Consumers', status: 'waiting' },
  ];

  const currentPipeline = isSimulationMode ? simulationPipeline : unconnectedPipeline;

  // --- 4. RECENT PLATFORM EVENTS ---
  const unconnectedEvents: PlatformEvent[] = [
    {
      id: '1',
      title: 'Backend offline',
      description: 'Connection gateway refused at port 8000. FastAPI daemon inactive.',
      timestamp: 'Just now',
      type: 'error',
    },
    {
      id: '2',
      title: 'Waiting for first dataset',
      description: 'Pipeline listener idle. Awaiting file drops or external stream webhooks.',
      timestamp: '1 min ago',
      type: 'info',
    },
    {
      id: '3',
      title: 'No Spark jobs executed',
      description: 'Compute cluster idle. Zero executor instances registered.',
      timestamp: '5 min ago',
      type: 'warning',
    },
    {
      id: '4',
      title: 'Metadata service idle',
      description: 'No schema definitions or unified lineage assets synced yet.',
      timestamp: '10 min ago',
      type: 'info',
    },
    {
      id: '5',
      title: 'Platform initialized',
      description: 'Local development sandbox container started successfully.',
      timestamp: '1 hour ago',
      type: 'success',
    },
  ];

  const simulationEvents: PlatformEvent[] = [
    {
      id: 's1',
      title: 'Spark job "iot_stream" started',
      description: 'Compute cluster scaled to 4 active executor pods successfully.',
      timestamp: 'Just now',
      type: 'success',
    },
    {
      id: 's2',
      title: 'Delta ACID commit #883',
      description: 'Silver customer_pii_masked records written with schema verification checks.',
      timestamp: '2 min ago',
      type: 'info',
    },
    {
      id: 's3',
      title: 'Metadata synchronization complete',
      description: 'Successfully updated catalog rules with 5 conformed column types.',
      timestamp: '8 min ago',
      type: 'success',
    },
    {
      id: 's4',
      title: 'RAG Grounding indexing trigger',
      description: 'Embedding generation pipeline for transaction_curated launched.',
      timestamp: '15 min ago',
      type: 'info',
    },
    {
      id: 's5',
      title: 'Platform initialized',
      description: 'Local development sandbox container started successfully.',
      timestamp: '1 hour ago',
      type: 'success',
    },
  ];

  const currentEvents = isSimulationMode ? simulationEvents : unconnectedEvents;

  // Render Service Icon
  const renderIcon = (iconName: string) => {
    switch (iconName) {
      case 'server': return <Server className="w-4.5 h-4.5" />;
      case 'hard-drive': return <HardDrive className="w-4.5 h-4.5" />;
      case 'cpu': return <Cpu className="w-4.5 h-4.5" />;
      case 'database': return <Database className="w-4.5 h-4.5" />;
      case 'tags': return <Tags className="w-4.5 h-4.5" />;
      case 'workflow': return <Workflow className="w-4.5 h-4.5" />;
      case 'binary': return <Binary className="w-4.5 h-4.5" />;
      case 'clock': return <Clock className="w-4.5 h-4.5" />;
      default: return <Server className="w-4.5 h-4.5" />;
    }
  };

  // Render Status Badge
  const getStatusBadge = (status: ServiceHealth['status']) => {
    switch (status) {
      case 'healthy':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 font-sans">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Healthy
          </span>
        );
      case 'starting':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-500 border border-amber-500/20 font-sans">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
            Starting
          </span>
        );
      case 'offline':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-500 border border-rose-500/20 font-sans">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
            Offline
          </span>
        );
      case 'maintenance':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-500 border border-blue-500/20 font-sans">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
            Maintenance
          </span>
        );
      case 'not_configured':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-500/15 text-muted-foreground border border-border font-sans">
            <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground" />
            Reserved
          </span>
        );
    }
  };

  // Render pipeline state bullet
  const getPipelineStatusBadge = (status: PipelineStage['status']) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/10 text-emerald-500 uppercase tracking-wider font-mono">
            Completed
          </span>
        );
      case 'running':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold bg-blue-500/10 text-blue-500 uppercase tracking-wider animate-pulse font-mono">
            Running
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-500/10 text-rose-500 uppercase tracking-wider font-mono">
            Failed
          </span>
        );
      case 'waiting':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold bg-muted text-muted-foreground uppercase tracking-wider font-mono">
            Waiting
          </span>
        );
    }
  };

  return (
    <div id="platform-health-dashboard-section" className="space-y-8 font-sans">
      
      {/* HEADER ROW WITH SIMULATION TOGGLE */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1 border-b border-border/60">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-500" />
            <h2 id="platform-health-title" className="text-lg font-bold tracking-tight text-foreground">
              Platform Health
            </h2>
          </div>
          <p id="platform-health-subtitle" className="text-xs text-muted-foreground">
            Monitor the health of every core platform component.
          </p>
        </div>

        {/* Dynamic connection indicator switch */}
        <div className="flex items-center gap-3 bg-muted/55 border border-border rounded-xl px-3 py-1.5 self-start sm:self-auto shadow-xs">
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${isSimulationMode ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
            <span className="text-[10px] font-bold font-mono text-foreground uppercase tracking-wider">
              {isSimulationMode ? 'Simulation Mode' : 'Sandbox Disconnected'}
            </span>
          </div>
          <div className="h-4 w-px bg-border" />
          <button
            onClick={() => setIsSimulationMode(!isSimulationMode)}
            className="text-[10px] font-bold text-blue-600 dark:text-blue-400 hover:text-blue-500 flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSimulationMode ? 'animate-spin' : ''}`} />
            {isSimulationMode ? 'Stop Demo' : 'Simulate Connected'}
          </button>
        </div>
      </div>

      {/* SYSTEM METRICS ROW (4 Compact Cards) */}
      <div id="system-metrics-grid" className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-card text-card-foreground border border-border p-4.5 rounded-xl flex items-center justify-between shadow-xs transition-all hover:border-border/80">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Datasets</span>
            <span className="text-2xl font-bold font-mono tracking-tight text-foreground">
              {currentMetrics.datasetsCount}
            </span>
          </div>
          <div className="p-2.5 bg-blue-500/10 text-blue-500 rounded-lg">
            <Database className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-card text-card-foreground border border-border p-4.5 rounded-xl flex items-center justify-between shadow-xs transition-all hover:border-border/80">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Pipelines</span>
            <span className="text-2xl font-bold font-mono tracking-tight text-foreground">
              {currentMetrics.pipelinesCount}
            </span>
          </div>
          <div className="p-2.5 bg-indigo-500/10 text-indigo-500 rounded-lg">
            <Workflow className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-card text-card-foreground border border-border p-4.5 rounded-xl flex items-center justify-between shadow-xs transition-all hover:border-border/80">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">AI Ready Tables</span>
            <span className="text-2xl font-bold font-mono tracking-tight text-foreground">
              {currentMetrics.aiTablesCount}
            </span>
          </div>
          <div className="p-2.5 bg-emerald-500/10 text-emerald-500 rounded-lg">
            <Layers className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-card text-card-foreground border border-border p-4.5 rounded-xl flex items-center justify-between shadow-xs transition-all hover:border-border/80">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">Platform Uptime</span>
            <span className="text-2xl font-bold font-mono tracking-tight text-foreground">
              {currentMetrics.uptime}
            </span>
          </div>
          <div className="p-2.5 bg-amber-500/10 text-amber-500 rounded-lg">
            <Activity className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* PROFESSONAL EMPTY STATE MESSAGE */}
      {!isSimulationMode && (
        <div id="unconnected-empty-state-card" className="bg-amber-500/5 text-foreground border border-amber-500/25 rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center gap-6 shadow-xs animate-fadeIn">
          <div className="p-4 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-full flex-shrink-0 animate-pulse">
            <AlertCircle className="w-8 h-8" />
          </div>
          <div className="space-y-3.5 text-center md:text-left flex-1">
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-amber-800 dark:text-amber-400 font-sans">
                No backend services connected
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed mt-1.5 font-light">
                No backend services are connected yet. This dashboard will automatically populate once FastAPI, MinIO, Apache Spark and Delta Lake are integrated.
              </p>
            </div>
            <button
              onClick={() => setIsSimulationMode(true)}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-amber-500 hover:bg-amber-600 text-white dark:text-slate-950 text-[11px] font-bold uppercase rounded-lg shadow-sm transition-all active:scale-[0.985] cursor-pointer"
            >
              Enable Demo Simulation
            </button>
          </div>
        </div>
      )}

      {/* CORE SERVICES STATUS cards */}
      <div className="space-y-4">
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider font-sans">
          Platform Components Status ({currentServices.length})
        </h3>
        <div id="health-services-grid" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {currentServices.map((service) => (
            <div
              key={service.id}
              className={`bg-card text-card-foreground border border-border rounded-xl p-4 flex flex-col justify-between shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${
                service.status === 'offline' ? 'opacity-70 hover:opacity-100' : ''
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="p-1.5 bg-blue-500/5 text-blue-500 rounded-lg">
                    {renderIcon(service.iconName)}
                  </div>
                  {getStatusBadge(service.status)}
                </div>
                
                <div>
                  <h4 className="text-xs font-bold text-foreground truncate">
                    {service.name}
                  </h4>
                  <p className="text-[10px] text-muted-foreground mt-1 leading-relaxed line-clamp-3">
                    {service.description}
                  </p>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-border/50 flex items-center justify-between text-[9px] font-mono font-bold text-muted-foreground uppercase">
                <span>Ver: {service.version}</span>
                <span>Check: {service.lastCheck}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* PIPELINE STATUS HORIZONTAL DIAGRAM */}
      <div id="pipeline-status-container" className="bg-card text-card-foreground border border-border rounded-xl p-5 shadow-xs space-y-5">
        <div className="space-y-1">
          <h3 className="text-xs font-bold text-foreground uppercase tracking-wider font-sans flex items-center gap-1.5">
            <Workflow className="w-3.5 h-3.5 text-blue-500" /> Pipeline Flow Lineage
          </h3>
          <p className="text-xs text-muted-foreground">
            Linear sequence of transformation check-ins mapping raw S3 drop ingestion to final AI-ready embedding consumers.
          </p>
        </div>

        {/* Horizontal scroll container on mobile, flex row on desktop */}
        <div className="overflow-x-auto pb-2 scrollbar-none">
          <div className="flex items-center min-w-[700px] py-2 px-1">
            {currentPipeline.map((stage, idx) => {
              const isLast = idx === currentPipeline.length - 1;
              return (
                <React.Fragment key={stage.name}>
                  {/* Stage Node */}
                  <div className="flex flex-col items-center space-y-2 flex-1">
                    <div className="relative">
                      <div className={`w-8 h-8 rounded-full border flex items-center justify-center font-bold text-xs font-mono transition-all duration-300 ${
                        stage.status === 'completed'
                          ? 'bg-emerald-500/10 border-emerald-500 text-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.15)]'
                          : stage.status === 'running'
                          ? 'bg-blue-500/10 border-blue-500 text-blue-500 animate-pulse shadow-[0_0_12px_rgba(59,130,246,0.25)]'
                          : stage.status === 'failed'
                          ? 'bg-rose-500/10 border-rose-500 text-rose-500'
                          : 'bg-muted border-border text-muted-foreground'
                      }`}>
                        {idx + 1}
                      </div>
                    </div>
                    
                    <div className="text-center space-y-0.5">
                      <span className="text-[11px] font-bold text-foreground block">
                        {stage.name}
                      </span>
                      {getPipelineStatusBadge(stage.status)}
                    </div>
                  </div>

                  {/* Arrow Connector */}
                  {!isLast && (
                    <div className="flex items-center justify-center px-2 flex-shrink-0">
                      <ArrowRight className={`w-4 h-4 ${
                        stage.status === 'completed' ? 'text-emerald-500/80' : 'text-muted-foreground/35'
                      }`} />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>

      {/* RECENT PLATFORM EVENTS TIMELINE */}
      <div id="recent-events-timeline-container" className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-card text-card-foreground border border-border rounded-xl p-5 shadow-xs space-y-5">
          <div className="space-y-1">
            <h3 className="text-xs font-bold text-foreground uppercase tracking-wider font-sans flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-blue-500" /> Platform Diagnostics Feed
            </h3>
            <p className="text-xs text-muted-foreground">
              Real-time audit history of data mutations, pipeline triggers, and cloud environment alerts.
            </p>
          </div>

          <div className="relative border-l border-border pl-5 space-y-5">
            {currentEvents.map((evt) => (
              <div key={evt.id} className="relative">
                {/* Dot indicator */}
                <div className={`absolute -left-[24.5px] mt-1.5 w-2 h-2 rounded-full border-2 border-card ${
                  evt.type === 'error'
                    ? 'bg-rose-500'
                    : evt.type === 'warning'
                    ? 'bg-amber-500'
                    : evt.type === 'success'
                    ? 'bg-emerald-500'
                    : 'bg-blue-500'
                }`} />
                
                <div className="text-xs font-sans space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-foreground text-xs leading-none">
                      {evt.title}
                    </span>
                    <span className="text-[9px] text-muted-foreground font-mono font-bold uppercase bg-muted/60 px-1 rounded border border-border/40">
                      {evt.timestamp}
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">
                    {evt.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Integration Instructions helper card */}
        <div className="bg-card text-card-foreground border border-border rounded-xl p-5 shadow-xs flex flex-col justify-between">
          <div className="space-y-4">
            <div className="space-y-1">
              <h3 className="text-xs font-bold text-foreground uppercase tracking-wider font-sans flex items-center gap-1.5">
                <HelpCircle className="w-3.5 h-3.5 text-blue-500" /> Integration Specs
              </h3>
              <p className="text-xs text-muted-foreground">
                Developer guidance on consuming FastAPI state endpoints into this component.
              </p>
            </div>

            <div className="space-y-3.5 pt-2 text-xs">
              <div className="space-y-1">
                <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">1. GET /api/health</span>
                <p className="text-[11px] text-muted-foreground leading-relaxed">
                  Fetches an array of component status nodes. Each entry matches the service layout schema.
                </p>
              </div>

              <div className="space-y-1">
                <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">2. API Schema Contract</span>
                <pre className="p-2.5 bg-muted rounded-lg text-[10px] font-mono text-foreground border border-border overflow-x-auto leading-relaxed">
{`{
  "service": "Apache Spark",
  "status": "healthy",
  "version": "3.5.1",
  "lastCheck": "10s ago",
  "description": "..."
}`}
                </pre>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-border/50 text-[10px] text-muted-foreground italic">
            Developed to consume real-time FastAPI endpoints without design modifications.
          </div>
        </div>
      </div>

    </div>
  );
};
