/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { PlatformProvider, usePlatform } from './context/PlatformContext';
import { Sidebar } from './components/Sidebar';
import { TopNavbar } from './components/TopNavbar';

// Page Imports
import { Dashboard } from './pages/Dashboard';
import { DataSources } from './pages/DataSources';
import { DataIngestion } from './pages/DataIngestion';
import { DataLake } from './pages/DataLake';
import { SparkProcessing } from './pages/SparkProcessing';
import { DeltaLake } from './pages/DeltaLake';
import { DataQuality } from './pages/DataQuality';
import { Metadata } from './pages/Metadata';
import { AIReadyData } from './pages/AIReadyData';
import { Architecture } from './pages/Architecture';
import { Settings } from './pages/Settings';

function AppContent() {
  const { activePage, sidebarOpen } = usePlatform();

  const renderActivePage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard />;
      case 'sources':
        return <DataSources />;
      case 'ingestion':
        return <DataIngestion />;
      case 'lake':
        return <DataLake />;
      case 'spark':
        return <SparkProcessing />;
      case 'delta':
        return <DeltaLake />;
      case 'quality':
        return <DataQuality />;
      case 'metadata':
        return <Metadata />;
      case 'ai-ready':
        return <AIReadyData />;
      case 'architecture':
        return <Architecture />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div id="app-content-root" className="min-h-screen bg-[#F8FAFC] dark:bg-[#0F172A] text-slate-900 dark:text-slate-100 transition-colors duration-200">
      {/* Platform Navigation */}
      <Sidebar />
      <TopNavbar />

      {/* Primary Page Canvas */}
      <main
        id="app-main-canvas"
        className="pt-24 pb-16 pr-6 md:pr-8 transition-all duration-300 min-h-screen"
        style={{ paddingLeft: sidebarOpen ? '18rem' : '7rem' }}
      >
        {renderActivePage()}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <PlatformProvider>
      <AppContent />
    </PlatformProvider>
  );
}

