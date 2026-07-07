import React from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PageHeader, Card, Badge, InsightCard } from '../components/UI';
import {
  Layers,
  FolderOpen,
  FileCode,
  HardDrive,
  Cpu,
  ArrowRight,
  Folder,
  FileText,
  Boxes
} from 'lucide-react';

export const DataLake: React.FC = () => {
  const { datasets, deltaTables } = usePlatform();

  // Zone categorizations
  const rawDatasets = datasets.filter((d) => d.status === 'Raw');
  const processedDatasets = datasets.filter((d) => d.status === 'Processed');
  const curatedDatasets = deltaTables;

  const zones = [
    {
      id: 'lake-zone-bronze',
      name: 'Raw Landing Zone (Bronze)',
      color: 'bg-amber-500',
      textColor: 'text-amber-500',
      badgeColor: 'warning' as const,
      borderColor: 'border-t-amber-500 dark:border-t-amber-500',
      path: 's3a://data-lake/bronze/raw_landing/',
      desc: 'Immutable landing directory. Stores un-processed formats (JSON payload feeds, local Excel/CSV raw exports) preserving original characters.',
      metrics: { files: rawDatasets.length + 2, size: '1.24 GB', format: 'CSV, JSON' },
      contents: [
        { name: 'iot_sensor_stream/year=2026/month=07/', type: 'Directory' },
        { name: 'retail_transactions_raw_dump.json', type: 'JSON Stream' },
        { name: 'customer_profiles_salesforce.csv', type: 'CSV Table' },
      ],
    },
    {
      id: 'lake-zone-silver',
      name: 'Processed Zone (Silver)',
      color: 'bg-blue-500',
      textColor: 'text-blue-500',
      badgeColor: 'primary' as const,
      borderColor: 'border-t-blue-500 dark:border-t-blue-500',
      path: 's3a://data-lake/silver/schema_conformed/',
      desc: 'Cleaned, schema-matched partition tables. Data is typed, columns validated, PII coordinates tagged, and saved in optimized parquet.',
      metrics: { files: processedDatasets.length + 3, size: '0.90 GB', format: 'Snappy Parquet' },
      contents: [
        { name: 'conformed_product_catalog/', type: 'Parquet Partition' },
        { name: 'iot_aggregates_silver/', type: 'Parquet Partition' },
        { name: 'cleansed_transactions_silver/', type: 'Parquet Partition' },
      ],
    },
    {
      id: 'lake-zone-gold',
      name: 'Curated Zone (Gold)',
      color: 'bg-emerald-500',
      textColor: 'text-emerald-500',
      badgeColor: 'success' as const,
      borderColor: 'border-t-emerald-500 dark:border-t-emerald-500',
      path: 's3a://data-lake/gold/analytics_ready/',
      desc: 'Aggregated analytics tables formatted in Delta Lake ACID. Built for ultra-fast queries, dynamic upserts, and time-travel rollbacks.',
      metrics: { files: curatedDatasets.length, size: '0.52 GB', format: 'Delta ACID format' },
      contents: curatedDatasets.map((t) => ({ name: `${t.name}/`, type: 'Delta Parquet Table' })),
    },
  ];

  return (
    <div id="datalake-page-container" className="space-y-8 animate-fadeIn">
      <PageHeader
        id="lake-header-block"
        title="Data Lake Storage Explorer"
        description="Inspect logical object directory trees mapped over local S3/MinIO buckets representing conformed Medallion levels."
      />

      {/* Storage Allocation Summary */}
      <div id="datalake-total-summary-card" className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card id="summary-bronze" className="border-l-4 border-l-amber-500 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Raw Land Volume</span>
            <span className="text-2xl font-extrabold font-mono text-slate-900 dark:text-white mt-1 block">1.24 GB</span>
          </div>
          <Badge id="badge-sum-bronze" content="Bronze Storage" variant="warning" />
        </Card>
        <Card id="summary-silver" className="border-l-4 border-l-blue-500 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Validated Parquet</span>
            <span className="text-2xl font-extrabold font-mono text-slate-900 dark:text-white mt-1 block">0.90 GB</span>
          </div>
          <Badge id="badge-sum-silver" content="Silver Storage" variant="primary" />
        </Card>
        <Card id="summary-gold" className="border-l-4 border-l-emerald-500 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">ACID Delta Tables</span>
            <span className="text-2xl font-extrabold font-mono text-slate-900 dark:text-white mt-1 block">0.52 GB</span>
          </div>
          <Badge id="badge-sum-gold" content="Gold Storage" variant="success" />
        </Card>
      </div>

      {/* Main medalliion zones layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {zones.map((zone) => (
          <Card key={zone.id} id={zone.id} className={`flex flex-col justify-between border-t-4 ${zone.borderColor}`}>
            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xs font-bold text-slate-900 dark:text-white font-sans uppercase tracking-wider flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${zone.color}`} />
                  {zone.name}
                </h3>
                <Badge id={`badge-${zone.id}`} content={`${zone.metrics.files} Files`} variant={zone.badgeColor} />
              </div>

              {/* Path prefix info box */}
              <div className="bg-slate-50 dark:bg-[#0f172a]/45 rounded-lg p-3 mb-4 border border-slate-100 dark:border-slate-800">
                <span className="text-[9px] uppercase font-bold text-slate-400 font-sans">Object bucket path</span>
                <p className="text-[10px] font-mono text-blue-600 dark:text-blue-400 font-semibold break-all mt-1">
                  {zone.path}
                </p>
              </div>

              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mb-5 font-sans">
                {zone.desc}
              </p>

              {/* Bucket list directories */}
              <div className="space-y-2.5 border-t border-slate-100 dark:border-slate-800 pt-4 mb-6">
                <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">
                  Virtual File System Tree
                </span>
                {zone.contents.length === 0 ? (
                  <p className="text-[10px] text-slate-400 italic">No files located in this partition.</p>
                ) : (
                  <div className="space-y-1.5">
                    {zone.contents.map((item, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between text-xs p-2 bg-slate-50 dark:bg-[#0F172A]/20 border border-slate-100/50 dark:border-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                      >
                        <div className="flex items-center gap-2 overflow-hidden mr-2">
                          {item.name.endsWith('/') ? (
                            <Folder className="w-3.5 h-3.5 text-blue-500 flex-shrink-0" />
                          ) : (
                            <FileText className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                          )}
                          <span className="font-mono text-[11px] text-slate-700 dark:text-slate-300 truncate">
                            {item.name}
                          </span>
                        </div>
                        <span className="text-[9px] font-bold text-slate-400 font-sans uppercase flex-shrink-0">
                          {item.type}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Zone Telemetry */}
            <div className="border-t border-slate-100 dark:border-slate-800 pt-4 grid grid-cols-2 gap-4 text-center">
              <div className="p-2.5 bg-slate-50 dark:bg-[#0F172A]/20 rounded-lg border border-slate-100 dark:border-slate-800">
                <span className="text-[9px] uppercase font-bold text-slate-400">Total size</span>
                <p className="text-xs font-bold font-mono text-slate-800 dark:text-slate-200 mt-1">
                  {zone.metrics.size}
                </p>
              </div>
              <div className="p-2.5 bg-slate-50 dark:bg-[#0F172A]/20 rounded-lg border border-slate-100 dark:border-slate-800">
                <span className="text-[9px] uppercase font-bold text-slate-400">Disk format</span>
                <p className="text-xs font-bold font-mono text-blue-500 mt-1">
                  {zone.metrics.format}
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <InsightCard
        id="lake-architecture-insight"
        title="Durable Object Storage Zone"
        purpose="Provides a scalable, cost-efficient, and secure directory lakehouse layout utilizing Bronze, Silver, and Gold tiers."
        enterpriseProblem="Traditional relational databases charge high premium fees for terabytes of raw unstructured log datasets."
        azureEquivalent="Azure Data Lake Storage Gen2 (ADLS)"
        enterpriseExample="An ADLS container partition tree storing massive files organized by year, month, and transaction hour."
        whyExists="Establishes a centralized source-of-truth datalake, allowing massive Spark computing nodes to perform on-demand transformations."
      />
    </div>
  );
};
