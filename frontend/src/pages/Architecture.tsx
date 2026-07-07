import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { PageHeader, Card, Badge } from '../components/UI';
import {
  Network,
  Database,
  Shuffle,
  Layers,
  Cpu,
  Triangle,
  ShieldCheck,
  Tags,
  BrainCircuit,
  Server,
  ArrowRight,
  ChevronRight,
  Info,
  ShieldAlert,
  CloudLightning,
  Workflow,
  Sparkles,
  CheckCircle2
} from 'lucide-react';

interface Stage {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  borderColor: string;
  glowColor: string;
  purpose: string;
  enterpriseProblem: string;
  azureEquivalent: string;
  enterpriseExample: string;
  whyExists: string;
}

export const Architecture: React.FC = () => {
  const [activeStageId, setActiveStageId] = useState<string>('sources');

  const stages: Stage[] = [
    {
      id: 'sources',
      label: '1. Sources',
      icon: Database,
      color: 'text-amber-500 bg-amber-500/10',
      borderColor: 'border-amber-500/30',
      glowColor: 'shadow-amber-500/10',
      purpose: 'Captures and isolates business events directly from operational and transactional databases.',
      enterpriseProblem: 'Operational DBs are optimized for transaction throughput (OLTP) and will degrade in performance or crash under analytical workloads.',
      azureEquivalent: 'Azure SQL Database, Cosmos DB, SaaS Connectors',
      enterpriseExample: 'Retail POS terminals logging sales across 5,000 global storefronts in real-time.',
      whyExists: 'Serves as the immutable origin of truth that feeds downstream analytical and warehouse systems.'
    },
    {
      id: 'ingestion',
      label: '2. Ingestion',
      icon: Shuffle,
      color: 'text-blue-500 bg-blue-500/10',
      borderColor: 'border-blue-500/30',
      glowColor: 'shadow-blue-500/10',
      purpose: 'Streams or copies transaction events over networks into centralized staging layers.',
      enterpriseProblem: 'Unstructured schemas, network latency spikes, and varying formats cause message drops and inconsistent delivery.',
      azureEquivalent: 'Azure Data Factory (ADF), Azure Event Hubs, Confluent Kafka',
      enterpriseExample: 'Data Factory triggers hourly copy pipelines moving conformed JSON event records over secure WAN channels.',
      whyExists: 'Decouples operational systems from analytics pipelines, ensuring transaction safety.'
    },
    {
      id: 'minio',
      label: '3. Storage Zone',
      icon: Layers,
      color: 'text-sky-500 bg-sky-500/10',
      borderColor: 'border-sky-500/30',
      glowColor: 'shadow-sky-500/10',
      purpose: 'Hosts a secure, scalable object lakehouse storage layer for storing raw semi-structured files.',
      enterpriseProblem: 'Storing terabytes of raw unstructured JSON directly inside traditional SQL tables is prohibitively expensive.',
      azureEquivalent: 'Azure Data Lake Storage Gen2 (ADLS)',
      enterpriseExample: 'Raw JSON files stored in secure, hierarchical object storage buckets organized by date and pipeline ID.',
      whyExists: 'Serves as an immutable historic archive enabling low-cost data recovery and schema-on-read querying.'
    },
    {
      id: 'spark',
      label: '4. Spark Compute',
      icon: Cpu,
      color: 'text-indigo-500 bg-indigo-500/10',
      borderColor: 'border-indigo-500/30',
      glowColor: 'shadow-indigo-500/10',
      purpose: 'Performs high-speed distributed memory calculations, column selections, and transformations.',
      enterpriseProblem: 'Single-node database engines fail to process terabytes of raw transaction records, triggering out-of-memory crashes.',
      azureEquivalent: 'Azure Databricks Compute, Synapse Spark Pools',
      enterpriseExample: 'A distributed 50-node Spark cluster cleans and parses 100 million active sales rows in less than 3 minutes.',
      whyExists: 'Guarantees horizontal scalability, allowing execution times to remain flat even as dataset sizes double.'
    },
    {
      id: 'delta',
      label: '5. Delta ACID',
      icon: Triangle,
      color: 'text-emerald-500 bg-emerald-500/10',
      borderColor: 'border-emerald-500/30',
      glowColor: 'shadow-emerald-500/10',
      purpose: 'Enforces ACID transaction boundaries, schema schema validation, and snapshot history logs.',
      enterpriseProblem: 'Simultaneous pipeline writes corrupt raw storage directories, causing users to read incomplete datasets.',
      azureEquivalent: 'Azure Synapse Delta Tables, Fabric Lakehouse',
      enterpriseExample: 'An automated financial auditor executes historical delta queries using built-in table time-travel tags.',
      whyExists: 'Bridges raw file-system storage and structured transactional databases, making standard files behave like robust tables.'
    },
    {
      id: 'quality',
      label: '6. Data Quality',
      icon: ShieldCheck,
      color: 'text-teal-500 bg-teal-500/10',
      borderColor: 'border-teal-500/30',
      glowColor: 'shadow-teal-500/10',
      purpose: 'Validates dataset structures against rigorous null constraints and structural thresholds.',
      enterpriseProblem: 'Corrupted records and null parameters bypass landing files, breaking executive dashboard formulas and analytics models.',
      azureEquivalent: 'Great Expectations Framework, Azure Purview Data Quality',
      enterpriseExample: 'An automated rules engine isolates records lacking a valid Customer ID into quarantine buckets.',
      whyExists: 'Guarantees that downstream dashboards and executive models are fed structurally and mathematically clean datasets.'
    },
    {
      id: 'metadata',
      label: '7. Metadata Catalog',
      icon: Tags,
      color: 'text-purple-500 bg-purple-500/10',
      borderColor: 'border-purple-500/30',
      glowColor: 'shadow-purple-500/10',
      purpose: 'Catalogs data attributes, maps asset lineages, and manages organizational ownership data.',
      enterpriseProblem: 'Data compliance inspectors cannot trace where specific metrics are sourced from, risking heavy privacy violations.',
      azureEquivalent: 'Microsoft Purview, Unity Catalog',
      enterpriseExample: 'Tracing an executive revenue graph metric back across every Spark stage to the original source database.',
      whyExists: 'Ensures absolute regulatory compliance (GDPR, HIPAA), governance, auditability, and ease of discovery.'
    },
    {
      id: 'ai-ready',
      label: '8. AI Ready Hub',
      icon: BrainCircuit,
      color: 'text-rose-500 bg-rose-500/10',
      borderColor: 'border-rose-500/30',
      glowColor: 'shadow-rose-500/10',
      purpose: 'Provides sanitized, masked, low-latency curated vectors for large language model prompts.',
      enterpriseProblem: 'Feeding customer names or phone numbers (PII) directly into external AI APIs breaks privacy policies.',
      azureEquivalent: 'Azure AI Studio, Azure OpenAI Studio Data Layers',
      enterpriseExample: 'Masked demographic datasets are used to safely feed context into customer sentiment models.',
      whyExists: 'Enables compliant generative AI adoption without sacrificing customer confidentiality.'
    },
    {
      id: 'consumers',
      label: '9. Consumers',
      icon: Server,
      color: 'text-violet-500 bg-violet-500/10',
      borderColor: 'border-violet-500/30',
      glowColor: 'shadow-violet-500/10',
      purpose: 'Exposes clean databases to analytical applications, dashboards, and deep predictive engines.',
      enterpriseProblem: 'Data scientists spend 80% of their time finding and cleaning data rather than deriving business value.',
      azureEquivalent: 'Power BI, Synapse Serverless SQL, Streamlit Hubs',
      enterpriseExample: 'Business executives query conformed regional sales performance directly via Power BI metrics.',
      whyExists: 'Transforms high-quality transactional tables into clear, actionable business strategies and value.'
    }
  ];

  const azureMappings = [
    {
      openSource: 'MinIO Local Object Store',
      azureEquivalent: 'Azure Data Lake Storage Gen2 (ADLS)',
      role: 'Raw Lakehouse Blob Storage',
      description: 'Provides scalable, high-throughput storage for Bronze partitions and raw telemetry logs, utilizing hierarchical directory spaces.'
    },
    {
      openSource: 'Apache Spark Local Cluster',
      azureEquivalent: 'Azure Databricks Workspace',
      role: 'Distributed In-Memory Compute',
      description: 'Executes parallelized data cleaning, schema conforms, and high-speed data deduplication stages on dynamic cluster VMs.'
    },
    {
      openSource: 'Delta Lake Transaction Log',
      azureEquivalent: 'Delta Tables on Microsoft Fabric',
      role: 'ACID Transactional Storage Layer',
      description: 'Guarantees concurrent write integrity, snapshot rollbacks, and schema enforcement on top of standard parquet files.'
    },
    {
      openSource: 'Amundsen Catalog Registry',
      azureEquivalent: 'Microsoft Purview / Unity Catalog',
      role: 'Governance Catalog & Lineage',
      description: 'Indexes physical file pathways, tracks structural columns, enforces role-based access, and traces system-wide lineages.'
    }
  ];

  const activeStage = stages.find(s => s.id === activeStageId) || stages[0];
  const ActiveIcon = activeStage.icon;

  return (
    <div id="architecture-page-container" className="space-y-10 animate-fadeIn font-sans pb-10">
      <PageHeader
        id="architecture-header-block"
        title="Interactive Platform Architecture"
        description="Review the complete Medallion engineering flow and see how local educational open-source sandbox technologies map to enterprise cloud stacks."
      />

      {/* INTERACTIVE PIPELINE VISUALIZATION */}
      <div className="space-y-6">
        <div>
          <h2 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
            Interactive Pipeline Flowchart
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Hover or click any pipeline stage below to inspect its operational role, business challenges, and Azure enterprise counterparts.
          </p>
        </div>

        {/* 9 Stages Interactive Flow Layout */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
          
          {/* Left / Top - Pipeline Stages Connections */}
          <div className="xl:col-span-4 space-y-3.5 max-h-[600px] overflow-y-auto pr-2 scrollbar-thin">
            {stages.map((stage) => {
              const StageIcon = stage.icon;
              const isActive = activeStageId === stage.id;
              return (
                <div
                  key={stage.id}
                  id={`stage-card-${stage.id}`}
                  onClick={() => setActiveStageId(stage.id)}
                  className={`flex items-center gap-4 p-4 rounded-xl border cursor-pointer transition-all duration-200 ${
                    isActive
                      ? `bg-blue-500/5 border-blue-600/70 dark:bg-blue-950/20 dark:border-blue-500 ${stage.glowColor} scale-[1.015]`
                      : 'bg-white dark:bg-[#111A2E]/40 border-slate-200 dark:border-slate-850/80 hover:border-slate-300 dark:hover:border-slate-800'
                  }`}
                >
                  <div className={`p-2.5 rounded-lg border ${stage.borderColor} ${stage.color} flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-105`}>
                    <StageIcon className="w-4 h-4" />
                  </div>
                  
                  <div className="flex-1 min-w-0 text-left">
                    <span className={`text-xs font-bold block ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-slate-700 dark:text-slate-350'}`}>
                      {stage.label}
                    </span>
                    <span className="text-[10px] text-slate-400 dark:text-slate-500 truncate block mt-0.5">
                      {stage.purpose}
                    </span>
                  </div>

                  <ChevronRight className={`w-4 h-4 text-slate-400 dark:text-slate-600 transition-transform ${isActive ? 'translate-x-1 text-blue-500' : ''}`} />
                </div>
              );
            })}
          </div>

          {/* Right / Bottom - Deep Stage Details Viewer */}
          <div className="xl:col-span-8 flex flex-col justify-stretch">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeStageId}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
                className="flex-1 bg-white dark:bg-[#111A2E]/40 border border-slate-200/95 dark:border-slate-850 rounded-2xl p-6 md:p-8 flex flex-col justify-between shadow-[0_4px_30px_rgba(0,0,0,0.015)] dark:shadow-none"
              >
                <div>
                  {/* Title Bar */}
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-100 dark:border-slate-850/60 mb-6">
                    <div className="flex items-center gap-3.5">
                      <div className={`p-3 rounded-xl ${activeStage.color} ${activeStage.borderColor} border`}>
                        <ActiveIcon className="w-6 h-6 animate-pulse" />
                      </div>
                      <div>
                        <Badge id={`badge-stage-${activeStage.id}`} content="Interactive Stage Monitor" variant="primary" />
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white mt-1">
                          {activeStage.label.substring(3)} Stage
                        </h3>
                      </div>
                    </div>
                    
                    <div className="flex flex-col text-left md:text-right">
                      <span className="text-[9px] text-slate-400 dark:text-slate-500 uppercase font-bold tracking-wider">Azure Equivalent</span>
                      <span className="text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900/40 px-3 py-1 rounded-lg mt-1 block w-max md:w-auto">
                        {activeStage.azureEquivalent}
                      </span>
                    </div>
                  </div>

                  {/* Dynamic Pipeline Track */}
                  <div className="mb-6 p-4 bg-slate-50 dark:bg-[#0B1329]/20 rounded-xl border border-slate-200/50 dark:border-slate-800/60 font-sans">
                    <div className="flex justify-between items-center text-[10px] text-slate-400 mb-3">
                      <span className="font-bold uppercase tracking-wider">Live Execution Sequence</span>
                      <span className="font-mono text-blue-500 animate-pulse font-bold flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-ping" />
                        Active Layer: {activeStage.label}
                      </span>
                    </div>
                    
                    <div className="relative flex items-center justify-between px-2">
                      {/* Base Track Line */}
                      <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-slate-200 dark:bg-slate-800 -translate-y-1/2 z-0" />
                      
                      {/* Progress Line */}
                      <div 
                        className="absolute top-1/2 left-0 h-0.5 bg-blue-500 transition-all duration-500 -translate-y-1/2 z-0"
                        style={{
                          width: `${
                            (stages.findIndex(s => s.id === activeStageId) / (stages.length - 1)) * 100
                          }%`
                        }}
                      />

                      {stages.map((st, i) => {
                        const isPastOrActive = stages.findIndex(s => s.id === activeStageId) >= i;
                        const isCurrentlyActive = st.id === activeStageId;
                        const StIcon = st.icon;

                        return (
                          <div key={st.id} className="relative z-10 flex flex-col items-center">
                            <button
                              onClick={() => setActiveStageId(st.id)}
                              className={`w-7 h-7 rounded-full flex items-center justify-center transition-all duration-300 border cursor-pointer ${
                                isCurrentlyActive
                                  ? 'bg-blue-600 border-blue-600 text-white shadow-md shadow-blue-500/20 scale-110'
                                  : isPastOrActive
                                  ? 'bg-blue-500/10 border-blue-500 text-blue-600 dark:text-blue-400'
                                  : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-400 hover:border-slate-300'
                              }`}
                              title={st.label}
                            >
                              <StIcon className="w-3.5 h-3.5" />
                            </button>
                            <span className={`text-[8px] font-sans font-bold mt-1.5 hidden md:block ${isCurrentlyActive ? 'text-blue-650 dark:text-blue-400' : 'text-slate-400'}`}>
                              {st.label.substring(3)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Deep Details Bento Compartments */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Purpose Section */}
                    <div className="space-y-1.5 p-4 bg-slate-50/50 dark:bg-[#0B1329]/30 rounded-xl border border-slate-150/50 dark:border-slate-850/40">
                      <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                        <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                        <span className="text-[10px] font-bold uppercase tracking-wider">Core Purpose</span>
                      </div>
                      <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans">
                        {activeStage.purpose}
                      </p>
                    </div>

                    {/* Enterprise Problem Section */}
                    <div className="space-y-1.5 p-4 bg-rose-50/10 dark:bg-rose-950/10 rounded-xl border border-rose-100/30 dark:border-rose-900/10">
                      <div className="flex items-center gap-2 text-rose-500">
                        <ShieldAlert className="w-4 h-4 flex-shrink-0" />
                        <span className="text-[10px] font-bold uppercase tracking-wider">The Enterprise Problem</span>
                      </div>
                      <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans">
                        {activeStage.enterpriseProblem}
                      </p>
                    </div>

                    {/* Real World Example Section */}
                    <div className="space-y-1.5 p-4 bg-amber-50/10 dark:bg-amber-950/10 rounded-xl border border-amber-100/30 dark:border-amber-900/10 md:col-span-2">
                      <div className="flex items-center gap-2 text-amber-500">
                        <Workflow className="w-4 h-4 flex-shrink-0" />
                        <span className="text-[10px] font-bold uppercase tracking-wider">Real World Enterprise Example</span>
                      </div>
                      <p className="text-xs text-slate-700 dark:text-slate-350 leading-relaxed font-sans font-medium">
                        {activeStage.enterpriseExample}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Footer Insight Box */}
                <div className="mt-6 pt-5 border-t border-slate-100 dark:border-slate-850/60 flex flex-col sm:flex-row items-start sm:items-center gap-3 bg-blue-500/5 dark:bg-blue-950/10 p-4 rounded-xl border border-blue-100/40 dark:border-blue-900/30">
                  <Info className="w-4 h-4 text-blue-500 mt-0.5 sm:mt-0 flex-shrink-0" />
                  <p className="text-xs text-slate-600 dark:text-slate-400 font-sans italic">
                    <strong className="text-slate-800 dark:text-slate-300 font-bold not-italic mr-1">Why This Layer Exists:</strong>
                    {activeStage.whyExists}
                  </p>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>

        </div>
      </div>

      {/* AZURE COMPONENT MAPPING SECTION */}
      <div className="space-y-6 pt-4">
        <div>
          <h2 className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
            Azure Cloud Translation & Integration
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Compare sandbox local components against Microsoft Azure production offerings.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {azureMappings.map((mapping, idx) => (
            <div
              key={idx}
              className="bg-white dark:bg-[#111A2E]/40 border border-slate-200/90 dark:border-slate-850 rounded-2xl p-5 hover:shadow-[0_4px_20px_rgba(0,0,0,0.015)] dark:hover:shadow-none transition-all duration-200 group flex flex-col justify-between"
            >
              <div>
                <div className="flex justify-between items-start pb-4 border-b border-slate-50 dark:border-slate-850/40 mb-4 gap-4">
                  <div>
                    <span className="text-[9px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Sandbox Component</span>
                    <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 mt-0.5 font-mono">
                      {mapping.openSource}
                    </h4>
                  </div>
                  <div className="text-right">
                    <span className="text-[9px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Azure equivalent</span>
                    <h4 className="text-xs font-bold text-blue-600 dark:text-blue-400 mt-0.5">
                      {mapping.azureEquivalent}
                    </h4>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center gap-1.5 text-blue-500/90 dark:text-blue-400/90">
                    <CloudLightning className="w-3.5 h-3.5" />
                    <span className="text-[10px] font-bold uppercase tracking-wider">{mapping.role}</span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    {mapping.description}
                  </p>
                </div>
              </div>

              <div className="mt-4 pt-3.5 border-t border-slate-50 dark:border-slate-850/30 flex items-center justify-between text-[10px] text-slate-400 font-sans">
                <span>Deployment Status: Sandbox Mocked</span>
                <span className="text-emerald-500 font-bold uppercase tracking-wide flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> Cloud Compatible
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
