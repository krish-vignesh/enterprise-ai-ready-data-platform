import React from 'react';
import { usePlatform } from '../context/PlatformContext';
import { PageId } from '../types';
import {
  LayoutDashboard,
  Database,
  Shuffle,
  Layers,
  Cpu,
  Triangle,
  ShieldCheck,
  Tags,
  BrainCircuit,
  Network,
  Settings,
  ChevronLeft,
  ChevronRight,
  DatabaseZap
} from 'lucide-react';

interface SidebarItem {
  id: PageId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  category: 'platform' | 'consumption' | 'architecture' | 'system';
}

export const Sidebar: React.FC = () => {
  const { activePage, setActivePage, sidebarOpen, setSidebarOpen } = usePlatform();

  const menuItems: SidebarItem[] = [
    // Data Platform Section
    { id: 'dashboard', label: 'Platform Overview', icon: LayoutDashboard, category: 'platform' },
    { id: 'sources', label: 'Data Sources', icon: Database, category: 'platform' },
    { id: 'ingestion', label: 'Data Ingestion', icon: Shuffle, category: 'platform' },
    { id: 'lake', label: 'Storage Zone (MinIO)', icon: Layers, category: 'platform' },
    { id: 'spark', label: 'Spark Processing', icon: Cpu, category: 'platform' },
    { id: 'delta', label: 'Delta Lake Logs', icon: Triangle, category: 'platform' },
    { id: 'quality', label: 'Data Quality (DQ)', icon: ShieldCheck, category: 'platform' },
    { id: 'metadata', label: 'Metadata & Lineage', icon: Tags, category: 'platform' },
    // Consumption Section
    { id: 'ai-ready', label: 'AI Ready Data Hub', icon: BrainCircuit, category: 'consumption' },
    // Architecture Section
    { id: 'architecture', label: 'Interactive Architecture', icon: Network, category: 'architecture' },
    // Platform Administration Section
    { id: 'settings', label: 'Platform Admin', icon: Settings, category: 'system' },
  ];

  const categories = [
    { key: 'platform', label: 'Data Platform' },
    { key: 'consumption', label: 'Consumption' },
    { key: 'architecture', label: 'Architecture' },
    { key: 'system', label: 'Platform' },
  ];

  return (
    <aside
      id="platform-sidebar"
      className={`fixed top-0 left-0 h-screen z-30 flex flex-col border-r bg-sidebar border-border transition-all duration-300 ${
        sidebarOpen ? 'w-64' : 'w-20'
      }`}
    >
      {/* Premium Floating Toggle Button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="absolute top-5 -right-3 w-6 h-6 rounded-full border border-border bg-sidebar text-muted-foreground hover:text-foreground shadow-sm flex items-center justify-center transition-all z-40 cursor-pointer hover:scale-110 active:scale-95"
        title={sidebarOpen ? "Collapse Navigation" : "Expand Navigation"}
      >
        {sidebarOpen ? <ChevronLeft className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
      </button>

      {/* Brand Header */}
      <div className={`flex items-center h-16 border-b border-border transition-all duration-300 ${
        sidebarOpen ? 'justify-between px-5' : 'justify-center px-0'
      }`}>
        <div className="flex items-center gap-2.5 overflow-hidden">
          <div className="p-1.5 bg-blue-600 rounded-lg text-white shadow-sm flex items-center justify-center transition-all hover:rotate-6">
            <DatabaseZap className="w-4 h-4 flex-shrink-0 animate-pulse" />
          </div>
          {sidebarOpen && (
            <div className="flex flex-col text-left transition-opacity duration-250 animate-fadeIn">
              <span className="font-sans font-bold text-xs tracking-tight text-slate-800 dark:text-slate-100 uppercase">
                Aether Sandbox
              </span>
              <span className="text-[9px] text-slate-400 dark:text-slate-500 font-bold tracking-wider uppercase">
                AI Ready Platform
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Navigation Group Section list */}
      <nav className={`flex-1 overflow-y-auto py-5 space-y-4 scrollbar-none transition-all duration-300 ${sidebarOpen ? 'px-3' : 'px-2'}`}>
        {categories.map((cat, catIdx) => {
          const items = menuItems.filter((item) => item.category === cat.key);
          if (items.length === 0) return null;

          return (
            <div key={cat.key} className="space-y-1">
              {sidebarOpen ? (
                <div className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider px-3 mb-1.5 font-sans animate-fadeIn">
                  {cat.label}
                </div>
              ) : (
                catIdx > 0 && <div className="h-px bg-border/60 my-3 mx-2" />
              )}
              <div className="space-y-0.5">
                {items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activePage === item.id;
                  return (
                    <button
                      key={item.id}
                      id={`sidebar-item-${item.id}`}
                      onClick={() => setActivePage(item.id)}
                      className={`flex items-center w-full rounded-lg text-left text-xs font-medium tracking-tight transition-all duration-150 group cursor-pointer relative ${
                        sidebarOpen 
                          ? 'gap-3 px-3 py-2' 
                          : 'justify-center py-2.5 px-0'
                      } ${
                        isActive
                          ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 font-semibold'
                          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                      }`}
                      title={!sidebarOpen ? item.label : undefined}
                    >
                      {isActive && !sidebarOpen && (
                        <div className="absolute left-0 top-1/4 bottom-1/4 w-1 bg-blue-600 dark:bg-blue-500 rounded-r" />
                      )}
                      {isActive && sidebarOpen && (
                        <div className="absolute left-0 top-1/4 bottom-1/4 w-0.5 bg-blue-600 dark:bg-blue-500 rounded-r" />
                      )}
                      <Icon className={`w-4 h-4 flex-shrink-0 transition-all duration-150 group-hover:scale-110 ${
                        isActive 
                          ? 'text-blue-600 dark:text-blue-400' 
                          : 'text-slate-400 dark:text-slate-500 group-hover:text-slate-700 dark:group-hover:text-slate-300'
                      }`} />
                      {sidebarOpen && (
                        <span className="font-sans whitespace-nowrap overflow-hidden text-ellipsis animate-fadeIn">
                          {item.label}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </nav>

      {/* Sidebar Footer detailing metadata */}
      <div className="p-4 border-t border-border bg-muted/35 transition-colors duration-200">
        {sidebarOpen ? (
          <div className="space-y-1.5 px-1 font-sans animate-fadeIn">
            <div className="flex items-center justify-between">
              <span className="text-[8px] font-bold uppercase tracking-wider text-muted-foreground">
                CORE STATUS
              </span>
              <span className="text-[8px] text-muted-foreground font-mono">
                v1.5.0-edge
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse flex-shrink-0" />
              <span className="text-[10px] font-medium text-muted-foreground truncate">
                Sandbox Instance Active
              </span>
            </div>
          </div>
        ) : (
          <div className="flex justify-center" title="Sandbox Active">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          </div>
        )}
      </div>
    </aside>
  );
};
