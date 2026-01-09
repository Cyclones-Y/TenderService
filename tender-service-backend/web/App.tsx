import React, { useEffect, useState } from 'react';
import { LayoutDashboard, List, FileText, Settings as SettingsIcon, Bell, Menu, X, LogOut, PieChart } from 'lucide-react';
import Dashboard from './components/Dashboard';
import TenderList from './components/TenderList';
import TenderDetail from './components/TenderDetail';
import Settings from './components/Settings';
import Subscription from './components/Subscription';
import { ViewState } from './types';
import { Button } from './components/ui/Button';

import { getApiUrl } from './utils/api';

type TrendStat = { date: string; count: number };

type DashboardData = {
  lastSyncMinutesAgo: number;
  trendStats: TrendStat[];
};

type DataResponse<T> = {
  code: number;
  msg: string;
  success: boolean;
  time: string;
  data?: T;
};

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewState>('dashboard');
  const [selectedTenderId, setSelectedTenderId] = useState<string | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [lastSyncText, setLastSyncText] = useState<string>('上次同步: 未知');
  const [dashboardWelcomeText, setDashboardWelcomeText] = useState<string>('欢迎回来。');

  useEffect(() => {
    const fetchLastSync = async () => {
      try {
        const res = await fetch(getApiUrl('/tenders/dashboard'));
        const json = (await res.json()) as DataResponse<DashboardData>;
        const minutes = json?.data?.lastSyncMinutesAgo;
        if (typeof minutes === 'number' && Number.isFinite(minutes)) {
          setLastSyncText(`上次同步: ${Math.max(0, Math.floor(minutes))} 分钟前`);
        } else {
          setLastSyncText('上次同步: 未知');
        }

        const trendStats = json?.data?.trendStats;
        const todayNew = Array.isArray(trendStats) ? trendStats.at(-1)?.count : undefined;
        if (typeof todayNew === 'number' && Number.isFinite(todayNew)) {
          setDashboardWelcomeText(`欢迎回来，今日已更新 ${Math.max(0, Math.floor(todayNew))} 条新招标信息。`);
        } else {
          setDashboardWelcomeText('欢迎回来。');
        }
      } catch {
        setLastSyncText('上次同步: 未知');
        setDashboardWelcomeText('欢迎回来。');
      }
    };
    void fetchLastSync();
  }, []);

  const handleViewDetail = (id: string) => {
    setSelectedTenderId(id);
    setCurrentView('detail');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleBackToList = () => {
    setSelectedTenderId(null);
    setCurrentView('list');
  };

  const handleNavClick = (view: ViewState) => {
    setCurrentView(view);
    setIsMobileMenuOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const NavItem = ({ view, label, icon: Icon }: { view: ViewState; label: string; icon: any }) => (
    <button
      onClick={() => handleNavClick(view)}
      className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-base font-medium transition-colors ${
        currentView === view || (view === 'list' && currentView === 'detail')
          ? 'bg-indigo-50 text-indigo-600'
          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
      }`}
    >
      <Icon className={`h-5 w-5 ${currentView === view ? 'text-indigo-600' : 'text-slate-500'}`} />
      {label}
    </button>
  );

  const getPageTitle = () => {
    switch (currentView) {
      case 'dashboard': return '仪表盘';
      case 'list': return '招标项目库';
      case 'detail': return '项目详情';
      case 'settings': return '偏好设置';
      case 'subscription': return '订阅管理';
      default: return 'TenderSight';
    }
  };

  const getPageDescription = () => {
     switch (currentView) {
      case 'dashboard': return dashboardWelcomeText;
      case 'list': return '浏览并管理所有招标项目信息。';
      case 'detail': return '查看招标项目的详细业务与资金数据。';
      case 'settings': return '管理系统显示偏好与编号规则。';
      case 'subscription': return '配置您的招标信息监控关键词与通知规则。';
      default: return '';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row font-sans">
      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between p-4 bg-white border-b border-slate-200 sticky top-0 z-20">
        <div className="flex items-center gap-2 font-bold text-xl text-slate-900">
           <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white">
             <PieChart size={18} />
           </div>
           <span>TenderSight</span>
        </div>
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-slate-600">
          {isMobileMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-10 w-72 bg-white border-r border-slate-200 transform transition-transform duration-200 ease-in-out
        md:relative md:translate-x-0
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex h-full flex-col">
          <div className="flex h-20 items-center border-b border-slate-200 px-6">
             <div className="flex items-center gap-3 font-bold text-2xl text-slate-900">
                <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center text-white">
                  <PieChart size={20} />
                </div>
                <span>招标信息统计</span>
             </div>
          </div>
          <div className="flex-1 overflow-y-auto py-6 px-4">
            <nav className="space-y-2">
              <NavItem view="dashboard" label="数据概览" icon={LayoutDashboard} />
              <NavItem view="list" label="招标信息" icon={List} />
            </nav>

            <div className="mt-10">
              <h3 className="mb-3 px-4 text-xs font-bold uppercase tracking-wider text-slate-400">
                系统管理
              </h3>
              <nav className="space-y-2">
                <NavItem view="settings" label="偏好设置" icon={SettingsIcon} />
                <NavItem view="subscription" label="订阅管理" icon={Bell} />
              </nav>
            </div>
          </div>
          <div className="border-t border-slate-200 p-6">
             <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 border border-slate-100 mb-4">
                <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-sm">
                  JS
                </div>
                <div className="flex-1 overflow-hidden">
                  <p className="truncate text-base font-medium text-slate-900">Jason Smith</p>
                  <p className="truncate text-sm text-slate-500">AI开发部</p>
                </div>
             </div>
             <button className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-base font-medium text-slate-700 hover:bg-slate-50 transition-colors">
                <LogOut className="h-5 w-5" />
                退出登录
             </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-x-hidden md:h-screen md:overflow-y-auto">
        <header className="sticky top-0 z-10 bg-white/90 backdrop-blur-md border-b border-slate-200 px-8 py-5 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              {getPageTitle()}
            </h1>
            <p className="text-base text-slate-500 mt-1">
               {getPageDescription()}
            </p>
          </div>
          <div className="flex items-center gap-4">
             <span className="text-sm text-slate-500 hidden sm:block">{lastSyncText}</span>
             <Button size="md" variant="ghost" className="relative" onClick={() => handleNavClick('subscription')}>
                <Bell className="h-6 w-6 text-slate-600" />
                <span className="absolute top-2 right-3 h-2.5 w-2.5 rounded-full bg-red-500 border border-white"></span>
             </Button>
          </div>
        </header>

        {/* Updated Container Width */}
        <div className="p-6 md:p-10 max-w-[1920px] mx-auto">
          {currentView === 'dashboard' && <Dashboard />}
          {currentView === 'list' && <TenderList onViewDetail={handleViewDetail} />}
          {currentView === 'detail' && selectedTenderId && (
            <TenderDetail id={selectedTenderId} onBack={handleBackToList} />
          )}
          {currentView === 'settings' && <Settings />}
          {currentView === 'subscription' && <Subscription />}
        </div>
      </main>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 z-0 bg-black/20 backdrop-blur-sm md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
    </div>
  );
};

export default App;
