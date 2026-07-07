import React, { useState } from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PageHeader, Card, Button, Table, Badge, InsightCard } from '../components/UI';
import {
  UploadCloud,
  FileText,
  FileSpreadsheet,
  Plus,
  Play,
  Settings,
  HelpCircle,
  Database,
  ArrowRight,
  ShieldCheck,
  Server,
  Workflow,
  Target,
  AlertTriangle,
  Cloud,
  Briefcase,
  Lightbulb
} from 'lucide-react';

export const DataSources: React.FC = () => {
  const { datasets, addDataset, runIngestion } = usePlatform();
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [fileName, setFileName] = useState('');
  const [fileFormat, setFileFormat] = useState<'CSV' | 'JSON' | 'Parquet'>('CSV');
  const [fileSize, setFileSize] = useState('2.4 MB');
  const [fileSource, setFileSource] = useState('Local CSV File');
  const [isDragging, setIsDragging] = useState(false);

  // Handle Simulated Form Submit
  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fileName) return;

    let finalName = fileName;
    const ext = `.${fileFormat.toLowerCase()}`;
    if (!finalName.endsWith(ext)) {
      finalName += ext;
    }

    addDataset(finalName, fileFormat, fileSize, fileSource);
    setFileName('');
    setShowUploadForm(false);
  };

  // Drag and Drop simulation
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFileName = 'transactions_export_' + Math.floor(Math.random() * 100) + '.csv';
    addDataset(droppedFileName, 'CSV', '12.8 MB', 'S3 Bucket Dump');
  };

  return (
    <div id="datasources-page-container" className="space-y-8 animate-fadeIn">
      <PageHeader
        id="sources-header-block"
        title="Data Sources Directory"
        description="Register and land raw source datasets into the bronze storage tier. Simulate loading sales logs, user profiles, ERP catalogs, or dynamic sensor feeds."
        actions={
          <Button
            id="open-upload-modal-btn"
            variant="primary"
            size="sm"
            icon={<Plus className="w-4 h-4" />}
            onClick={() => setShowUploadForm(true)}
          >
            Register Source File
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          
          {/* File Drag / Drop Simulator */}
          <div
            id="upload-drag-zone"
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center transition-all duration-200 cursor-pointer ${
              isDragging
                ? 'border-blue-500 bg-blue-50/45 dark:bg-blue-950/15'
                : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-[#1E293B]/40 hover:border-blue-500 dark:hover:border-blue-500'
            }`}
          >
            <div className="p-3 bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 rounded-lg border border-blue-100 dark:border-blue-900/30 mb-4">
              <UploadCloud className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-800 dark:text-white font-sans">
              Drag and drop raw analytical files here
            </h3>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1 max-w-sm">
              Supports raw CSV, JSON, or Snappy Parquet logs. Landed files immediately appear in the raw MinIO bucket queue.
            </p>
            <div className="flex items-center gap-2 mt-4 text-xs">
              <span className="text-slate-400">or</span>
              <button
                id="trigger-manual-form-btn"
                onClick={() => setShowUploadForm(true)}
                className="text-blue-600 dark:text-blue-400 font-bold hover:underline"
              >
                manually register metadata coordinates
              </button>
            </div>
          </div>

          {/* Dataset list Table */}
          <Card id="dataset-list-panel">
            <div className="flex justify-between items-center mb-5">
              <div>
                <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider font-sans">
                  Landed Data Catalog
                </h3>
                <p className="text-xs text-slate-400">
                  Registered raw datasets awaiting validation and Delta compilation.
                </p>
              </div>
              <span className="text-xs font-mono font-bold bg-slate-100 dark:bg-slate-800 border px-2.5 py-1 rounded-lg dark:text-slate-300">
                {datasets.length} Active Sources
              </span>
            </div>

            <Table
              id="datasets-data-table"
              headers={['Dataset Name', 'Format', 'Source Origin', 'Size', 'Status', 'Pipeline Action']}
            >
              {datasets.map((dataset) => (
                <tr 
                  key={dataset.id} 
                  className="hover:bg-blue-500/[0.02] dark:hover:bg-blue-400/[0.015] border-l border-transparent hover:border-l-blue-500 transition-all duration-150"
                >
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      {dataset.format === 'CSV' ? (
                        <div className="p-1.5 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 rounded border border-emerald-100 dark:border-emerald-900/30">
                          <FileSpreadsheet className="w-3.5 h-3.5" />
                        </div>
                      ) : (
                        <div className="p-1.5 bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 rounded border border-blue-100 dark:border-blue-900/30">
                          <FileText className="w-3.5 h-3.5" />
                        </div>
                      )}
                      <div>
                        <span className="text-xs font-bold text-slate-900 dark:text-slate-100 font-mono block">
                          {dataset.name}
                        </span>
                        <span className="text-[9px] text-slate-400 dark:text-slate-500 font-mono mt-0.5 block">
                          Landed: {dataset.uploadedAt}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <span className="text-[10px] font-bold font-mono bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                      {dataset.format}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-xs text-slate-500 dark:text-slate-400 font-sans">
                    {dataset.source}
                  </td>
                  <td className="px-5 py-4 text-xs font-mono font-bold text-slate-700 dark:text-slate-300">
                    {dataset.size}
                  </td>
                  <td className="px-5 py-4">
                    <Badge
                      id={`status-badge-${dataset.id}`}
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
                  </td>
                  <td className="px-5 py-4">
                    {dataset.status === 'Raw' ? (
                      <Button
                        id={`trigger-ingest-${dataset.id}`}
                        variant="success"
                        size="sm"
                        icon={<Play className="w-3 h-3 text-white fill-white" />}
                        onClick={() => runIngestion(dataset.id)}
                      >
                        Run Ingest
                      </Button>
                    ) : (
                      <span className="text-[11px] text-slate-400 dark:text-slate-500 font-bold italic font-sans flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                        Compacted
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </Table>
          </Card>
        </div>

        {/* Right sidebar details */}
        <div className="space-y-6">
          <Card id="datasources-summary-card">
            <h3 className="text-xs font-bold text-slate-800 dark:text-white uppercase tracking-wider mb-4 font-sans">
              MinIO Storage Node Config
            </h3>
            <div className="space-y-1.5">
              <div className="flex justify-between items-center py-2 border-b border-slate-50 dark:border-slate-800 text-xs">
                <span className="text-slate-400 dark:text-slate-500 font-sans">S3 Adapter Protocol</span>
                <span className="font-mono font-bold text-slate-800 dark:text-slate-200">s3a://</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-50 dark:border-slate-800 text-xs">
                <span className="text-slate-400 dark:text-slate-500 font-sans">S3 Region Host</span>
                <span className="font-mono font-bold text-emerald-500">us-east-1 (local-net)</span>
              </div>
              <div className="flex justify-between items-center py-2 text-xs">
                <span className="text-slate-400 dark:text-slate-500 font-sans">SSL Certification</span>
                <span className="font-mono font-bold text-blue-500">Mutual TLS Enforced</span>
              </div>
            </div>
          </Card>

          <div className="space-y-4 font-sans">
            <h3 className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider font-sans">
              Data Landing Educational Matrix
            </h3>
            
            {/* Card 1: Purpose */}
            <div className="bg-white dark:bg-[#1E293B]/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex gap-3 items-start">
              <div className="p-1.5 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg flex-shrink-0">
                <Target className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-850 dark:text-slate-200">1. Purpose</span>
                  <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded border border-blue-500/20">Landed Zone</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  Gathers raw operations logs & profiles securely into unified S3 landing buckets.
                </p>
              </div>
            </div>

            {/* Card 2: Enterprise Problem */}
            <div className="bg-white dark:bg-[#1E293B]/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex gap-3 items-start">
              <div className="p-1.5 bg-amber-500/10 text-amber-600 dark:text-amber-450 rounded-lg flex-shrink-0">
                <AlertTriangle className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-850 dark:text-slate-200">2. Enterprise Problem</span>
                  <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-amber-500/10 text-amber-600 dark:text-amber-450 rounded border border-amber-500/20">DB Overloads</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  Direct database queries degrade operational systems, causing performance lag or downtime.
                </p>
              </div>
            </div>

            {/* Card 3: Azure Equivalent */}
            <div className="bg-white dark:bg-[#1E293B]/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex gap-3 items-start">
              <div className="p-1.5 bg-sky-500/10 text-sky-600 dark:text-sky-400 rounded-lg flex-shrink-0">
                <Cloud className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-850 dark:text-slate-200">3. Azure Equivalent</span>
                  <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-sky-500/10 text-sky-600 dark:text-sky-400 rounded border border-sky-500/20">ADLS Gen2</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  Azure Data Lake Storage Gen2 combined with Synapse Copy Activities.
                </p>
              </div>
            </div>

            {/* Card 4: Enterprise Example */}
            <div className="bg-white dark:bg-[#1E293B]/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex gap-3 items-start">
              <div className="p-1.5 bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded-lg flex-shrink-0">
                <Briefcase className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-850 dark:text-slate-200">4. Real Enterprise Example</span>
                  <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded border border-purple-500/20">S3 Batch Dump</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                  ADLS Gen2 receiving hourly 10MB POS JSON dumps from 1,200 global stores.
                </p>
              </div>
            </div>

            {/* Card 5: Key Takeaway */}
            <div className="bg-white dark:bg-[#1E293B]/40 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 shadow-xs hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-150 flex gap-3 items-start border-l-4 border-l-emerald-500 dark:border-l-emerald-500">
              <div className="p-1.5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-lg flex-shrink-0">
                <Lightbulb className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-850 dark:text-slate-200">5. Key Takeaway</span>
                  <span className="text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded border border-emerald-500/20">Data Replay</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed italic">
                  Provides an immutable audit layer to easily rerun downstream tables or debug.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Dialog Form */}
      {showUploadForm && (
        <div id="modal-backdrop" className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 dark:bg-slate-950/60 backdrop-blur-xs">
          <Card id="upload-dialog" className="w-full max-w-md border border-slate-250 dark:border-slate-800 shadow-2xl animate-fadeIn">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100 dark:border-slate-800 mb-5">
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider font-sans">
                Register Raw Dataset Coordinates
              </h3>
              <button
                onClick={() => setShowUploadForm(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4 text-xs font-sans">
              <div className="space-y-1.5">
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Logical Dataset Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. ad_analytics_logs"
                  value={fileName}
                  onChange={(e) => setFileName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none dark:text-white font-mono"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Physical Format
                  </label>
                  <select
                    value={fileFormat}
                    onChange={(e) => setFileFormat(e.target.value as any)}
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none dark:text-white"
                  >
                    <option value="CSV">CSV</option>
                    <option value="JSON">JSON</option>
                    <option value="Parquet">Snappy Parquet</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Simulated Payload Size
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 15.4 MB"
                    value={fileSize}
                    onChange={(e) => setFileSize(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none dark:text-white"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Source Origin System Label
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Salesforce CRM / MQTT Sensor Stream"
                  value={fileSource}
                  onChange={(e) => setFileSource(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none dark:text-white"
                />
              </div>

              <div className="flex justify-end gap-2.5 pt-4 border-t border-slate-100 dark:border-slate-800 mt-6">
                <Button id="cancel-upload-btn" variant="outline" size="sm" type="button" onClick={() => setShowUploadForm(false)}>
                  Cancel
                </Button>
                <Button id="submit-upload-btn" variant="primary" size="sm" type="submit">
                  Simulate Land
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
};
