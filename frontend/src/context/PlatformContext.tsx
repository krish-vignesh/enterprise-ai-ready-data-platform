import React, { createContext, useContext, useState, useEffect } from 'react';
import { PageId, Dataset, IngestionJob, SparkJob, DeltaTable, QualityRule } from '../types';

interface PlatformContextProps {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  activePage: PageId;
  setActivePage: (page: PageId) => void;
  datasets: Dataset[];
  ingestionJobs: IngestionJob[];
  sparkJobs: SparkJob[];
  deltaTables: DeltaTable[];
  qualityRules: QualityRule[];
  addDataset: (name: string, format: 'CSV' | 'JSON' | 'Parquet', size: string, source: string) => void;
  runIngestion: (id: string) => Promise<void>;
  runSparkProcessing: (jobId: string) => Promise<void>;
  updateQualityRule: (ruleId: string, status: 'PASSED' | 'FAILED' | 'WARNING') => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  selectedTableId: string;
  setSelectedTableId: (id: string) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const PlatformContext = createContext<PlatformContextProps | undefined>(undefined);

export const PlatformProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [activePage, setActivePage] = useState<PageId>('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTableId, setSelectedTableId] = useState('customer_master');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Initial Data Sources / Datasets
  const [datasets, setDatasets] = useState<Dataset[]>([
    {
      id: 'ds-1',
      name: 'customer_profiles',
      format: 'CSV',
      size: '14.2 MB',
      source: 'Salesforce CRM',
      rowCount: 125400,
      uploadedAt: '2026-07-01 10:14',
      status: 'Curated',
      owner: 'Data Platform Team',
      columns: [
        { name: 'customer_id', type: 'VARCHAR(50)', nullable: false, description: 'Unique identifier for the customer' },
        { name: 'first_name', type: 'VARCHAR(100)', nullable: false, description: 'Customer first name' },
        { name: 'last_name', type: 'VARCHAR(100)', nullable: false, description: 'Customer last name' },
        { name: 'email', type: 'VARCHAR(255)', nullable: false, description: 'Primary email address' },
        { name: 'country', type: 'VARCHAR(100)', nullable: true, description: 'Signup location' },
        { name: 'created_at', type: 'TIMESTAMP', nullable: false, description: 'Profile creation date' },
      ],
    },
    {
      id: 'ds-2',
      name: 'retail_transactions',
      format: 'JSON',
      size: '185.7 MB',
      source: 'POS Terminal Ingestion',
      rowCount: 1482000,
      uploadedAt: '2026-07-01 11:30',
      status: 'Curated',
      owner: 'Analytics Team',
      columns: [
        { name: 'transaction_id', type: 'VARCHAR(64)', nullable: false, description: 'Unique identifier for the sale' },
        { name: 'customer_id', type: 'VARCHAR(50)', nullable: true, description: 'Associated customer ID' },
        { name: 'store_id', type: 'INT', nullable: false, description: 'Store location identifier' },
        { name: 'amount', type: 'DECIMAL(10,2)', nullable: false, description: 'Transaction amount' },
        { name: 'timestamp', type: 'TIMESTAMP', nullable: false, description: 'Date and time of transaction' },
      ],
    },
    {
      id: 'ds-3',
      name: 'product_catalog',
      format: 'CSV',
      size: '1.8 MB',
      source: 'ERP Master Database',
      rowCount: 12500,
      uploadedAt: '2026-07-02 01:22',
      status: 'Processed',
      owner: 'Merchandising Team',
      columns: [
        { name: 'product_id', type: 'VARCHAR(50)', nullable: false, description: 'Primary product SKU' },
        { name: 'sku_name', type: 'VARCHAR(255)', nullable: false, description: 'Visual product display name' },
        { name: 'category', type: 'VARCHAR(100)', nullable: false, description: 'L1 catalog grouping' },
        { name: 'price', type: 'DECIMAL(8,2)', nullable: false, description: 'MSRP price point' },
      ],
    },
    {
      id: 'ds-4',
      name: 'iot_sensor_stream',
      format: 'Parquet',
      size: '2.4 GB',
      source: 'MQTT Broker',
      rowCount: 24500000,
      uploadedAt: '2026-07-02 03:00',
      status: 'Raw',
      owner: 'IoT Engineering',
      columns: [
        { name: 'sensor_id', type: 'VARCHAR(30)', nullable: false, description: 'Hardware unique address' },
        { name: 'metric_name', type: 'VARCHAR(50)', nullable: false, description: 'Telemetry variable metric name' },
        { name: 'reading_value', type: 'DOUBLE', nullable: false, description: 'Floating numerical reading' },
        { name: 'timestamp', type: 'TIMESTAMP', nullable: false, description: 'Capture timestamp' },
      ],
    },
  ]);

  // Ingestion Jobs Tracker
  const [ingestionJobs, setIngestionJobs] = useState<IngestionJob[]>([
    { id: 'ing-101', datasetName: 'customer_profiles', status: 'SUCCESS', progress: 100, recordsIngested: 125400, duration: '4.2s', timestamp: '2026-07-01 10:15' },
    { id: 'ing-102', datasetName: 'retail_transactions', status: 'SUCCESS', progress: 100, recordsIngested: 1482000, duration: '18.7s', timestamp: '2026-07-01 11:32' },
    { id: 'ing-103', datasetName: 'product_catalog', status: 'SUCCESS', progress: 100, recordsIngested: 12500, duration: '1.1s', timestamp: '2026-07-02 01:23' },
    { id: 'ing-104', datasetName: 'iot_sensor_stream', status: 'QUEUED', progress: 0, recordsIngested: 0, duration: '0s', timestamp: '2026-07-02 03:00' },
  ]);

  // Spark Jobs Tracker
  const [sparkJobs, setSparkJobs] = useState<SparkJob[]>([
    { id: 'sp-201', name: 'customer_profiles_silver_transform', type: 'Batch', status: 'COMPLETED', progress: 100, cores: 8, memory: '32 GB', duration: '1m 12s', startedAt: '2026-07-01 10:20' },
    { id: 'sp-202', name: 'retail_transactions_dedup_enrich', type: 'Batch', status: 'COMPLETED', progress: 100, cores: 16, memory: '64 GB', duration: '2m 45s', startedAt: '2026-07-01 11:45' },
    { id: 'sp-203', name: 'product_catalog_format_normalization', type: 'Batch', status: 'COMPLETED', progress: 100, cores: 4, memory: '16 GB', duration: '35s', startedAt: '2026-07-02 01:30' },
    { id: 'sp-204', name: 'iot_sensor_aggregation_stream', type: 'Streaming', status: 'RUNNING', progress: 85, cores: 24, memory: '96 GB', duration: 'Continuous', startedAt: '2026-07-02 03:05' },
  ]);

  // Delta Lake Tables
  const [deltaTables, setDeltaTables] = useState<DeltaTable[]>([
    {
      id: 'customer_master',
      name: 'customer_master',
      location: 's3a://delta-lake/curated/customer_master',
      version: 2,
      lastUpdated: '2026-07-01 10:30',
      history: [
        { version: 2, timestamp: '2026-07-01 10:30', operation: 'MERGE', userName: 'SparkJobRunner', summary: 'Upserted customer demographics updates from Salesforce CRM incremental feed.' },
        { version: 1, timestamp: '2026-07-01 10:22', operation: 'UPDATE', userName: 'SparkJobRunner', summary: 'Anonymized email addresses and standardized country codes.' },
        { version: 0, timestamp: '2026-07-01 10:20', operation: 'WRITE (CREATE)', userName: 'DataEngAdmin', summary: 'Initial table creation from processed customer profiles.' }
      ],
      schema: [
        { column: 'customer_id', type: 'string', partitionKey: true },
        { column: 'first_name', type: 'string', partitionKey: false },
        { column: 'last_name', type: 'string', partitionKey: false },
        { column: 'email', type: 'string', partitionKey: false },
        { column: 'country', type: 'string', partitionKey: false },
        { column: 'is_active', type: 'boolean', partitionKey: false },
        { column: 'last_login', type: 'timestamp', partitionKey: false }
      ]
    },
    {
      id: 'transaction_ledger',
      name: 'transaction_ledger',
      location: 's3a://delta-lake/curated/transaction_ledger',
      version: 1,
      lastUpdated: '2026-07-01 11:55',
      history: [
        { version: 1, timestamp: '2026-07-01 11:55', operation: 'OPTIMIZE', userName: 'DeltaLakeDaemon', summary: 'Compacted small Parquet files via Z-Order layout optimization.' },
        { version: 0, timestamp: '2026-07-01 11:45', operation: 'WRITE (CREATE)', userName: 'SparkJobRunner', summary: 'Parsed raw JSON telemetry, validated schema, and initialized transactions partition.' }
      ],
      schema: [
        { column: 'transaction_id', type: 'string', partitionKey: true },
        { column: 'customer_id', type: 'string', partitionKey: false },
        { column: 'store_id', type: 'integer', partitionKey: false },
        { column: 'amount', type: 'double', partitionKey: false },
        { column: 'timestamp', type: 'timestamp', partitionKey: false },
        { column: 'partition_date', type: 'date', partitionKey: true }
      ]
    }
  ]);

  // Data Quality Rules
  const [qualityRules, setQualityRules] = useState<QualityRule[]>([
    { id: 'dq-1', tableName: 'customer_master', ruleName: 'customer_id_not_null', type: 'Null Check', status: 'PASSED', targetColumn: 'customer_id', checkedRecords: 125400, failedRecords: 0 },
    { id: 'dq-2', tableName: 'customer_master', ruleName: 'email_format_valid', type: 'Custom', status: 'PASSED', targetColumn: 'email', checkedRecords: 125400, failedRecords: 0 },
    { id: 'dq-3', tableName: 'customer_master', ruleName: 'country_not_null_warning', type: 'Null Check', status: 'WARNING', targetColumn: 'country', checkedRecords: 125400, failedRecords: 231, errorMessage: '231 customer records have empty/null country codes. Tolerable threshold is 1%.' },
    { id: 'dq-4', tableName: 'transaction_ledger', ruleName: 'amount_positive', type: 'Range Validation', status: 'PASSED', targetColumn: 'amount', checkedRecords: 1482000, failedRecords: 0 },
    { id: 'dq-5', tableName: 'transaction_ledger', ruleName: 'transaction_id_unique', type: 'Uniqueness', status: 'PASSED', targetColumn: 'transaction_id', checkedRecords: 1482000, failedRecords: 0 }
  ]);

  // Syncing with Tailwind Dark Mode
  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  // 1. Ingestion / Data Source Upload Simulated Function
  const addDataset = (name: string, format: 'CSV' | 'JSON' | 'Parquet', size: string, source: string) => {
    const formattedName = name.trim().toLowerCase().replace(/[^a-z0-9_]/g, '_');
    const newId = `ds-${Date.now()}`;
    const newDataset: Dataset = {
      id: newId,
      name: formattedName,
      format,
      size,
      source,
      rowCount: Math.floor(Math.random() * 500000) + 10000,
      uploadedAt: new Date().toISOString().replace('T', ' ').slice(0, 16),
      status: 'Raw',
      owner: 'Adhoc Upload',
      columns: [
        { name: 'id', type: 'BIGINT', nullable: false, description: 'Generated primary key ID' },
        { name: 'metric_value', type: 'DOUBLE', nullable: true, description: 'Analyzed metric value' },
        { name: 'status', type: 'VARCHAR(20)', nullable: false, description: 'Processing status label' },
        { name: 'updated_at', type: 'TIMESTAMP', nullable: false, description: 'Last edit timestamp' },
      ],
    };

    setDatasets((prev) => [newDataset, ...prev]);

    // Create a matching Queued Ingestion Job
    const newIngJob: IngestionJob = {
      id: `ing-${Math.floor(Math.random() * 900) + 100}`,
      datasetName: formattedName,
      status: 'QUEUED',
      progress: 0,
      recordsIngested: 0,
      duration: '0s',
      timestamp: new Date().toISOString().replace('T', ' ').slice(0, 16),
    };
    setIngestionJobs((prev) => [newIngJob, ...prev]);
  };

  // 2. Run Ingestion Pipeline Action
  const runIngestion = async (id: string) => {
    const targetDataset = datasets.find((d) => d.id === id);
    if (!targetDataset) return;

    // Update dataset status to "Ingesting"
    setDatasets((prev) =>
      prev.map((d) => (d.id === id ? { ...d, status: 'Ingesting' } : d))
    );

    // Update job to RUNNING
    setIngestionJobs((prev) =>
      prev.map((j) =>
        j.datasetName === targetDataset.name ? { ...j, status: 'RUNNING', progress: 5 } : j
      )
    );

    // Simulate progress
    for (let progress = 10; progress <= 100; progress += 30) {
      await new Promise((r) => setTimeout(r, 400));
      const cappedProgress = Math.min(progress, 100);
      setIngestionJobs((prev) =>
        prev.map((j) =>
          j.datasetName === targetDataset.name
            ? {
                ...j,
                progress: cappedProgress,
                recordsIngested: Math.floor((targetDataset.rowCount * cappedProgress) / 100),
                duration: `${(Math.random() * 5 + 1).toFixed(1)}s`,
              }
            : j
        )
      );
    }

    // Mark completed
    setDatasets((prev) =>
      prev.map((d) => (d.id === id ? { ...d, status: 'Processed' } : d))
    );
    setIngestionJobs((prev) =>
      prev.map((j) =>
        j.datasetName === targetDataset.name
          ? { ...j, status: 'SUCCESS', progress: 100, recordsIngested: targetDataset.rowCount }
          : j
      )
    );

    // Add a corresponding Spark job dynamically
    const newSparkJob: SparkJob = {
      id: `sp-${Math.floor(Math.random() * 900) + 200}`,
      name: `${targetDataset.name}_silver_transform`,
      type: 'Batch',
      status: 'PENDING',
      progress: 0,
      cores: 8,
      memory: '32 GB',
      duration: '0s',
      startedAt: new Date().toISOString().replace('T', ' ').slice(0, 16),
    };
    setSparkJobs((prev) => [newSparkJob, ...prev]);
  };

  // 3. Run Spark Job Action
  const runSparkProcessing = async (jobId: string) => {
    const targetJob = sparkJobs.find((j) => j.id === jobId);
    if (!targetJob) return;

    setSparkJobs((prev) =>
      prev.map((j) => (j.id === jobId ? { ...j, status: 'RUNNING', progress: 10 } : j))
    );

    // Simulate multi-stage Spark job
    for (let p = 20; p <= 100; p += 20) {
      await new Promise((r) => setTimeout(r, 600));
      setSparkJobs((prev) =>
        prev.map((j) => (j.id === jobId ? { ...j, progress: p, duration: `${Math.floor(p / 2)}s` } : j))
      );
    }

    // Set complete
    setSparkJobs((prev) =>
      prev.map((j) => (j.id === jobId ? { ...j, status: 'COMPLETED', duration: '48s' } : j))
    );

    // Generate Delta Table from this job!
    const baseName = targetJob.name.replace('_silver_transform', '');
    const cleanTableName = baseName.replace(/[^a-z0-9_]/g, '_');

    // Add Delta table
    const exists = deltaTables.some((t) => t.id === cleanTableName);
    if (!exists) {
      const newDeltaTable: DeltaTable = {
        id: cleanTableName,
        name: cleanTableName,
        location: `s3a://delta-lake/curated/${cleanTableName}`,
        version: 0,
        lastUpdated: new Date().toISOString().replace('T', ' ').slice(0, 16),
        history: [
          {
            version: 0,
            timestamp: new Date().toISOString().replace('T', ' ').slice(0, 16),
            operation: 'WRITE (CREATE)',
            userName: 'SparkJobRunner',
            summary: `Created schema-optimized Silver Delta Table from ${baseName} dataset source.`,
          },
        ],
        schema: [
          { column: 'id', type: 'long', partitionKey: true },
          { column: 'metric_value', type: 'double', partitionKey: false },
          { column: 'status', type: 'string', partitionKey: false },
          { column: 'updated_at', type: 'timestamp', partitionKey: false },
        ],
      };

      setDeltaTables((prev) => [newDeltaTable, ...prev]);

      // Add Data Quality Rules for this table
      const rules: QualityRule[] = [
        {
          id: `dq-${Date.now()}-1`,
          tableName: cleanTableName,
          ruleName: `${cleanTableName}_id_not_null`,
          type: 'Null Check',
          status: 'PASSED',
          targetColumn: 'id',
          checkedRecords: 50000,
          failedRecords: 0,
        },
        {
          id: `dq-${Date.now()}-2`,
          tableName: cleanTableName,
          ruleName: `${cleanTableName}_status_valid`,
          type: 'Type Match',
          status: 'PASSED',
          targetColumn: 'status',
          checkedRecords: 50000,
          failedRecords: 0,
        },
      ];
      setQualityRules((prev) => [...prev, ...rules]);
      setSelectedTableId(cleanTableName);
    }

    // Update original dataset status to "Curated"
    setDatasets((prev) =>
      prev.map((d) => (d.name === baseName ? { ...d, status: 'Curated' } : d))
    );
  };

  // 4. Update Quality Rule
  const updateQualityRule = (ruleId: string, status: 'PASSED' | 'FAILED' | 'WARNING') => {
    setQualityRules((prev) =>
      prev.map((r) =>
        r.id === ruleId
          ? {
              ...r,
              status,
              failedRecords: status === 'FAILED' ? Math.floor(Math.random() * 500) + 10 : 0,
              errorMessage: status === 'FAILED' ? 'Violated integrity constraints.' : undefined,
            }
          : r
      )
    );
  };

  return (
    <PlatformContext.Provider
      value={{
        theme,
        toggleTheme,
        activePage,
        setActivePage,
        datasets,
        ingestionJobs,
        sparkJobs,
        deltaTables,
        qualityRules,
        addDataset,
        runIngestion,
        runSparkProcessing,
        updateQualityRule,
        searchQuery,
        setSearchQuery,
        selectedTableId,
        setSelectedTableId,
        sidebarOpen,
        setSidebarOpen,
      }}
    >
      {children}
    </PlatformContext.Provider>
  );
};

export const usePlatform = () => {
  const context = useContext(PlatformContext);
  if (!context) {
    throw new Error('usePlatform must be used within a PlatformProvider');
  }
  return context;
};
