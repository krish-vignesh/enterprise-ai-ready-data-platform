import React from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PlatformHealth } from '../components/PlatformHealth';
import { PageHeader, Card, Button, Badge } from '../components/UI';
import {
  Settings as SettingsIcon,
  Sun,
  Moon,
  Info,
  Sliders,
  Bell,
  Cpu,
  Monitor,
  Activity
} from 'lucide-react';

export const Settings: React.FC = () => {
  const { theme, toggleTheme } = usePlatform();

  return (
    <div id="settings-page-container" className="space-y-8 animate-fadeIn font-sans">
      <PageHeader
        id="settings-header-block"
        title="Platform Administration"
        description="Configure sandbox cluster executors, SLA thresholds, parquet compression parameters, and user interfaces."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Visual Customization Card */}
          <Card id="settings-theme-panel">
            <div className="mb-6">
              <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                Interface Customization
              </h3>
              <p className="text-xs text-slate-400">
                Toggle the sandbox visualization engine between conformed light mode and ACID dark mode.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 font-sans">
              <button
                onClick={() => theme === 'dark' && toggleTheme()}
                className={`flex-1 p-5 rounded-xl border text-center flex flex-col items-center justify-center gap-2.5 transition-all duration-150 cursor-pointer ${
                  theme === 'light'
                    ? 'border-blue-500 bg-blue-500/10 text-blue-600 font-bold'
                    : 'border-slate-200 dark:border-slate-850 bg-slate-50 dark:bg-[#1E293B]/20 text-slate-400 dark:text-slate-500 hover:bg-slate-100 dark:hover:bg-[#1E293B]/40'
                }`}
              >
                <Sun className="w-5 h-5 text-amber-500" />
                <div className="space-y-0.5">
                  <span className="text-xs font-bold block">Enterprise Light</span>
                  <span className="text-[10px] opacity-75 font-normal">Sleek off-white surfaces</span>
                </div>
              </button>

              <button
                onClick={() => theme === 'light' && toggleTheme()}
                className={`flex-1 p-5 rounded-xl border text-center flex flex-col items-center justify-center gap-2.5 transition-all duration-150 cursor-pointer ${
                  theme === 'dark'
                    ? 'border-blue-500 bg-blue-500/10 text-blue-400 font-bold'
                    : 'border-slate-200 dark:border-slate-850 bg-slate-50 dark:bg-[#1E293B]/20 text-slate-400 dark:text-slate-500 hover:bg-slate-100 dark:hover:bg-[#1E293B]/40'
                }`}
              >
                <Moon className="w-5 h-5 text-blue-400" />
                <div className="space-y-0.5">
                  <span className="text-xs font-bold block">ACID Dark Mode</span>
                  <span className="text-[10px] opacity-75 font-normal">Slate eye-safe design</span>
                </div>
              </button>
            </div>
          </Card>

          {/* Sandbox Configurations */}
          <Card id="settings-spark-config-panel">
            <div className="mb-6">
              <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-blue-500" /> Spark Cluster Tuning
              </h3>
              <p className="text-xs text-slate-400">
                Adjust virtual memory parameters and catalog partitions inside this sandbox workspace.
              </p>
            </div>

            <div className="space-y-5 text-xs font-sans">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-bold text-slate-400 uppercase">
                    Parquet Compression format
                  </label>
                  <select className="w-full px-3.5 py-2 bg-slate-50 dark:bg-[#0f172a]/60 border border-slate-250 dark:border-slate-800 rounded-lg focus:outline-none dark:text-white text-xs font-sans">
                    <option>Snappy Parquet (Production Standard)</option>
                    <option>GZIP (Highly Compressed)</option>
                    <option>Uncompressed (Performance Audit)</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-bold text-slate-400 uppercase">
                    Compute Executor Layout
                  </label>
                  <select className="w-full px-3.5 py-2 bg-slate-50 dark:bg-[#0f172a]/60 border border-slate-250 dark:border-slate-800 rounded-lg focus:outline-none dark:text-white text-xs font-sans">
                    <option>Standard: 8 Cores, 32GB RAM</option>
                    <option>Performance: 16 Cores, 64GB RAM</option>
                    <option>Enterprise Multi-Node: 32 Cores, 128GB RAM</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5 pt-2">
                <label className="block text-[10px] font-bold text-slate-400 uppercase">
                  Quality SLA Warning Threshold
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="50"
                    max="100"
                    defaultValue="95"
                    className="flex-1 accent-blue-500 h-1 bg-slate-200 dark:bg-slate-800 rounded cursor-pointer"
                  />
                  <span className="font-mono font-bold text-slate-800 dark:text-white bg-slate-100 dark:bg-slate-800 border dark:border-slate-800 px-2.5 py-1 rounded">
                    95% SLA Target
                  </span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Info card on right side */}
        <div className="space-y-6">
          <Card id="settings-about-card">
            <div className="mb-4">
              <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans flex items-center gap-1.5">
                <Info className="w-4 h-4 text-slate-400" /> Platform Specification
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                This platform is an educational conformed sandbox simulation mapping Apache Spark workflows onto logical Medallion zones. No live billing is active.
              </p>
            </div>
            
            <div className="space-y-2.5 border-t border-slate-100 dark:border-slate-850 pt-4 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-slate-50 dark:border-slate-900">
                <span className="text-slate-400">Environment</span>
                <span className="text-emerald-500 font-bold uppercase text-[10px] bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-250 dark:border-emerald-900/30 px-1.5 py-0.5 rounded">Local Sandbox</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50 dark:border-slate-900">
                <span className="text-slate-400">S3 Adapter</span>
                <span className="text-slate-700 dark:text-slate-300">MinIO Client</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Host Engine</span>
                <span className="text-slate-700 dark:text-slate-300">local-master:3000</span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      <div className="pt-4 border-t border-border/45">
        <PlatformHealth />
      </div>
    </div>
  );
};
