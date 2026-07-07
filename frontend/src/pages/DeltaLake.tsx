import React, { useState } from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PageHeader, Card, Button, Badge, Table, InsightCard } from '../components/UI';
import {
  Triangle,
  History,
  GitBranch,
  ShieldAlert,
  Sliders,
  CheckCircle2,
  AlertCircle,
  Clock,
  User,
  Database,
  Folder,
  CornerDownRight,
  FileText
} from 'lucide-react';

export const DeltaLake: React.FC = () => {
  const { deltaTables, selectedTableId, setSelectedTableId } = usePlatform();
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const [simState, setSimState] = useState<'IDLE' | 'COMPARING' | 'BLOCKED' | 'COMPLETED'>('IDLE');

  const activeTable = deltaTables.find((t) => t.id === selectedTableId) || deltaTables[0];

  const handleTableChange = (id: string) => {
    setSelectedTableId(id);
    setSelectedVersion(null); // Reset version selection
  };

  const runSimulation = (mode: 'STRICT' | 'MERGE') => {
    setSimState('COMPARING');
    setTimeout(() => {
      if (mode === 'STRICT') {
        setSimState('BLOCKED');
      } else {
        setSimState('COMPLETED');
      }
    }, 1200);
  };

  return (
    <div id="delta-lake-page-container" className="space-y-8 animate-fadeIn">
      <PageHeader
        id="delta-header-block"
        title="Delta Lake ACID Ledger"
        description="Verify Parquet table transaction ledgers, schema evolution guards, and concurrent multi-write time-travel snapshots."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column - Select Table list */}
        <div className="space-y-6 lg:col-span-1">
          <Card id="delta-tables-list-card">
            <div className="mb-4">
              <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                Delta Catalog Tables
              </h3>
              <p className="text-xs text-slate-400">
                Select conformed Delta table to view its commit history logs.
              </p>
            </div>
            
            <div className="space-y-2">
              {deltaTables.map((table) => {
                const isActive = table.id === activeTable?.id;
                return (
                  <button
                    key={table.id}
                    onClick={() => handleTableChange(table.id)}
                    className={`w-full text-left p-4 rounded-xl border transition-all duration-150 cursor-pointer ${
                      isActive
                        ? 'bg-blue-500/10 border-blue-500 text-blue-600 dark:text-blue-400 font-bold'
                        : 'bg-white dark:bg-[#1E293B]/40 border-slate-200 dark:border-slate-800 text-slate-500 hover:bg-slate-50 dark:hover:bg-[#1E293B]/60'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold font-mono">
                        {table.name}
                      </span>
                      <Badge id={`badge-${table.id}`} content={`v${table.version}`} variant="primary" />
                    </div>
                    <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-1.5 truncate font-sans">
                      {table.location}
                    </p>
                  </button>
                );
              })}
            </div>
          </Card>

          {/* Schema Evolution Guard */}
          <Card id="schema-evolution-info-card">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 rounded-lg border border-blue-100 dark:border-blue-900/30 flex-shrink-0">
                <ShieldAlert className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-slate-900 dark:text-white font-sans uppercase tracking-wider">
                  Schema Evolution Guard
                </h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
                  Delta Lake blocks structural writes if incoming columns drift from the catalog. Auto-merges can be bypassed with <code className="font-mono text-blue-500 dark:text-blue-400 bg-slate-100 dark:bg-slate-900 px-1 py-0.5 rounded">.option("mergeSchema", "true")</code>.
                </p>
                <div className="pt-2 flex items-center gap-1.5 text-[10px] text-emerald-600 dark:text-emerald-400 font-bold font-sans">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Schema validation guard active</span>
                </div>
              </div>
            </div>
          </Card>

          {/* Delta ACID Merge & Evolution Simulator */}
          <Card id="schema-evolution-simulator" className="p-5 font-sans space-y-4">
            <div className="space-y-1">
              <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                Delta MERGE & Evolution Sandbox
              </h4>
              <p className="text-[11px] text-slate-400">
                Simulate an enterprise UPSERT merge statement drifting your schema layout.
              </p>
            </div>

            <div className="bg-slate-50 dark:bg-slate-900/60 p-3 rounded-xl border border-slate-150 dark:border-slate-850/80 space-y-3">
              <div className="flex justify-between items-center text-[10px] text-slate-400">
                <span>Incoming Row Data:</span>
                <span className="font-mono bg-blue-500/10 text-blue-600 dark:text-blue-400 px-1.5 py-0.5 rounded font-bold">schema_drifted</span>
              </div>
              <div className="font-mono text-[10px] bg-white dark:bg-slate-950 p-2.5 rounded-lg border border-slate-200 dark:border-slate-850 space-y-1 text-slate-600 dark:text-slate-300">
                <p>{"{"}</p>
                <p className="pl-4">{"\"transaction_id\": \"TX84920\","}</p>
                <p className="pl-4 text-amber-500 font-bold">{"\"net_margin_usd\": 1485.20, // New column!"}</p>
                <p className="pl-4">{"\"event_timestamp\": 1719948010"}</p>
                <p>{"}"}</p>
              </div>

              {/* Steps progression */}
              <div className="space-y-2.5 pt-1">
                {/* Step 1: Scan Existing Schema */}
                <div className="flex items-center gap-2 text-[10.5px]">
                  <div className={`w-5 h-5 rounded-full font-mono text-[10px] flex items-center justify-center flex-shrink-0 ${simState !== 'IDLE' ? 'bg-blue-500 text-white animate-pulse' : 'bg-slate-200 dark:bg-slate-800 text-slate-500'}`}>1</div>
                  <span className="text-slate-600 dark:text-slate-300">Inspect existing table schema for drift</span>
                </div>
                {/* Step 2: ACID Lock Transaction */}
                <div className="flex items-center gap-2 text-[10.5px]">
                  <div className={`w-5 h-5 rounded-full font-mono text-[10px] flex items-center justify-center flex-shrink-0 ${simState === 'COMPLETED' || simState === 'BLOCKED' ? 'bg-indigo-500 text-white' : 'bg-slate-200 dark:bg-slate-800 text-slate-500'}`}>2</div>
                  <span className="text-slate-600 dark:text-slate-300">Acquire exclusive optimistic concurrency lock</span>
                </div>
              </div>
            </div>

            {/* Dynamic Status Outputs */}
            {simState === 'COMPARING' && (
              <div className="p-3 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg border border-blue-500/20 text-xs flex items-center gap-2 animate-pulse">
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-ping" />
                <span>Running Delta schema drift safety pre-checks...</span>
              </div>
            )}

            {simState === 'BLOCKED' && (
              <div className="p-3 bg-red-500/10 text-red-600 dark:text-red-400 rounded-lg border border-red-500/20 text-xs space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  <span>SchemaEvolutionException</span>
                </div>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-normal">
                  Transaction safely rejected! Column 'net_margin_usd' does not match target schema metadata. Table structure preserved from corrupt write.
                </p>
              </div>
            )}

            {simState === 'COMPLETED' && (
              <div className="p-3 bg-emerald-500/10 text-emerald-600 dark:text-emerald-450 rounded-lg border border-emerald-500/20 text-xs space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span>Merge schema evolution success</span>
                </div>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-normal">
                  Successfully evolved target schema specification metadata. Added 'net_margin_usd' column and committed transaction JSON log files.
                </p>
              </div>
            )}

            {simState === 'IDLE' && (
              <div className="grid grid-cols-2 gap-2">
                <Button
                  id="reject-drift-btn"
                  variant="outline"
                  size="sm"
                  onClick={() => runSimulation('STRICT')}
                  className="w-full text-[10px] py-1.5"
                >
                  Strict Guard Check
                </Button>
                <Button
                  id="evolve-drift-btn"
                  variant="primary"
                  size="sm"
                  onClick={() => runSimulation('MERGE')}
                  className="w-full text-[10px] py-1.5"
                >
                  Evolve & Commit Schema
                </Button>
              </div>
            )}

            {simState !== 'IDLE' && (
              <Button
                id="reset-drift-sim-btn"
                variant="outline"
                size="sm"
                onClick={() => setSimState('IDLE')}
                className="w-full text-[10px]"
              >
                Reset Sandbox State
              </Button>
            )}
          </Card>
        </div>

        {/* Right columns - Table transaction logs */}
        {activeTable ? (
          <div className="lg:col-span-2 space-y-6">
            <Card id="delta-table-details-card">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-150 dark:border-slate-800">
                <div className="space-y-1">
                  <h3 className="text-xs font-bold text-slate-950 dark:text-white font-mono uppercase tracking-wider flex items-center gap-2">
                    <Triangle className="w-4 h-4 text-blue-500 fill-blue-500" />
                    {activeTable.name}
                  </h3>
                  <p className="text-xs text-slate-400 dark:text-slate-500 font-sans">
                    Physical bucket endpoint: <code className="font-mono text-[10px] text-blue-500 break-all">{activeTable.location}</code>
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge id="badge-active-table-v" content={`Current version: v${activeTable.version}`} variant="success" />
                </div>
              </div>

              {/* Transaction history log ledger */}
              <div className="bg-slate-50 dark:bg-[#0F172A]/30 p-5 rounded-xl border border-slate-200/60 dark:border-slate-800 space-y-5">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2 text-xs font-sans text-slate-800 dark:text-slate-300">
                    <History className="w-4 h-4 text-slate-400" />
                    <span className="font-bold">Delta ACID Time-Travel Ledger</span>
                  </div>
                  <span className="text-[9px] bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded font-bold">
                    Snapshots
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {activeTable.history.map((commit) => (
                    <button
                      key={commit.version}
                      onClick={() => setSelectedVersion(commit.version)}
                      className={`p-3 rounded-lg border text-center transition-all duration-150 cursor-pointer ${
                        (selectedVersion === null && commit.version === activeTable.version) || selectedVersion === commit.version
                          ? 'border-blue-500 bg-blue-500/10 text-blue-600 dark:text-blue-400 font-bold'
                          : 'border-slate-200 dark:border-slate-850 bg-white dark:bg-[#1E293B]/40 text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800/60'
                      }`}
                    >
                      <span className="text-xs font-mono block font-extrabold">Snapshot v{commit.version}</span>
                      <span className="text-[10px] text-slate-400 font-sans block mt-1">{commit.operation}</span>
                    </button>
                  ))}
                </div>

                {/* Show details of selected version */}
                <div className="p-4 bg-white dark:bg-[#1E293B] border border-slate-200 dark:border-slate-800 rounded-lg text-xs font-sans">
                  {(() => {
                    const ver = selectedVersion !== null ? selectedVersion : activeTable.version;
                    const commit = activeTable.history.find((c) => c.version === ver);
                    return commit ? (
                      <div className="space-y-3">
                        <div className="flex flex-wrap items-center justify-between text-[10px] font-mono text-slate-400 pb-2 border-b border-slate-100 dark:border-slate-800">
                          <span className="flex items-center gap-1"><User className="w-3.5 h-3.5" /> Committer: {commit.userName}</span>
                          <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Timestamp: {commit.timestamp}</span>
                        </div>
                        <div>
                          <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                            Transaction Event: <span className="font-mono text-blue-500">{commit.operation}</span>
                          </h4>
                          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mt-1.5 font-sans">
                            {commit.summary}
                          </p>
                        </div>
                      </div>
                    ) : null;
                  })()}
                </div>

                {/* Live Delta Log Ledger File System Simulator */}
                {(() => {
                  const ver = selectedVersion !== null ? selectedVersion : activeTable.version;
                  return (
                    <div className="mt-6 border border-slate-150 dark:border-slate-800 rounded-xl p-4 bg-slate-50/50 dark:bg-[#1E293B]/10 space-y-4">
                      <div>
                        <h4 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider font-sans flex items-center gap-1.5">
                          <Sliders className="w-3.5 h-3.5 text-blue-500" /> Interactive Delta Parquet Time-Travel Sandbox
                        </h4>
                        <p className="text-[11px] text-slate-400 mt-0.5">
                          Slide through delta snapshot commits to see how raw transactional Parquet file states evolve.
                        </p>
                      </div>

                      {/* Slider controller */}
                      <div className="flex items-center gap-4 py-2 px-3 bg-white dark:bg-slate-900 border border-slate-150 dark:border-slate-800 rounded-xl">
                        <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400">Time Travel Node:</span>
                        <input 
                          type="range" 
                          min="0" 
                          max={activeTable.history.length - 1} 
                          value={ver} 
                          onChange={(e) => setSelectedVersion(Number(e.target.value))}
                          className="flex-1 accent-blue-500 cursor-pointer h-1 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none"
                        />
                        <span className="text-xs font-bold font-mono text-blue-600 dark:text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-200/30">
                          v{ver}
                        </span>
                      </div>

                      {/* File Tree visual structure */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                        {/* Delta log JSON files */}
                        <div className="p-3 bg-white dark:bg-slate-900 border border-slate-150 dark:border-slate-800 rounded-xl space-y-2.5">
                          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                            <span className="font-bold text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                              <Folder className="w-3.5 h-3.5 text-amber-500 fill-amber-500" /> _delta_log/ (ACID History)
                            </span>
                            <span className="text-[9px] font-mono text-slate-400">Directory</span>
                          </div>
                          <div className="space-y-1.5 pl-2">
                            {activeTable.history.map((commit) => {
                              const isActive = commit.version <= ver;
                              const isSelected = commit.version === ver;
                              return (
                                <div 
                                  key={commit.version} 
                                  className={`flex items-center justify-between p-2 rounded-lg transition-all duration-150 ${
                                    isSelected 
                                      ? 'bg-blue-500/10 border border-blue-500/30 text-blue-600 dark:text-blue-400 font-bold shadow-xs' 
                                      : isActive 
                                      ? 'text-slate-700 dark:text-slate-300 opacity-80' 
                                      : 'text-slate-400 dark:text-slate-600 line-through'
                                  }`}
                                >
                                  <div className="flex items-center gap-2 font-mono text-[10px] truncate">
                                    <CornerDownRight className="w-3 h-3 text-slate-400 flex-shrink-0" />
                                    <FileText className="w-3.5 h-3.5 text-blue-500" />
                                    <span>000000...000{commit.version}.json</span>
                                  </div>
                                  <span className={`text-[8px] uppercase px-1.5 py-0.5 rounded font-sans flex-shrink-0 ${
                                    isSelected 
                                      ? 'bg-blue-500/20 text-blue-700 dark:text-blue-300 font-bold' 
                                      : isActive 
                                      ? 'bg-slate-100 dark:bg-slate-850 text-slate-500' 
                                      : 'bg-slate-100 dark:bg-slate-850 text-slate-400'
                                  }`}>
                                    {isSelected ? 'Read Head' : isActive ? 'Historic' : 'Shadowed'}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        {/* Physical Parquet files */}
                        <div className="p-3 bg-white dark:bg-slate-900 border border-slate-150 dark:border-slate-800 rounded-xl space-y-2.5">
                          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                            <span className="font-bold text-[10px] text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                              <Folder className="w-3.5 h-3.5 text-blue-500 fill-blue-500" /> parquet_data/ (Storage Files)
                            </span>
                            <span className="text-[9px] font-mono text-slate-400">Directories</span>
                          </div>
                          <div className="space-y-1.5 pl-2">
                            {activeTable.history.map((commit) => {
                              const isActive = commit.version <= ver;
                              const isSelected = commit.version === ver;
                              return (
                                <div 
                                  key={commit.version} 
                                  className={`flex items-center justify-between p-2 rounded-lg transition-all duration-150 ${
                                    isSelected 
                                      ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 font-bold shadow-xs' 
                                      : isActive 
                                      ? 'text-slate-700 dark:text-slate-300 opacity-80' 
                                      : 'text-slate-400 dark:text-slate-600 line-through'
                                  }`}
                                >
                                  <div className="flex items-center gap-2 font-mono text-[10px] truncate">
                                    <CornerDownRight className="w-3 h-3 text-slate-400 flex-shrink-0" />
                                    <Database className="w-3.5 h-3.5 text-emerald-500" />
                                    <span>part-000{commit.version}-snappy.parquet</span>
                                  </div>
                                  <span className={`text-[8px] uppercase px-1.5 py-0.5 rounded font-sans flex-shrink-0 ${
                                    isSelected 
                                      ? 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-bold' 
                                      : isActive 
                                      ? 'bg-slate-100 dark:bg-slate-850 text-slate-500' 
                                      : 'bg-slate-100 dark:bg-slate-850 text-slate-400'
                                  }`}>
                                    {isSelected ? 'Created v' + commit.version : isActive ? 'Active' : 'Unreferenced'}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>

              {/* Display Table Schema */}
              <div className="mt-8 space-y-4">
                <div>
                  <h4 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                    Table Schema Specification
                  </h4>
                  <p className="text-xs text-slate-400 mt-1">
                    Columns definitions, physical data types, and directory partition indicators.
                  </p>
                </div>

                <Table id="delta-table-schema" headers={['Field Name', 'Type Mapping', 'Partitioning']}>
                  {activeTable.schema.map((col, index) => (
                    <tr key={index} className="hover:bg-slate-50/50 dark:hover:bg-slate-850/10">
                      <td className="px-5 py-3 font-mono text-xs font-bold text-slate-800 dark:text-slate-200">
                        {col.column}
                      </td>
                      <td className="px-5 py-3 font-mono text-xs text-slate-500 dark:text-slate-400">
                        {col.type}
                      </td>
                      <td className="px-5 py-3">
                        {col.partitionKey ? (
                          <span className="inline-flex items-center gap-1 text-[9px] font-bold text-amber-600 bg-amber-50 dark:bg-amber-950/40 px-2 py-0.5 rounded border border-amber-200 dark:border-amber-900/30">
                            <GitBranch className="w-3 h-3" /> Partition Column
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400 dark:text-slate-500 italic font-sans">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </Table>
              </div>
            </Card>
          </div>
        ) : (
          <div className="lg:col-span-2">
            <Card id="no-delta-tables-warning" className="p-10 text-center space-y-4">
              <AlertCircle className="w-10 h-10 text-slate-400 mx-auto" />
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-slate-800 dark:text-white font-sans">No Delta tables generated yet</h4>
                <p className="text-xs text-slate-400">
                  Go to the Spark Processing page and run a Silver-to-Gold Spark pipeline to construct tables.
                </p>
              </div>
            </Card>
          </div>
        )}
      </div>

      <InsightCard
        id="delta-architecture-insight"
        title="Parquet Transaction Isolation Logs"
        purpose="Enforces ACID transaction parameters, schema validations, and directory logs directly on top of cheap cloud folders."
        enterpriseProblem="Simultaneous updates from multiple scheduled batch write jobs result in file corruption, directory overlaps, or dirty reads."
        azureEquivalent="Azure Synapse Serverless Delta Tables, Microsoft Fabric Lakehouse"
        enterpriseExample="An automated financial reporting query retrieving point-in-time snapshot details using table time-travel tags."
        whyExists="Bridges the gap between physical files and transactional DBMS systems, ensuring complete data consistency across all read/write nodes."
      />
    </div>
  );
};
