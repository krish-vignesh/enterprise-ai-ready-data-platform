import React from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PageHeader, Card, Button, Table, Badge, InsightCard } from '../components/UI';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Settings,
  HelpCircle,
  TrendingUp,
  Activity,
  Zap,
  Gauge
} from 'lucide-react';

export const DataQuality: React.FC = () => {
  const { qualityRules, updateQualityRule } = usePlatform();

  // Metrics Calculations
  const totalRules = qualityRules.length;
  const passedRules = qualityRules.filter((r) => r.status === 'PASSED').length;
  const failedRules = qualityRules.filter((r) => r.status === 'FAILED').length;
  const warningRules = qualityRules.filter((r) => r.status === 'WARNING').length;

  const qualityScore = totalRules > 0 ? Math.round((passedRules / totalRules) * 100) : 100;

  // Custom Radial SVG Gauge render
  const renderQualityGauge = () => {
    const radius = 50;
    const strokeWidth = 8;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (qualityScore / 100) * circumference;

    let scoreColor = 'stroke-emerald-500';
    let textColor = 'text-emerald-500 bg-emerald-500/10';
    if (qualityScore < 70) {
      scoreColor = 'stroke-rose-500';
      textColor = 'text-rose-500 bg-rose-500/10';
    } else if (qualityScore < 90) {
      scoreColor = 'stroke-amber-500';
      textColor = 'text-amber-500 bg-amber-500/10';
    }

    return (
      <div id="quality-gauge-radial" className="flex flex-col items-center justify-center p-6 text-center">
        <div className="relative w-32 h-32">
          {/* Background circle track */}
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r={radius}
              className="stroke-slate-100 dark:stroke-slate-800"
              strokeWidth={strokeWidth}
              fill="none"
            />
            {/* Value stroke track */}
            <circle
              cx="64"
              cy="64"
              r={radius}
              className={`transition-all duration-300 ${scoreColor}`}
              strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              fill="none"
            />
          </svg>
          {/* Percentage value text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-black font-mono tracking-tight text-slate-900 dark:text-white">
              {qualityScore}%
            </span>
            <span className="text-[9px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider mt-0.5 font-sans">
              Quality Index
            </span>
          </div>
        </div>

        {/* Status sub-label */}
        <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold">
          {qualityScore >= 90 ? (
            <span className="text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200/40 dark:border-emerald-900/30 px-2.5 py-0.5 rounded flex items-center gap-1 font-sans">
              <CheckCircle2 className="w-3.5 h-3.5" /> SLA Compliant
            </span>
          ) : qualityScore >= 70 ? (
            <span className="text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border border-amber-200/40 dark:border-amber-900/30 px-2.5 py-0.5 rounded flex items-center gap-1 font-sans">
              <AlertTriangle className="w-3.5 h-3.5" /> SLA Warn Alert
            </span>
          ) : (
            <span className="text-rose-700 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border border-rose-200/40 dark:border-rose-900/30 px-2.5 py-0.5 rounded flex items-center gap-1 font-sans">
              <XCircle className="w-3.5 h-3.5" /> SLA Fault State
            </span>
          )}
        </div>
      </div>
    );
  };

  return (
    <div id="dataquality-page-container" className="space-y-8 animate-fadeIn">
      <PageHeader
        id="quality-header-block"
        title="Data Quality Expectations"
        description="Configure declarative constraints verifying null thresholds, format outliers, and value boundaries before committing Delta gold tables."
      />

      {/* Grid: Gauge + Aggregates */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Quality Score Gauge Card */}
        <Card id="quality-gauge-card" className="flex flex-col justify-between">
          <div className="space-y-1">
            <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
              Quality Score Tracker
            </h3>
            <p className="text-xs text-slate-400">
              Aggregated assertion metrics conformed over all Silver and Gold Delta records.
            </p>
          </div>
          {renderQualityGauge()}
          <div className="text-[10px] text-slate-400 dark:text-slate-500 border-t border-slate-100 dark:border-slate-800 pt-4 text-center font-sans">
            Evaluated live over {totalRules} active assertions
          </div>
        </Card>

        {/* Quality Aggregates List */}
        <div className="lg:col-span-2 space-y-6">
          <Card id="quality-aggregates-card" className="h-full flex flex-col justify-between">
            <div>
              <div className="mb-6">
                <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                  Assertion Status Summary
                </h3>
                <p className="text-xs text-slate-400">
                  Global data quality thresholds mapped onto real-time incoming records.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-sans">
                <div className="p-4 bg-emerald-50 dark:bg-[#122c22]/30 border border-emerald-100 dark:border-emerald-900/40 rounded-xl">
                  <div className="flex justify-between items-center text-emerald-600 dark:text-emerald-400">
                    <span className="text-[10px] font-bold uppercase tracking-wider">Passed rules</span>
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <p className="text-2xl font-black font-mono text-emerald-600 dark:text-emerald-400 mt-2">
                    {passedRules}
                  </p>
                </div>

                <div className="p-4 bg-amber-50 dark:bg-[#342718]/30 border border-amber-100 dark:border-amber-900/40 rounded-xl">
                  <div className="flex justify-between items-center text-amber-600 dark:text-amber-400">
                    <span className="text-[10px] font-bold uppercase tracking-wider">Warning levels</span>
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <p className="text-2xl font-black font-mono text-amber-600 dark:text-amber-400 mt-2">
                    {warningRules}
                  </p>
                </div>

                <div className="p-4 bg-rose-50 dark:bg-[#2c151b]/30 border border-rose-100 dark:border-rose-900/40 rounded-xl">
                  <div className="flex justify-between items-center text-rose-600 dark:text-rose-400">
                    <span className="text-[10px] font-bold uppercase tracking-wider">Failed exceptions</span>
                    <XCircle className="w-4 h-4" />
                  </div>
                  <p className="text-2xl font-black font-mono text-rose-600 dark:text-rose-400 mt-2">
                    {failedRules}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-slate-50 dark:bg-[#0f172a]/30 rounded-lg p-4 border border-slate-100 dark:border-slate-800 mt-6 flex justify-between items-center text-xs font-sans">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-blue-500 animate-pulse" />
                <span className="text-slate-500 dark:text-slate-400">
                  Global quality SLA is set to <strong className="font-mono text-slate-800 dark:text-slate-200">95%</strong>
                </span>
              </div>
              <Badge id="badge-sla" content="SLA Monitored" variant="primary" />
            </div>
          </Card>
        </div>
      </div>

      {/* Rules list with Toggle action buttons */}
      <Card id="quality-rules-table-panel">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
              Configured Expectation Declarations
            </h3>
            <p className="text-xs text-slate-400">
              Interactive sandbox simulation controls: toggle statuses to test alerts and schema compliance.
            </p>
          </div>
          <span className="text-xs font-mono font-bold bg-slate-100 dark:bg-slate-800 border px-2.5 py-1 rounded-lg dark:text-slate-300">
            {qualityRules.length} Assertions Active
          </span>
        </div>

        <Table id="quality-rules-table" headers={['Target Table', 'Expectation Expression', 'Constraint Type', 'Passed / Failed Rows', 'State', 'Simulation Actions']}>
          {qualityRules.map((rule) => (
            <tr 
              key={rule.id} 
              className="hover:bg-blue-500/[0.02] dark:hover:bg-blue-400/[0.015] transition-colors duration-150 border-l border-transparent hover:border-l-blue-500"
            >
              <td className="px-5 py-4 font-mono text-xs font-bold text-slate-900 dark:text-white">
                {rule.tableName}
              </td>
              <td className="px-5 py-4 font-sans">
                <div>
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200 font-mono">
                    {rule.ruleName}
                  </span>
                  {rule.errorMessage && (
                    <span className="text-[10px] text-rose-500 block mt-1 font-mono">
                      Error Log: {rule.errorMessage}
                    </span>
                  )}
                </div>
              </td>
              <td className="px-5 py-4 text-xs font-sans text-slate-500 dark:text-slate-400">
                {rule.type}
              </td>
              <td className="px-5 py-4">
                <div className="text-xs font-mono">
                  <span className="text-slate-800 dark:text-slate-200 font-bold">
                    {rule.checkedRecords.toLocaleString()}
                  </span>
                  <span className="text-slate-400"> / </span>
                  <span className={rule.failedRecords > 0 ? 'text-rose-500 font-bold animate-pulse' : 'text-slate-400'}>
                    {rule.failedRecords.toLocaleString()}
                  </span>
                </div>
              </td>
              <td className="px-5 py-4">
                <Badge
                  id={`badge-rule-${rule.id}`}
                  content={rule.status}
                  variant={
                    rule.status === 'PASSED'
                      ? 'success'
                      : rule.status === 'WARNING'
                      ? 'warning'
                      : 'danger'
                  }
                />
              </td>
              <td className="px-5 py-4">
                <div className="flex items-center gap-2 justify-start md:justify-end">
                  <button
                    onClick={() => updateQualityRule(rule.id, 'PASSED')}
                    className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-350 bg-emerald-500/10 hover:bg-emerald-500/20 px-2.5 py-1 rounded-lg border border-emerald-500/20 dark:border-emerald-800/40 cursor-pointer transition-all duration-150 hover:shadow-xs"
                  >
                    Simulate Pass
                  </button>
                  <button
                    onClick={() => updateQualityRule(rule.id, 'FAILED')}
                    className="text-[10px] font-bold text-rose-600 dark:text-rose-450 hover:text-rose-700 dark:hover:text-rose-400 bg-rose-500/10 hover:bg-rose-500/20 px-2.5 py-1 rounded-lg border border-rose-500/20 dark:border-rose-800/40 cursor-pointer transition-all duration-150 hover:shadow-xs"
                  >
                    Simulate Fail
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </Table>
      </Card>

      <InsightCard
        id="quality-architecture-insight"
        title="DLT Expectations & Schema Gates"
        purpose="Enforces programmatic null-value validations, data range boundaries, and format checks directly inside active pipeline executions."
        enterpriseProblem="Incomplete or corrupted customer entries leak into master analytics systems, producing incorrect business dashboards and breaking reports."
        azureEquivalent="Databricks Delta Live Tables (DLT) Expectations, Azure Purview DQ Rules"
        enterpriseExample="A declarative constraint rule that isolates POS entries lacking a valid transaction price directly into quarantine buckets."
        whyExists="Establishes mathematical trust and reliability in analytical tables before business analysts or ML algorithms query them."
      />
    </div>
  );
};
