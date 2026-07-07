import React, { useState } from 'react';
import { usePlatform } from '../context/PlatformContext';
import { Sun, Moon, Search, Bell, HelpCircle, Menu, Cpu } from 'lucide-react';

export const TopNavbar: React.FC = () => {
  const { theme, toggleTheme, searchQuery, setSearchQuery, sidebarOpen, setSidebarOpen } = usePlatform();
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    { id: 1, text: 'Spark streaming job "iot_sensor_stream" committed 1.2M logs successfully.', time: '2 mins ago', type: 'info' },
    { id: 2, text: 'SLA deviation warning on customer_master: Unresolved country code Nulls.', time: '1 hour ago', type: 'warning' },
    { id: 3, text: 'Delta ACID Z-Order optimization complete on gold.transaction_ledger.', time: '3 hours ago', type: 'success' },
  ];

  return (
    <header
      id="platform-top-navbar"
      className="fixed top-0 right-0 h-16 z-20 flex items-center justify-between px-6 bg-background border-b border-border transition-all duration-200"
      style={{ left: sidebarOpen ? '16rem' : '5rem' }}
    >
      {/* Search Input block */}
      <div className="flex items-center gap-3 flex-1 max-w-md">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="md:hidden p-2 rounded-lg text-muted-foreground hover:bg-muted"
          title="Toggle Navigation"
        >
          <Menu className="w-4 h-4" />
        </button>
        <div className="relative w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            id="global-search-input"
            type="text"
            placeholder="Search tables, raw data feeds, Spark logs, quality tests..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 bg-muted border border-border rounded-lg text-xs text-foreground placeholder-muted-foreground focus:outline-none focus:ring-1 focus:ring-blue-500/35 focus:border-blue-500/50 transition-all duration-150"
          />
        </div>
      </div>

      {/* Utilities panel */}
      <div className="flex items-center gap-3">
        {/* Help Portal documentation */}
        <button
          id="help-portal-btn"
          title="Open API Reference & Framework Docs"
          className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors cursor-pointer"
        >
          <HelpCircle className="w-4.5 h-4.5" />
        </button>

        {/* Theme Toggle */}
        <button
          id="theme-toggle-btn"
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Toggle Light Theme' : 'Toggle Dark Theme'}
          className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors cursor-pointer"
        >
          {theme === 'dark' ? (
            <Sun className="w-4.5 h-4.5 text-amber-500" />
          ) : (
            <Moon className="w-4.5 h-4.5 text-indigo-500" />
          )}
        </button>

        {/* Alerts Center with status badge */}
        <div className="relative">
          <button
            id="notifications-dropdown-btn"
            onClick={() => setShowNotifications(!showNotifications)}
            className={`p-1.5 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors relative cursor-pointer ${
              showNotifications ? 'bg-muted text-foreground' : ''
            }`}
          >
            <Bell className="w-4.5 h-4.5" />
            <span className="absolute top-1 right-1 w-1.5 h-1.5 bg-rose-500 rounded-full" />
          </button>

          {showNotifications && (
            <>
              <div 
                className="fixed inset-0 z-40" 
                onClick={() => setShowNotifications(false)} 
              />
              <div className="absolute right-0 mt-2.5 w-80 bg-card border border-border rounded-xl shadow-lg overflow-hidden z-50 animate-fadeIn">
                <div className="px-4 py-3 border-b border-border flex justify-between items-center bg-muted/40">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                    Notifications Log
                  </span>
                  <span className="text-[9px] bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 px-1.5 py-0.5 rounded font-bold uppercase">
                    3 Warnings
                  </span>
                </div>
                <div className="divide-y divide-border max-h-64 overflow-y-auto">
                  {notifications.map((notif) => (
                    <div key={notif.id} className="p-3.5 hover:bg-muted/80 transition-colors">
                      <p className="text-xs text-foreground/90 leading-relaxed font-sans">
                        {notif.text}
                      </p>
                      <span className="text-[9px] text-muted-foreground mt-1 block font-mono">
                        {notif.time}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        <div className="h-5 w-px bg-border mx-1" />

        {/* Platform Identity */}
        <div className="flex items-center gap-2.5 pl-1.5 font-sans">
          <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-900/40 flex items-center justify-center shadow-xs">
            <Cpu className="w-4 h-4" />
          </div>
          <div className="hidden lg:flex flex-col text-left">
            <span className="text-xs font-semibold text-foreground/90 leading-none">
              Enterprise Sandbox
            </span>
            <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-wider mt-1">
              Data Platform
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
