import React from 'react';
import { motion } from 'motion/react';
import { 
  ArrowUpRight, 
  ArrowDownRight, 
  Info, 
  ShieldCheck, 
  Terminal, 
  HelpCircle,
  Target,
  AlertTriangle,
  Cloud,
  Briefcase,
  Lightbulb,
  CheckCircle
} from 'lucide-react';

// PAGE HEADER (Premium typography: clean, spacious, modern hierarchy)
export interface PageHeaderProps {
  id: string;
  title: string;
  description: string;
  actions?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ id, title, description, actions }) => {
  return (
    <div id={`${id}-header`} className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-slate-200 dark:border-slate-850 mb-8 gap-4">
      <div className="space-y-1.5">
        <h1 id={`${id}-title`} className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-white font-sans">
          {title}
        </h1>
        <p id={`${id}-desc`} className="text-xs md:text-sm text-slate-500 dark:text-slate-400 font-sans max-w-3xl leading-relaxed">
          {description}
        </p>
      </div>
      {actions && (
        <div id={`${id}-actions`} className="flex flex-wrap items-center gap-2.5">
          {actions}
        </div>
      )}
    </div>
  );
};

// PREMIUM CARD WITH HOVER LIFT (Linear/Vercel inspired, soft shadows, sharp borders)
interface CardProps {
  id: string;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ id, children, className = '', onClick }) => {
  return (
    <div
      id={id}
      onClick={onClick}
      className={`bg-card text-card-foreground border border-border rounded-xl p-6 shadow-[0_1px_3px_rgba(0,0,0,0.02),0_1px_2px_rgba(0,0,0,0.04)] transition-all duration-200 ${
        onClick 
          ? 'cursor-pointer hover:shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:hover:bg-card/60 hover:scale-[1.005] hover:border-border/85 active:scale-[0.995]' 
          : 'hover:shadow-[0_4px_20px_rgba(0,0,0,0.02)] hover:border-border/80'
      } ${className}`}
    >
      {children}
    </div>
  );
};

