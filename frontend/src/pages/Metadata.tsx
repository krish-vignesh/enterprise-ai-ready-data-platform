import React, { useState } from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PageHeader, Card, Table, Badge, InsightCard } from '../components/UI';
import {
  Tags,
  GitCommit,
  User,
  ArrowRight,
  Database,
  Shuffle,
  Layers,
  Cpu,
  Triangle,
  BrainCircuit,
  Lock,
  GitBranch,
  ShieldCheck
} from 'lucide-react';

export const Metadata: React.FC = () => {
  const { datasets, deltaTables } = usePlatform();
  const [selectedId, setSelectedId] = useState<string>('customer_profiles');

  // Unified metadata item finder
  const activeDataset = datasets.find((d) => d.name === selectedId);
  const activeTable = deltaTables.find((t) => t.name === selectedId);

  // Fallbacks
  const name = activeDataset?.name || activeTable?.name || 'customer_profiles';
  const owner = activeDataset?.owner || 'Data Platform Core Team';
  const format = activeDataset?.format || 'Delta';
  const rows = activeDataset?.rowCount || 125400;
  const size = activeDataset?.size || '14.2 MB';
  const columns = activeDataset?.columns || [
    { name: 'customer_id', type: 'string', nullable: false, description: 'Unique identifier for the customer' },
    { name: 'first_name', type: 'string', nullable: false, description: 'Customer first name' },
    { name: 'last_name', type: 'string', nullable: false, description: 'Customer last name' },
    { name: 'email', type: 'string', nullable: false, description: 'Primary email address' },
    { name: 'country', type: 'string', nullable: true, description: 'Signup location' },
  ];

  const metadataList = [
    { id: 'customer_profiles', name: 'customer_profiles', type: 'Dataset Source' },
    { id: 'retail_transactions', name: 'retail_transactions', type: 'Dataset Source' },
    { id: 'customer_master', name: 'customer_master', type: 'Delta Table' },
    { id: 'transaction_ledger', name: 'transaction_ledger', type: 'Delta Table' },
  ];

  return (
    <div id="metadata-page-container" className="space-y-8 animate-fadeIn">
      <PageHeader
        id="metadata-header-block"
        title="Metadata & Lineage Catalog"
        description="Search global schema catalogs, enforce corporate governance boundaries, and track operational dataset lineage lineages."
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left selector menu */}
        <div className="lg:col-span-1 space-y-4">
          <Card id="metadata-catalog-selector">
            <div className="mb-4">
              <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                Unified Data Catalog
              </h3>
              <p className="text-xs text-slate-400">
                Browse conformed storage paths and tables.
              </p>
            </div>
            
            <div className="space-y-1.5">
              {metadataList.map((item) => {
                const isActive = selectedId === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setSelectedId(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-left text-xs font-semibold transition-all duration-150 cursor-pointer ${
                      isActive
                        ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 font-bold border-l-2 border-blue-600 pl-2'
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/40 border-l-2 border-transparent'
                    }`}
                  >
                    <span className="font-mono truncate mr-2">{item.name}</span>
                    <span className="text-[9px] bg-slate-150 dark:bg-slate-800 text-slate-500 dark:text-slate-400 px-1.5 py-0.5 rounded font-sans uppercase font-bold border border-slate-250 dark:border-slate-700/60">
                      {item.type.split(' ')[0]}
                    </span>
                  </button>
                );
              })}
            </div>
          </Card>

          {/* Governance & support metadata */}
          <Card id="metadata-ownership-card">
            <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider mb-4 font-sans">
              Governance & Security
            </h3>
            <div className="space-y-3.5 text-xs font-sans">
              <div className="flex items-center gap-2.5 text-slate-600 dark:text-slate-300">
                <User className="w-4 h-4 text-slate-400 flex-shrink-0" />
                <div>
                  <span className="text-[9px] text-slate-400 block uppercase font-bold tracking-wider">Asset Owner Group</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">{owner}</span>
                </div>
              </div>
              <div className="flex items-center gap-2.5 text-slate-600 dark:text-slate-300 border-t border-slate-100 dark:border-slate-800 pt-3.5">
                <Lock className="w-4 h-4 text-rose-400 flex-shrink-0" />
                <div>
                  <span className="text-[9px] text-slate-400 block uppercase font-bold tracking-wider">PII Privacy Check</span>
                  <span className="font-bold text-rose-500 flex items-center gap-1">
                    PII Masking Active
                  </span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Right details panel */}
        <div className="lg:col-span-3 space-y-6">
          
          {/* Interactive Lineage tracking graph */}
          <Card id="lineage-map-card">
            <div className="mb-6">
              <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                Dynamic Physical Lineage Trace
              </h3>
              <p className="text-xs text-slate-400">
                Tracing operational columns from raw landing folders to model-ready Gold Delta files.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-slate-50/50 dark:bg-[#0B1329]/50 p-4 rounded-xl border border-slate-200/60 dark:border-slate-850/60 text-center text-xs font-sans">
              
              {/* Node 1 */}
              <div className="p-3 bg-white dark:bg-[#1E293B]/60 border border-slate-200 dark:border-slate-800 rounded-lg flex flex-col items-center shadow-xs hover:border-blue-500/40 hover:scale-[1.01] transition-all duration-250">
                <Database className="w-4 h-4 text-amber-500 mb-1.5" />
                <span className="font-mono text-[10px] font-bold block truncate max-w-full">{name}_raw</span>
                <span className="text-[9px] text-amber-600 font-bold uppercase block mt-1">Landing S3</span>
              </div>

              {/* Node 2 */}
              <div className="p-3 bg-white dark:bg-[#1E293B]/60 border border-slate-200 dark:border-slate-800 rounded-lg flex flex-col items-center shadow-xs hover:border-blue-500/40 hover:scale-[1.01] transition-all duration-250">
                <Shuffle className="w-4 h-4 text-blue-500 mb-1.5" />
                <span className="font-mono text-[10px] font-bold block truncate max-w-full">ingest_{name}</span>
                <span className="text-[9px] text-blue-600 font-bold uppercase block mt-1">Conform</span>
              </div>

              {/* Node 3 */}
              <div className="p-3 bg-white dark:bg-[#1E293B]/60 border border-slate-200 dark:border-slate-800 rounded-lg flex flex-col items-center shadow-xs hover:border-blue-500/40 hover:scale-[1.01] transition-all duration-250">
                <Cpu className="w-4 h-4 text-indigo-500 mb-1.5 animate-pulse" />
                <span className="font-mono text-[10px] font-bold block truncate max-w-full">spark_dedup</span>
                <span className="text-[9px] text-indigo-600 font-bold uppercase block mt-1">RAM Workload</span>
              </div>

              {/* Node 4 */}
              <div className="p-3 bg-blue-500/5 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/40 rounded-lg flex flex-col items-center shadow-xs hover:scale-[1.01] transition-all duration-250">
                <Triangle className="w-4 h-4 text-blue-500 fill-blue-500 mb-1.5 animate-pulse" />
                <span className="font-mono text-[10px] font-bold text-blue-600 dark:text-blue-400 block truncate max-w-full">
                  {name}_delta
                </span>
                <span className="text-[9px] text-emerald-600 font-bold uppercase block mt-1">ACID table</span>
              </div>

            </div>
          </Card>

          {/* Column Schema list */}
          <Card id="schema-details-card">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                  Schema Catalog Specification
                </h3>
                <p className="text-xs text-slate-400">
                  Target columns, data types, null conditions, and semantic labels.
                </p>
              </div>
              <div className="flex gap-4 text-xs font-mono text-slate-500">
                <span>Row count: <strong className="text-slate-800 dark:text-slate-200">{rows.toLocaleString()}</strong></span>
                <span>Size: <strong className="text-slate-800 dark:text-slate-200">{size}</strong></span>
              </div>
            </div>

            <Table id="metadata-columns-table" headers={['Field Label', 'Type Mapping', 'Nullable', 'Semantic Business Description']}>
              {columns.map((col, index) => (
                <tr key={index} className="hover:bg-slate-50/50 dark:hover:bg-slate-850/10">
                  <td className="px-5 py-3.5 font-mono text-xs font-bold text-slate-900 dark:text-white">
                    {col.name}
                  </td>
                  <td className="px-5 py-3.5 font-mono text-xs text-blue-600 dark:text-blue-400 font-bold">
                    {col.type || 'string'}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                      {col.nullable ? 'Nullable' : 'Strict Check'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
                    {col.description || 'Description catalog detail pending annotation.'}
                  </td>
                </tr>
              ))}
            </Table>
          </Card>
        </div>
      </div>

      <InsightCard
        id="metadata-architecture-insight"
        title="Unified Enterprise Metastore Lineages"
        purpose="Tracks, documents, and visualizes physical table columns, data type constraints, and logical execution pipelines."
        enterpriseProblem="Compliance officers, auditors, and database developers cannot locate the exact origin of modified dashboard values, risking regulatory breaches."
        azureEquivalent="Microsoft Purview, Databricks Unity Catalog"
        enterpriseExample="A compliance officer tracing a 'SocialSecurityNumber' field across several Spark stages back to the source server log files."
        whyExists="Assures absolute compliance with global guidelines (GDPR, HIPAA), enables high-speed dataset discoveries, and tracks pipeline transformations."
      />
    </div>
  );
};
