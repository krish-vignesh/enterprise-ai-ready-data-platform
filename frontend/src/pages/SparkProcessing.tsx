import React, { useState, useEffect } from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PageHeader, Card, Button, Badge, ProgressBar, InsightCard } from '../components/UI';
import { motion, AnimatePresence } from 'motion/react';
import {
  Cpu,
  Play,
  Layers,
  Activity,
  HardDrive,
  Workflow,
  CheckCircle2,
  RefreshCw,
  Clock,
  Network,
  GitCommit,
  GitPullRequest,
  Zap,
  Server,
  CornerDownRight,
  Database,
  ArrowRightLeft
} from 'lucide-react';

interface DagStage {
  id: number;
  name: string;
  subText: string;
  catalystStep: string;
  enterpriseDetail: string;
  inputSource: string;
  outputTarget: string;
}

export const SparkProcessing: React.FC = () => {
  const { sparkJobs, runSparkProcessing } = usePlatform();
  const [selectedDagStage, setSelectedDagStage] = useState<number>(0);

  const runningJobs = sparkJobs.filter((j) => j.status === 'RUNNING');
  const isAnyJobRunning = runningJobs.length > 0;
  const activeJob = runningJobs[0] || null;

  // Simulate dynamic cluster telemetry when jobs are running
  const [telemetry, setTelemetry] = useState({
    cpuUtilization: 4,
    shuffleSpeed: 0,
    networkI_O: 12,
    diskReadWrite: 0
  });

  useEffect(() => {
    let interval: any;
    if (isAnyJobRunning) {
      interval = setInterval(() => {
        setTelemetry({
          cpuUtilization: Math.floor(Math.random() * 20) + 78, // 78% - 98%
          shuffleSpeed: Math.floor(Math.random() * 150) + 250, // 250 - 400 MB/s
          networkI_O: Math.floor(Math.random() * 80) + 120, // 120 - 200 MB/s
          diskReadWrite: Math.floor(Math.random() * 200) + 300 // 300 - 500 MB/s
        });
      }, 800);
    } else {
      setTelemetry({
        cpuUtilization: 3, // Idle state
        shuffleSpeed: 0,
        networkI_O: 1,
        diskReadWrite: 0
      });
    }
    return () => clearInterval(interval);
  }, [isAnyJobRunning]);

  const dagStages: DagStage[] = [
    {
      id: 0,
      name: 'Stage 0: FileScanParquet',
      subText: 'Lazy evaluation scan of raw storage partitions',
      catalystStep: 'Logical Analysis & Partition Pruning',
      enterpriseDetail: 'Spark reads file metadata headers first without loading records to memory. Pushdown filters discard files outside partition ranges, cutting IO times by 90%.',
      inputSource: 'S3 Raw Landing Bucket (Bronze Zone)',
      outputTarget: 'Executor JVM Memory Partition Arcs'
    },
    {
      id: 1,
      name: 'Stage 1: FilterAndNullValidate',
      subText: 'Row-level filtering of corrupted and PII fields',
      catalystStep: 'Physical Execution Generation',
      enterpriseDetail: 'Spark generates raw Java bytecode targeting selected columns in memory arrays. Discards rows where essential identifiers are empty or broken.',
      inputSource: 'Executor JVM Memory Partition Arcs',
      outputTarget: 'Deduplication Cache Blocks'
    },
    {
      id: 2,
      name: 'Stage 2: HashAggregate / Shuffle',
      subText: 'Deduplicating rows across partitions',
      catalystStep: 'Exchange Partition Shuffle Plan',
      enterpriseDetail: 'Requires a Shuffle exchange across worker nodes. Rows with similar partition hash keys are copied across networks to a single node to filter duplicates.',
      inputSource: 'Deduplication Cache Blocks',
      outputTarget: 'Shuffled Clean Partition Arrays'
    },
    {
      id: 3,
      name: 'Stage 3: SaveIntoDeltaLake',
      subText: 'Final ACID transactions write back to disk',
      catalystStep: 'Transactional File Commit Operation',
      enterpriseDetail: 'Writes cleaned rows as compressed snappy Parquet files. Appends a transaction version ID to the Delta Lake ACID log directory.',
      inputSource: 'Shuffled Clean Partition Arrays',
      outputTarget: 'Delta Lake Directory (Silver/Gold Zone)'
    }
  ];

  const activeDagStageData = dagStages.find(s => s.id === selectedDagStage) || dagStages[0];

  return (
    <div id="spark-processing-page-container" className="space-y-10 animate-fadeIn font-sans pb-10">
      <PageHeader
        id="spark-header-block"
        title="Distributed Spark Compute Engine"
        description="Monitor distributed in-memory clusters executing logical optimizations to convert raw staging files into fully conformed transactional Delta tables."
      />

      {/* CLUSTER TELEMETRY PANEL */}
      <div id="spark-cluster-stats" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card id="spark-stat-cores" className="relative overflow-hidden flex items-center gap-4 border border-slate-200/80 dark:border-slate-850">
          <div className="p-3 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-xl">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Allocated Cores</span>
            <span className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5 block">
              {isAnyJobRunning ? '64 JVM Cores' : '8 Cores (Idle)'}
            </span>
          </div>
          {isAnyJobRunning && (
            <span className="absolute top-2 right-2 flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
          )}
        </Card>

        <Card id="spark-stat-ram" className="flex items-center gap-4 border border-slate-200/80 dark:border-slate-850">
          <div className="p-3 bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 rounded-xl">
            <Activity className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">In-Memory Utilization</span>
            <span className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5 block">
              {isAnyJobRunning ? '142 GB / 192 GB' : '1.2 GB / 32 GB'}
            </span>
          </div>
        </Card>

        <Card id="spark-stat-active" className="flex items-center gap-4 border border-slate-200/80 dark:border-slate-850">
          <div className="p-3 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-xl">
            <RefreshCw className={`w-5 h-5 ${isAnyJobRunning ? 'animate-spin' : ''}`} />
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Cluster Workers</span>
            <span className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5 block">
              {isAnyJobRunning ? '4 Executors Active' : 'Cluster Sleeping'}
            </span>
          </div>
        </Card>

        <Card id="spark-stat-disk" className="flex items-center gap-4 border border-slate-200/80 dark:border-slate-850">
          <div className="p-3 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-xl">
            <HardDrive className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Disk & Network I/O</span>
            <span className="text-lg font-bold font-mono text-slate-900 dark:text-white mt-0.5 block">
              {isAnyJobRunning ? `${telemetry.diskReadWrite} MB/s Avg` : '0 MB/s (Idle)'}
            </span>
          </div>
        </Card>
      </div>

      {/* CLUSTER ARCHITECTURE VISUALIZER & INTERACTIVE DAG */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* LEFT: Distributed Spark Cluster Diagram */}
        <div className="lg:col-span-7 flex flex-col">
          <Card id="spark-cluster-map-card" className="flex-1 flex flex-col justify-between p-6 border-slate-200/80 dark:border-slate-850">
            <div className="mb-6">
              <span className="text-[9px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider bg-blue-500/10 px-2 py-0.5 rounded">
                Physical Distribution Layer
              </span>
              <h3 className="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider mt-2">
                Distributed In-Memory Cluster Map
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Visualizes coordination between the Driver (Master) and Executor (Workers) executing task loops.
              </p>
            </div>

            {/* Topology Diagram Container */}
            <div className="bg-slate-50/50 dark:bg-[#0B1329]/50 border border-slate-100 dark:border-slate-850 p-6 rounded-2xl flex flex-col gap-6 relative overflow-hidden">
              
              {/* Dynamic Task Pulses when Job Runs */}
              {isAnyJobRunning && (
                <div className="absolute inset-0 pointer-events-none">
                  {/* Glowing pulses traveling down from driver to worker */}
                  <div className="absolute left-1/4 top-1/3 w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0s' }} />
                  <div className="absolute left-2/4 top-1/3 w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <div className="absolute left-3/4 top-1/3 w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0.4s' }} />
                </div>
              )}

              {/* Driver / Master Node */}
              <div className="flex justify-center">
                <div className="w-full max-w-sm bg-white dark:bg-[#1E293B]/70 border border-slate-200 dark:border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-xs">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-600 rounded-lg text-white">
                      <Zap className="w-4 h-4" />
                    </div>
                    <div className="text-left">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Driver Node</span>
                      <h4 className="text-xs font-bold text-slate-800 dark:text-slate-100 font-mono">spark-master-driver</h4>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-[9px] px-2 py-0.5 font-bold uppercase rounded bg-blue-500/10 text-blue-600 dark:text-blue-400">
                      Coordinating
                    </span>
                  </div>
                </div>
              </div>

              {/* Connections Arrow */}
              <div className="flex justify-center items-center gap-4 text-slate-300 dark:text-slate-700">
                <div className="w-px h-6 bg-slate-200 dark:bg-slate-800" />
              </div>

              {/* Worker Nodes Layout */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Worker Node 1 */}
                <div className="bg-white dark:bg-[#1E293B]/70 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-3.5 shadow-xs">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-50 dark:border-slate-850/60">
                    <div className="flex items-center gap-2">
                      <Server className="w-3.5 h-3.5 text-indigo-500" />
                      <h5 className="text-[10px] font-bold text-slate-700 dark:text-slate-200 font-mono">spark-worker-01</h5>
                    </div>
                    <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded ${isAnyJobRunning ? 'bg-emerald-500/15 text-emerald-600' : 'bg-slate-100 text-slate-400'}`}>
                      {isAnyJobRunning ? 'RUNNING' : 'IDLE'}
                    </span>
                  </div>

                  {/* Executors */}
                  <div className="space-y-2.5">
                    {/* Executor JVM A */}
                    <div className="p-2.5 bg-slate-50 dark:bg-[#0B1329]/50 border border-slate-100 dark:border-slate-850 rounded-lg space-y-1.5 text-left">
                      <div className="flex justify-between items-center text-[9px] font-bold text-slate-500 uppercase tracking-wider">
                        <span>Executor JVM A</span>
                        <span className="font-mono text-blue-500 font-extrabold">{isAnyJobRunning ? '84% CPU' : 'Idle'}</span>
                      </div>
                      <div className="w-full h-1 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-500 transition-all duration-1000 rounded-full"
                          style={{ width: isAnyJobRunning ? '84%' : '2%' }}
                        />
                      </div>
                    </div>

                    {/* Executor JVM B */}
                    <div className="p-2.5 bg-slate-50 dark:bg-[#0B1329]/50 border border-slate-100 dark:border-slate-850 rounded-lg space-y-1.5 text-left">
                      <div className="flex justify-between items-center text-[9px] font-bold text-slate-500 uppercase tracking-wider">
                        <span>Executor JVM B</span>
                        <span className="font-mono text-indigo-500 font-extrabold">{isAnyJobRunning ? '78% CPU' : 'Idle'}</span>
                      </div>
                      <div className="w-full h-1 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-indigo-500 transition-all duration-1000 rounded-full"
                          style={{ width: isAnyJobRunning ? '78%' : '2%' }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Worker Node 2 */}
                <div className="bg-white dark:bg-[#1E293B]/70 border border-slate-200 dark:border-slate-800 p-4 rounded-xl space-y-3.5 shadow-xs">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-50 dark:border-slate-850/60">
                    <div className="flex items-center gap-2">
                      <Server className="w-3.5 h-3.5 text-indigo-500" />
                      <h5 className="text-[10px] font-bold text-slate-700 dark:text-slate-200 font-mono">spark-worker-02</h5>
                    </div>
                    <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded ${isAnyJobRunning ? 'bg-emerald-500/15 text-emerald-600' : 'bg-slate-100 text-slate-400'}`}>
                      {isAnyJobRunning ? 'RUNNING' : 'IDLE'}
                    </span>
                  </div>

                  {/* Executors */}
                  <div className="space-y-2.5">
                    {/* Executor JVM C */}
                    <div className="p-2.5 bg-slate-50 dark:bg-[#0B1329]/50 border border-slate-100 dark:border-slate-850 rounded-lg space-y-1.5 text-left">
                      <div className="flex justify-between items-center text-[9px] font-bold text-slate-500 uppercase tracking-wider">
                        <span>Executor JVM C</span>
                        <span className="font-mono text-blue-500 font-extrabold">{isAnyJobRunning ? '91% CPU' : 'Idle'}</span>
                      </div>
                      <div className="w-full h-1 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-500 transition-all duration-1000 rounded-full"
                          style={{ width: isAnyJobRunning ? '91%' : '2%' }}
                        />
                      </div>
                    </div>

                    {/* Executor JVM D */}
                    <div className="p-2.5 bg-slate-50 dark:bg-[#0B1329]/50 border border-slate-100 dark:border-slate-850 rounded-lg space-y-1.5 text-left">
                      <div className="flex justify-between items-center text-[9px] font-bold text-slate-500 uppercase tracking-wider">
                        <span>Executor JVM D</span>
                        <span className="font-mono text-indigo-500 font-extrabold">{isAnyJobRunning ? '76% CPU' : 'Idle'}</span>
                      </div>
                      <div className="w-full h-1 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-indigo-500 transition-all duration-1000 rounded-full"
                          style={{ width: isAnyJobRunning ? '76%' : '2%' }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

              </div>

              {/* Network Shuffle Zone */}
              <div className="p-3 bg-indigo-500/5 border border-indigo-500/15 rounded-xl flex items-center justify-between mt-2">
                <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
                  <ArrowRightLeft className={`w-4 h-4 ${isAnyJobRunning ? 'animate-bounce' : ''}`} />
                  <span className="text-[10px] font-bold uppercase tracking-wider">Exchange Shuffle Network</span>
                </div>
                <span className="text-[10px] font-mono font-medium text-slate-600 dark:text-slate-450">
                  {isAnyJobRunning ? `${telemetry.shuffleSpeed} MB/s Exchange` : '0 MB/s'}
                </span>
              </div>

            </div>
          </Card>
        </div>

        {/* RIGHT: Interactive Catalyst DAG Optimizer */}
        <div className="lg:col-span-5 flex flex-col space-y-6">
          <Card id="spark-dag-viz-card" className="border-slate-200/80 dark:border-slate-850">
            <div className="space-y-1 mb-6">
              <span className="text-[9px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider bg-indigo-500/10 px-2 py-0.5 rounded">
                Logical Plan optimizer
              </span>
              <h3 className="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider mt-2 flex items-center gap-1.5">
                <Network className="w-4 h-4 text-blue-500" /> Catalyst DAG Pipeline
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Click a stage block below to trace Catalyst optimization mechanics.
              </p>
            </div>

            {/* Interactive DAG Blocks */}
            <div className="space-y-3.5">
              {dagStages.map((stage) => {
                const isSelected = selectedDagStage === stage.id;
                return (
                  <div
                    key={stage.id}
                    onClick={() => setSelectedDagStage(stage.id)}
                    className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all duration-150 relative ${
                      isSelected
                        ? 'border-indigo-500 bg-indigo-500/5 shadow-xs'
                        : 'border-slate-150 dark:border-slate-850 bg-white dark:bg-[#111A2E]/40 hover:bg-slate-50 dark:hover:bg-[#111A2E]/60'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[10px] font-bold text-slate-700 dark:text-slate-300">{stage.name}</span>
                      {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />}
                    </div>
                    <span className="text-[10px] text-slate-400 block mt-1">{stage.subText}</span>
                  </div>
                );
              })}
            </div>

            {/* Stage Detail Details box */}
            <div className="mt-5 p-4 bg-slate-50/50 dark:bg-[#0B1329]/50 border border-slate-200/50 dark:border-slate-850 rounded-xl space-y-3 text-left">
              <div className="flex items-center gap-1.5 text-indigo-600 dark:text-indigo-400 border-b border-slate-100 dark:border-slate-800 pb-2">
                <CornerDownRight className="w-3.5 h-3.5" />
                <span className="text-[10px] font-bold uppercase tracking-wider">Catalyst Optimization detail</span>
              </div>
              <div className="space-y-2">
                <div>
                  <span className="text-[9px] uppercase font-bold text-slate-400 block">Optimizer Step</span>
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{activeDagStageData.catalystStep}</span>
                </div>
                <div>
                  <span className="text-[9px] uppercase font-bold text-slate-400 block">Enterprise Mechanism</span>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-sans">{activeDagStageData.enterpriseDetail}</p>
                </div>
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <div>
                    <span className="text-[9px] uppercase font-bold text-slate-400 block">Input Source</span>
                    <span className="text-[10px] text-slate-600 dark:text-slate-400 font-mono truncate block">{activeDagStageData.inputSource}</span>
                  </div>
                  <div>
                    <span className="text-[9px] uppercase font-bold text-slate-400 block">Output Target</span>
                    <span className="text-[10px] text-slate-600 dark:text-slate-400 font-mono truncate block">{activeDagStageData.outputTarget}</span>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>

      </div>

      {/* ACTIVE SPARK JOBS QUEUE */}
      <Card id="spark-jobs-table-panel" className="border-slate-200/80 dark:border-slate-850">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 mb-6 pb-4 border-b border-slate-50 dark:border-slate-850/60">
          <div>
            <h3 className="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
              Cluster Execution Queue
            </h3>
            <p className="text-xs text-slate-400">
              Trigger Spark jobs to process active database queues into conformed Delta tables.
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {sparkJobs.map((job) => (
            <div
              key={job.id}
              className="p-4 bg-white dark:bg-[#111A2E]/50 border border-slate-200/80 dark:border-slate-850 rounded-xl flex flex-col space-y-4 hover:shadow-xs transition-all"
            >
              <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg">
                    <Cpu className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-xs font-bold text-slate-800 dark:text-slate-200 font-mono">
                        {job.name}
                      </h4>
                      <Badge
                        id={`badge-spark-${job.id}`}
                        content={job.status}
                        variant={
                          job.status === 'COMPLETED'
                            ? 'success'
                            : job.status === 'RUNNING'
                            ? 'warning'
                            : job.status === 'PENDING'
                            ? 'neutral'
                            : 'danger'
                        }
                      />
                    </div>
                    <div className="flex flex-wrap items-center gap-3 mt-1 text-[10px] text-slate-400 font-mono">
                      <span>Job ID: <strong>{job.id}</strong></span>
                      <span>•</span>
                      <span>Cores: <strong>{job.cores}</strong></span>
                      <span>•</span>
                      <span>JVM RAM: <strong>{job.memory}</strong></span>
                    </div>
                  </div>
                </div>

                {job.status === 'PENDING' && (
                  <Button
                    id={`run-spark-btn-${job.id}`}
                    variant="primary"
                    size="sm"
                    icon={<Play className="w-3 text-white fill-white" />}
                    onClick={() => runSparkProcessing(job.id)}
                    className="hover:scale-[1.03]"
                  >
                    Trigger Job Compute
                  </Button>
                )}
              </div>

              {job.status === 'RUNNING' && (
                <div className="space-y-2.5 animate-pulse">
                  <ProgressBar
                    id={`spark-prog-${job.id}`}
                    progress={job.progress}
                    statusLabel="Active Spark SQL Thread pool: reading and sorting table parquet partitions..."
                  />
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-[10px] font-mono text-slate-400 pt-1.5 border-t border-slate-50 dark:border-slate-850/60 mt-1">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-blue-500" />
                      <span>Stage 0: Scan S3 Parquet</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-blue-500" />
                      <span>Stage 1: Validate Null Schemas</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${job.progress >= 85 ? 'bg-blue-500 animate-ping' : 'bg-slate-300'}`} />
                      <span className={job.progress >= 85 ? 'text-blue-500 font-bold' : ''}>Stage 2: Write Transaction Log</span>
                    </div>
                  </div>
                </div>
              )}

              {job.status === 'COMPLETED' && (
                <div className="flex items-start sm:items-center gap-3 text-xs text-emerald-700 dark:text-emerald-400 bg-emerald-500/5 dark:bg-emerald-950/20 p-3.5 rounded-xl border border-emerald-100/45 dark:border-emerald-900/30 font-sans">
                  <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-500 mt-0.5 sm:mt-0" />
                  <span className="leading-relaxed">
                    <strong>Transaction success:</strong> Spark executor completed deduplications and committed conformed datasets to S3 directory. Unified metastore updated successfully.
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* STRUCTURED ARCHITECTURE INSIGHT CARD */}
      <InsightCard
        id="spark-architecture-insight"
        title="Apache Spark In-Memory Master-Worker Coordination"
        purpose="Loads physical partition files into distributed executor RAM heaps, enabling high-performance lazily evaluated pipeline calculations."
        enterpriseProblem="Single-server database instances cannot scale. Loading multi-gigabyte transactional tables triggers system-level out-of-memory crashes."
        azureEquivalent="Azure Databricks Ephemeral Clusters, Azure Synapse Analytics Spark Jobs"
        enterpriseExample="A dynamic 20-node serverless Databricks cluster spins up, parses 500 million raw customer logs, merges updates, and scales down to zero."
        whyExists="Horizontally scales pipeline compute costs by isolating ephemeral processing clusters from permanent physical filesystems."
      />
    </div>
  );
};