// KPI/STAT CARD OVERHAUL (Premium alignment, spacing, typography)
interface StatCardProps {
  id: string;
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({ 
  id, 
  title, 
  value, 
  subtitle, 
  trend, 
  icon, 
  className = '',
  onClick
}) => {
  return (
    <Card id={id} onClick={onClick} className={`relative overflow-hidden group ${className}`}>
      <div className="flex justify-between items-start">
        <div className="space-y-1.5">
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 font-sans">
            {title}
          </p>
          <h3 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-white font-sans">
            {value}
          </h3>
        </div>
        {icon && (
          <div className="p-2 bg-slate-50 dark:bg-slate-800/60 rounded-lg text-slate-400 dark:text-slate-500 border border-slate-200/50 dark:border-slate-800 group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors duration-150 flex items-center justify-center">
            {icon}
          </div>
        )}
      </div>

      <div className="flex items-center gap-2 mt-4 text-xs">
        {trend && (
          <span
            className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold font-sans ${
              trend.isPositive 
                ? 'bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-450 border border-emerald-100 dark:border-emerald-900/30' 
                : 'bg-rose-50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-450 border border-rose-100 dark:border-rose-900/30'
            }`}
          >
            {trend.isPositive ? <ArrowUpRight className="w-3 h-3 mr-0.5" /> : <ArrowDownRight className="w-3 h-3 mr-0.5" />}
            {trend.value}
          </span>
        )}
        {subtitle && (
          <span className="text-slate-400 dark:text-slate-500 text-[10px] font-sans truncate">
            {subtitle}
          </span>
        )}
      </div>
    </Card>
  );
};

// PREMIUM BADGE (Soft tint color, distinct contrast borders)
interface BadgeProps {
  id: string;
  content: string;
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'neutral' | 'purple' | 'slate';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ id, content, variant = 'neutral', className = '' }) => {
  const styles = {
    primary: 'bg-blue-50 dark:bg-blue-950/30 text-blue-700 dark:text-blue-400 border border-blue-100 dark:border-blue-900/40',
    success: 'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/40',
    warning: 'bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400 border border-amber-100 dark:border-amber-900/40',
    danger: 'bg-rose-50 dark:bg-rose-950/30 text-rose-700 dark:text-rose-400 border border-rose-100 dark:border-rose-900/40',
    neutral: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700',
    purple: 'bg-indigo-50 dark:bg-indigo-950/30 text-indigo-700 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/40',
    slate: 'bg-slate-50 dark:bg-slate-900/40 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800',
  };

  return (
    <span
      id={id}
      className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold tracking-tight font-sans ${styles[variant]} ${className}`}
    >
      {content}
    </span>
  );
};

// PREMIUM ACTION BUTTON (Sleek, minimalist, consistent sizing, shadcn inspired)
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  id: string;
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost' | 'success';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  id,
  children,
  variant = 'primary',
  size = 'md',
  icon,
  className = '',
  ...props
}) => {
  const baseStyle = 'inline-flex items-center justify-center font-sans font-medium rounded-lg transition-all duration-150 cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-500 dark:bg-blue-600 dark:hover:bg-blue-500 text-white shadow-xs border border-blue-700/20 active:scale-[0.985]',
    secondary: 'bg-secondary hover:bg-secondary/80 text-secondary-foreground border border-border active:scale-[0.985]',
    outline: 'border border-border bg-card hover:bg-muted text-foreground',
    danger: 'bg-rose-600 hover:bg-rose-750 text-white border border-rose-700/20 active:scale-[0.985]',
    success: 'bg-emerald-600 hover:bg-emerald-750 text-white border border-emerald-700/20 active:scale-[0.985]',
    ghost: 'hover:bg-muted text-muted-foreground hover:text-foreground',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs gap-1.5',
    md: 'px-4 py-2 text-sm gap-2',
    lg: 'px-5 py-2.5 text-sm gap-2.5',
  };

  return (
    <button
      id={id}
      className={`${baseStyle} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {icon && <span className="flex-shrink-0 flex items-center justify-center">{icon}</span>}
      {children}
    </button>
  );
};

// COMPACT TABLE (No horizontal borders clutter, sleek, highly readable in both modes)
interface TableProps {
  id: string;
  headers: string[];
  children: React.ReactNode;
}

export const Table: React.FC<TableProps> = ({ id, headers, children }) => {
  return (
    <div id={`${id}-container`} className="overflow-x-auto border border-border rounded-xl bg-card shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
      <table id={id} className="min-w-full divide-y divide-border">
        <thead className="bg-muted/50">
          <tr>
            {headers.map((header, index) => (
              <th
                key={index}
                scope="col"
                className="px-5 py-3 text-left text-[10px] font-bold uppercase tracking-wider text-muted-foreground font-sans"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border bg-transparent">
          {children}
        </tbody>
      </table>
    </div>
  );
};

// PREMIUM PROGRESS BAR
interface ProgressBarProps {
  id: string;
  progress: number;
  className?: string;
  statusLabel?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ id, progress, className = '', statusLabel }) => {
  return (
    <div id={id} className={`w-full ${className}`}>
      {statusLabel && (
        <div className="flex justify-between items-center text-[10px] text-slate-400 dark:text-slate-500 mb-1.5 font-sans">
          <span>{statusLabel}</span>
          <span className="font-mono font-bold">{progress}%</span>
        </div>
      )}
      <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
        <motion.div
          className="bg-blue-600 dark:bg-blue-500 h-full rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
};

// POPUP DIALOG / MODAL
interface DialogProps {
  id: string;
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const Dialog: React.FC<DialogProps> = ({ id, isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div id={id} className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 dark:bg-slate-950/60 backdrop-blur-xs">
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.98 }}
        transition={{ duration: 0.15 }}
        className="bg-card text-card-foreground border border-border rounded-xl w-full max-w-lg overflow-hidden shadow-xl"
      >
        <div className="flex justify-between items-center px-6 py-4 border-b border-border">
          <h3 className="text-xs font-bold text-foreground uppercase tracking-wider font-sans">
            {title}
          </h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            ✕
          </button>
        </div>
        <div className="p-6">
          {children}
        </div>
      </motion.div>
    </div>
  );
};

// METADATA VALUE ROW (For modular summaries)
export const MetaRow: React.FC<{ label: string; value: React.ReactNode; font?: 'sans' | 'mono' }> = ({ label, value, font = 'sans' }) => {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-50 dark:border-slate-850/40 text-xs">
      <span className="text-slate-400 dark:text-slate-500 font-sans">{label}</span>
      <span className={`font-semibold text-slate-800 dark:text-slate-350 text-right ${font === 'mono' ? 'font-mono' : 'font-sans'}`}>
        {value}
      </span>
    </div>
  );
};

// REUSABLE ARCHITECTURE INSIGHT / EDUCATIONAL INFORMATION CARD
interface InsightCardProps {
  id: string;
  title: string;
  description?: string;
  purpose?: string;
  enterpriseProblem?: string;
  azureEquivalent?: string;
  enterpriseExample?: string;
  whyExists?: string;
  azureMapping?: {
    openSource: string;
    azureEquivalent: string;
    description: string;
  };
}

export const InsightCard: React.FC<InsightCardProps> = ({ 
  id, 
  title, 
  description, 
  purpose,
  enterpriseProblem,
  azureEquivalent,
  enterpriseExample,
  whyExists,
  azureMapping 
}) => {
  const hasStructuredData = purpose || enterpriseProblem || azureEquivalent || enterpriseExample || whyExists;

  return (
    <div id={id} className="bg-card text-card-foreground border border-border rounded-xl p-5 shadow-xs hover:shadow-md transition-all duration-200 space-y-4">
      <div className="flex gap-3 items-center">
        <div className="p-2 bg-blue-500/10 dark:bg-blue-400/10 text-blue-600 dark:text-blue-400 rounded-lg flex-shrink-0">
          <ShieldCheck className="w-4 h-4" />
        </div>
        <div>
          <h4 className="text-xs font-bold text-foreground uppercase tracking-wider font-sans">
            {title}
          </h4>
          {description && (
            <p className="text-[11px] text-muted-foreground mt-0.5 leading-relaxed">
              {description}
            </p>
          )}
        </div>
      </div>

      {hasStructuredData && (
        <div className="space-y-3.5 pt-3 border-t border-border">
          {purpose && (
            <div className="bg-muted/40 border border-border rounded-xl p-3.5 flex gap-3 items-start">
              <div className="p-1.5 bg-blue-500/10 dark:bg-blue-400/10 text-blue-600 dark:text-blue-400 rounded-lg flex-shrink-0">
                <Target className="w-3.5 h-3.5" />
              </div>
              <div className="space-y-0.5">
                <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">1. Purpose</span>
                <p className="text-xs text-foreground/95 leading-relaxed font-sans">{purpose}</p>
              </div>
            </div>
          )}

          {enterpriseProblem && (
            <div className="bg-amber-500/[0.03] dark:bg-amber-500/[0.015] border border-amber-200/50 dark:border-amber-900/30 rounded-xl p-3.5 flex gap-3 items-start">
              <div className="p-1.5 bg-amber-500/10 dark:bg-amber-400/10 text-amber-600 dark:text-amber-400 rounded-lg flex-shrink-0">
                <AlertTriangle className="w-3.5 h-3.5" />
              </div>
              <div className="space-y-0.5">
                <span className="text-[9px] font-bold text-amber-600/80 dark:text-amber-550 uppercase tracking-wider block">2. Enterprise Problem</span>
                <p className="text-xs text-foreground/95 leading-relaxed font-sans">{enterpriseProblem}</p>
              </div>
            </div>
          )}

          {azureEquivalent && (
            <div className="bg-sky-500/[0.04] dark:bg-sky-500/[0.02] border border-sky-200/50 dark:border-sky-900/30 rounded-xl p-3.5 flex gap-3 items-start">
              <div className="p-1.5 bg-sky-500/10 dark:bg-sky-400/10 text-sky-600 dark:text-sky-400 rounded-lg flex-shrink-0">
                <Cloud className="w-3.5 h-3.5" />
              </div>
              <div className="space-y-1">
                <span className="text-[9px] font-bold text-sky-600/80 dark:text-sky-400 uppercase tracking-wider block">3. Azure Equivalent</span>
                <div className="inline-block px-2 py-0.5 bg-sky-100 dark:bg-sky-950/50 text-sky-700 dark:text-sky-350 rounded font-bold text-[10px] font-sans border border-sky-200/30 dark:border-sky-900/30">
                  {azureEquivalent}
                </div>
              </div>
            </div>
          )}

          {enterpriseExample && (
            <div className="bg-purple-500/[0.03] dark:bg-purple-500/[0.015] border border-purple-200/40 dark:border-purple-900/25 rounded-xl p-3.5 flex gap-3 items-start">
              <div className="p-1.5 bg-purple-500/10 dark:bg-purple-400/10 text-purple-600 dark:text-purple-450 rounded-lg flex-shrink-0">
                <Briefcase className="w-3.5 h-3.5" />
              </div>
              <div className="space-y-0.5">
                <span className="text-[9px] font-bold text-purple-600/80 dark:text-purple-450 uppercase tracking-wider block">4. Enterprise Example</span>
                <p className="text-xs text-foreground/95 leading-relaxed font-sans">{enterpriseExample}</p>
              </div>
            </div>
          )}

          {whyExists && (
            <div className="bg-emerald-500/[0.03] dark:bg-emerald-500/[0.015] border border-emerald-200/40 dark:border-emerald-900/25 rounded-xl p-3.5 flex gap-3 items-start border-l-4 border-l-emerald-500 dark:border-l-emerald-500">
              <div className="p-1.5 bg-emerald-500/10 dark:bg-emerald-400/10 text-emerald-600 dark:text-emerald-400 rounded-lg flex-shrink-0">
                <Lightbulb className="w-3.5 h-3.5" />
              </div>
              <div className="space-y-0.5">
                <span className="text-[9px] font-bold text-emerald-600/80 dark:text-emerald-450 uppercase tracking-wider block">5. Key Takeaway</span>
                <p className="text-xs text-foreground/95 leading-relaxed font-sans italic">{whyExists}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {azureMapping && (
        <div className="space-y-3 pt-3 border-t border-border">
          <div className="bg-muted/40 border border-border rounded-xl p-3.5 space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider block">Sandbox Tech</span>
                <span className="font-mono text-[11px] text-foreground font-bold block bg-muted px-2 py-0.5 rounded border border-border">
                  {azureMapping.openSource}
                </span>
              </div>
              <div className="space-y-1">
                <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider block">Azure Equivalent</span>
                <span className="font-sans text-[11px] text-sky-600 dark:text-sky-400 font-bold block bg-sky-50 dark:bg-sky-950/50 px-2 py-0.5 rounded border border-sky-100 dark:border-sky-900/40">
                  {azureMapping.azureEquivalent}
                </span>
              </div>
            </div>
            <p className="text-[11px] text-muted-foreground leading-relaxed italic border-l-2 border-blue-500 pl-2.5 pt-0.5">
              {azureMapping.description}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
