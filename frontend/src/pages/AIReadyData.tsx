import React, { useState } from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PageHeader, Card, Button, Table, Badge, InsightCard } from '../components/UI';
import {
  BrainCircuit,
  Database,
  BarChart4,
  Cpu,
  Play,
  Terminal,
  Sparkles,
  Layers,
  ArrowRight,
  Zap,
  Globe,
  Lock,
  ArrowUpRight
} from 'lucide-react';

export const AIReadyData: React.FC = () => {
  const { deltaTables } = usePlatform();
  const [activeTab, setActiveTab] = useState<'ml' | 'bi' | 'genai'>('ml');

  // Selected query for BI tab
  const [selectedQuery, setSelectedQuery] = useState(0);

  // Generative AI prompt simulator
  const [genAiPrompt, setGenAiPrompt] = useState('Retrieve the top 3 store sales and draft a Slack alert.');
  const [isPromptGenerating, setIsPromptGenerating] = useState(false);
  const [simulatedRagOutput, setSimulatedRagOutput] = useState('');

  // Sample structured SQL queries & responses
  const sqlQueries = [
    {
      sql: `SELECT store_id, SUM(amount) as sales \nFROM transaction_ledger \nGROUP BY store_id \nORDER BY sales DESC LIMIT 3;`,
      headers: ['Store Reference', 'Sales Volume', 'Locale', 'KPI Index'],
      rows: [
        ['Store #104 (Seattle)', '$342,400.00', 'US-WEST', 'Tier 1 Prime'],
        ['Store #112 (New York)', '$310,250.00', 'US-EAST', 'Tier 1 Prime'],
        ['Store #101 (Boston)', '$288,140.00', 'US-EAST', 'Tier 2 Active'],
      ],
    },
    {
      sql: `SELECT country, COUNT(customer_id) as total_users \nFROM customer_master \nGROUP BY country \nORDER BY total_users DESC;`,
      headers: ['Country Segment', 'Registered Customers', 'SLA Conformity', 'Market Share'],
      rows: [
        ['United States (US)', '84,120 profiles', '100% Passed', '67.1%'],
        ['Canada (CA)', '21,450 profiles', '100% Passed', '17.1%'],
        ['United Kingdom (GB)', '19,830 profiles', '98.8% Warn', '15.8%'],
      ],
    },
  ];

  // RAG simulation answers
  const handlePromptSimulate = () => {
    setIsPromptGenerating(true);
    setSimulatedRagOutput('');
    setTimeout(() => {
      setIsPromptGenerating(false);
      setSimulatedRagOutput(
        `[SYSTEM CONTEXT RAG GROUNDING ACTIVE] \n\n1. FETCHED TRANSACTION COMMIT HISTORY:\n   - Querying delta logs: s3a://delta-lake/gold/transaction_ledger\n   - Checked rows: 1,482,000 \n\n2. GROUNDING CONTEXT EXTRACTED (TOP 3 REVENUES):\n   - Seattle (Store 104): $342,400.00 \n   - New York (Store 112): $310,250.00 \n   - Boston (Store 101): $288,140.00 \n\n3. PRODUCED SECURE LLM SUMMARY OUTLINE:\n   "🚨 *Weekly Store Revenue Alert* 🚨\n   The top-performing physical branches for fiscal week 26:\n   🥇 *Seattle (Store 104)*: $342,400\n   🥈 *New York (Store 112)*: $310,250\n   🥉 *Boston (Store 101)*: $288,140\n   \n   Transactional integrity confirmed over Delta Lake commit logs. All downstream outputs aligned."`
      );
    }, 1000);
  };

  return (
    <div id="aiready-page-container" className="space-y-8 animate-fadeIn">
      <PageHeader
        id="ai-ready-header"
        title="AI-Ready Serving Hub"
        description="Expose conformed gold partitions directly to downstream consumers, analytical pipelines, ML feature stores, and GenAI prompts."
      />

      {/* Selector Tabs matching Consumers Section */}
      <div id="ai-hub-consumers-tabs" className="flex border-b border-slate-200 dark:border-slate-800 gap-6">
        <button
          onClick={() => setActiveTab('ml')}
          className={`pb-4 text-xs font-bold uppercase tracking-wider transition-all duration-150 relative cursor-pointer flex items-center gap-2 ${
            activeTab === 'ml'
              ? 'text-blue-600 dark:text-blue-400 border-b-2 border-b-blue-500'
              : 'text-slate-400 dark:text-slate-500 hover:text-slate-700'
          }`}
        >
          <Cpu className="w-4 h-4" /> Feature Store
        </button>
        <button
          onClick={() => setActiveTab('bi')}
          className={`pb-4 text-xs font-bold uppercase tracking-wider transition-all duration-150 relative cursor-pointer flex items-center gap-2 ${
            activeTab === 'bi'
              ? 'text-blue-600 dark:text-blue-400 border-b-2 border-b-blue-500'
              : 'text-slate-400 dark:text-slate-500 hover:text-slate-700'
          }`}
        >
          <BarChart4 className="w-4 h-4" /> BI Analytics
        </button>
        <button
          onClick={() => setActiveTab('genai')}
          className={`pb-4 text-xs font-bold uppercase tracking-wider transition-all duration-150 relative cursor-pointer flex items-center gap-2 ${
            activeTab === 'genai'
              ? 'text-blue-600 dark:text-blue-400 border-b-2 border-b-blue-500'
              : 'text-slate-400 dark:text-slate-500 hover:text-slate-700'
          }`}
        >
          <Sparkles className="w-4 h-4" /> GenAI / RAG Grounding
        </button>
      </div>

      {/* Dynamic Tab Contents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main interactive area */}
        <div className="lg:col-span-2 space-y-6">
          {activeTab === 'ml' && (
            <Card id="ml-features-card">
              <div className="mb-6">
                <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                  Offline ML Feature Store
                </h3>
                <p className="text-xs text-slate-400">
                  Feature matrices extracted directly from conformed Delta Lake logs. Suitable for model training pipelines.
                </p>
              </div>

              <Table id="ml-features-table" headers={['Feature Key', 'Type Mapping', 'Mean / Mode', 'Std Deviation', 'Scaler Target']}>
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-850/10">
                  <td className="px-5 py-4 font-mono text-xs font-bold text-slate-900 dark:text-white">customer_id_index</td>
                  <td className="px-5 py-4 font-mono text-xs text-blue-500">double</td>
                  <td className="px-5 py-4 text-xs font-mono text-slate-500">Index Label</td>
                  <td className="px-5 py-4 text-xs font-mono text-slate-400">-</td>
                  <td className="px-5 py-4"><Badge id="b-1" content="Dense Index" variant="primary" /></td>
                </tr>
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-850/10">
                  <td className="px-5 py-4 font-mono text-xs font-bold text-slate-900 dark:text-white">normalized_amount</td>
                  <td className="px-5 py-4 font-mono text-xs text-blue-500">double</td>
                  <td className="px-5 py-4 text-xs font-mono text-slate-500">112.54</td>
                  <td className="px-5 py-4 text-xs font-mono text-slate-500">15.42</td>
                  <td className="px-5 py-4"><Badge id="b-2" content="MinMaxScaled" variant="success" /></td>
                </tr>
                <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-850/10">
                  <td className="px-5 py-4 font-mono text-xs font-bold text-slate-900 dark:text-white">is_churn_risk</td>
                  <td className="px-5 py-4 font-mono text-xs text-blue-500">integer</td>
                  <td className="px-5 py-4 text-xs font-mono text-slate-500">0.02</td>
                  <td className="px-5 py-4 text-xs font-mono text-slate-500">0.12</td>
                  <td className="px-5 py-4"><Badge id="b-3" content="One-Hot Enc" variant="purple" /></td>
                </tr>
              </Table>
            </Card>
          )}

          {activeTab === 'bi' && (
            <Card id="bi-query-card" className="space-y-6">
              <div>
                <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                  Analytical Query Playground
                </h3>
                <p className="text-xs text-slate-400">
                  Execute serverless analytical queries against conformed gold Delta schemas.
                </p>
              </div>

              {/* Pre-written query picker */}
              <div className="flex gap-3">
                <button
                  onClick={() => setSelectedQuery(0)}
                  className={`px-4 py-2 rounded-lg text-xs font-semibold border transition-all duration-150 cursor-pointer ${
                    selectedQuery === 0
                      ? 'bg-blue-500/10 border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-[#1E293B]/40 text-slate-500 dark:text-slate-400'
                  }`}
                >
                  Query Store Sales
                </button>
                <button
                  onClick={() => setSelectedQuery(1)}
                  className={`px-4 py-2 rounded-lg text-xs font-semibold border transition-all duration-150 cursor-pointer ${
                    selectedQuery === 1
                      ? 'bg-blue-500/10 border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-[#1E293B]/40 text-slate-500 dark:text-slate-400'
                  }`}
                >
                  Query Demographics
                </button>
              </div>

              {/* Simulated Query editor box */}
              <div className="bg-[#0f172a] text-slate-100 rounded-xl p-5 font-mono text-xs border border-slate-800 shadow-inner relative">
                <Terminal className="absolute right-4 top-4 text-slate-500 w-4 h-4" />
                <span className="text-[10px] uppercase text-slate-500 font-bold block mb-3">Serverless SQL Engine</span>
                <pre className="text-blue-400 leading-relaxed overflow-x-auto whitespace-pre">
                  {sqlQueries[selectedQuery].sql}
                </pre>
              </div>

              {/* Query output */}
              <div className="space-y-3 pt-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase block tracking-wider font-sans">
                  Result Cache (Real-time catalog query)
                </span>
                <Table id="query-results-table" headers={sqlQueries[selectedQuery].headers}>
                  {sqlQueries[selectedQuery].rows.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-850/10">
                      {row.map((cell, cellIdx) => (
                        <td
                          key={cellIdx}
                          className={`px-5 py-3 text-xs ${
                            cellIdx === 0
                              ? 'font-bold text-slate-900 dark:text-white font-mono'
                              : 'text-slate-500 dark:text-slate-400 font-sans'
                          }`}
                        >
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </Table>
              </div>
            </Card>
          )}

          {activeTab === 'genai' && (
            <Card id="genai-grounding-card" className="space-y-6">
              <div>
                <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                  Contextual RAG Grounding Console
                </h3>
                <p className="text-xs text-slate-400">
                  Ground Large Language Models using conformed gold tables to guarantee auditability and eliminate hallucinations.
                </p>
              </div>

              <div className="space-y-3 font-sans">
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Instruction Prompt
                </label>
                <div className="flex flex-col sm:flex-row gap-3">
                  <input
                    type="text"
                    value={genAiPrompt}
                    onChange={(e) => setGenAiPrompt(e.target.value)}
                    className="flex-1 px-4 py-2.5 bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-lg text-xs dark:text-white focus:outline-none"
                  />
                  <Button
                    id="trigger-rag-simulate-btn"
                    variant="primary"
                    size="sm"
                    onClick={handlePromptSimulate}
                    disabled={isPromptGenerating}
                    icon={<Sparkles className="w-4 h-4 text-white fill-white" />}
                  >
                    {isPromptGenerating ? 'Grounding LLM...' : 'Analyze Context'}
                  </Button>
                </div>
              </div>

              {simulatedRagOutput && (
                <div className="bg-[#0f172a] text-slate-200 border border-slate-800 font-mono text-xs rounded-xl p-5 shadow-lg whitespace-pre-wrap leading-relaxed animate-fadeIn">
                  {simulatedRagOutput}
                </div>
              )}
            </Card>
          )}
        </div>

        {/* Right side helper info */}
        <div className="space-y-6 font-sans">
          <Card id="ai-active-consumers-card">
            <div className="mb-4">
              <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                Enterprise Consumer Matrix
              </h3>
              <p className="text-[11px] text-slate-400 mt-1">
                Conformed gold tier serving nodes optimized for high-performance enterprise workloads.
              </p>
            </div>
            
            <div className="space-y-3">
              {/* Feature Card 1: Machine Learning */}
              <div className="p-3 bg-blue-500/[0.02] dark:bg-blue-400/[0.01] border border-blue-200/20 dark:border-blue-900/20 rounded-xl flex gap-3 items-start">
                <div className="p-1.5 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg">
                  <Cpu className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-200">Offline Machine Learning (ML)</h4>
                  <p className="text-[10px] text-slate-400 leading-relaxed mt-0.5">
                    Feature tables optimized for training neural networks and gradient boosting models.
                  </p>
                </div>
              </div>

              {/* Feature Card 2: Serverless BI */}
              <div className="p-3 bg-emerald-500/[0.02] dark:bg-emerald-400/[0.01] border border-emerald-200/20 dark:border-emerald-900/20 rounded-xl flex gap-3 items-start">
                <div className="p-1.5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-lg">
                  <BarChart4 className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-200">Serverless BI Analytics</h4>
                  <p className="text-[10px] text-slate-400 leading-relaxed mt-0.5">
                    Zero-copy Direct Lake connection providing low-latency dashboard aggregations.
                  </p>
                </div>
              </div>

              {/* Feature Card 3: Generative AI */}
              <div className="p-3 bg-purple-500/[0.02] dark:bg-purple-400/[0.01] border border-purple-200/20 dark:border-purple-900/20 rounded-xl flex gap-3 items-start">
                <div className="p-1.5 bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded-lg">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-200">Generative AI / LLMs</h4>
                  <p className="text-[10px] text-slate-400 leading-relaxed mt-0.5">
                    Structured embeddings sync to vector databases for semantic grounding search.
                  </p>
                </div>
              </div>

              {/* Feature Card 4: Power BI Direct */}
              <div className="p-3 bg-amber-500/[0.02] dark:bg-amber-400/[0.01] border border-amber-200/20 dark:border-amber-900/20 rounded-xl flex gap-3 items-start">
                <div className="p-1.5 bg-amber-500/10 text-amber-600 dark:text-amber-450 rounded-lg">
                  <Layers className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-200">Power BI Zero-Copy</h4>
                  <p className="text-[10px] text-slate-400 leading-relaxed mt-0.5">
                    Eliminate duplication by reading direct S3 Parquet directories in Microsoft Fabric.
                  </p>
                </div>
              </div>

              {/* Feature Card 5: Safe RAG Grounding */}
              <div className="p-3 bg-sky-500/[0.02] dark:bg-sky-400/[0.01] border border-sky-200/20 dark:border-sky-900/20 rounded-xl flex gap-3 items-start">
                <div className="p-1.5 bg-sky-500/10 text-sky-600 dark:text-sky-400 rounded-lg">
                  <Lock className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 dark:text-slate-200">Compliance & RAG Guardrails</h4>
                  <p className="text-[10px] text-slate-400 leading-relaxed mt-0.5">
                    Strictly masked data fields block private identification vectors (PII leak guard).
                  </p>
                </div>
              </div>
            </div>
          </Card>

          <InsightCard
            id="ai-ready-architecture-insight"
            title="The Grounded Analytical Layer"
            purpose="Exposes fully cleansed, conformed, and masked Gold Delta tables for safe analytical queries, dashboards, and LLM completions."
            enterpriseProblem="Unstructured business files often contain duplicate records, invalid formats, or raw customer details (PII) that violate corporate compliance laws."
            azureEquivalent="Azure Synapse Analytics, Power BI Direct Lake"
            enterpriseExample="A secured Synapse endpoint syncing conformed Gold tables directly to a custom Power BI executive sales dashboard."
            whyExists="Enables zero-copy business operations, giving departments immediate, self-service access to high-trust metrics without file duplicates."
          />
        </div>
      </div>
    </div>
  );
};
