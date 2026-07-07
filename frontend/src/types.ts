export type PageId =
  | 'dashboard'
  | 'sources'
  | 'ingestion'
  | 'lake'
  | 'spark'
  | 'delta'
  | 'quality'
  | 'metadata'
  | 'ai-ready'
  | 'architecture'
  | 'settings';

export interface Dataset {
  id: string;
  name: string;
  format: 'CSV' | 'JSON' | 'Parquet' | 'Delta';
  size: string;
  source: string;
  rowCount: number;
  uploadedAt: string;
  status: 'Raw' | 'Ingesting' | 'Processed' | 'Curated' | 'Failed';
  owner: string;
  columns: { name: string; type: string; nullable: boolean; description: string }[];
}

export interface IngestionJob {
  id: string;
  datasetName: string;
  status: 'SUCCESS' | 'RUNNING' | 'FAILED' | 'QUEUED';
  progress: number;
  recordsIngested: number;
  duration: string;
  timestamp: string;
}

export interface SparkJob {
  id: string;
  name: string;
  type: 'Batch' | 'Streaming';
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  progress: number;
  cores: number;
  memory: string;
  duration: string;
  startedAt: string;
}

export interface DeltaTable {
  id: string;
  name: string;
  location: string;
  version: number;
  lastUpdated: string;
  history: {
    version: number;
    timestamp: string;
    operation: string;
    userName: string;
    summary: string;
  }[];
  schema: {
    column: string;
    type: string;
    partitionKey: boolean;
  }[];
}

export interface QualityRule {
  id: string;
  tableName: string;
  ruleName: string;
  type: 'Null Check' | 'Type Match' | 'Range Validation' | 'Uniqueness' | 'Custom';
  status: 'PASSED' | 'FAILED' | 'WARNING';
  targetColumn: string;
  checkedRecords: number;
  failedRecords: number;
  errorMessage?: string;
}

export interface LineageNode {
  id: string;
  label: string;
  type: 'source' | 'ingestion' | 'lake' | 'spark' | 'delta' | 'consumer';
  status: 'active' | 'pending' | 'completed';
}

export interface LineageEdge {
  from: string;
  to: string;
}
