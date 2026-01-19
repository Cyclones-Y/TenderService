import React, { useEffect, useState } from 'react';
import { Card, CardContent } from './ui/Card';
import { Button } from './ui/Button';
import { Clock, FileCheck, AlertTriangle, ArrowLeft, Search, Filter } from 'lucide-react';
import { getApiUrl } from '../utils/api';

type HistoryItem = {
  analysisId: number;
  tenderId: number;
  projectName: string;
  analysisTime: string;
  score: number;
  riskTag: string;
  decisionConclusion: string;
};

type HistoryResponse = {
  code: number;
  msg: string;
  success: boolean;
  data: HistoryItem[];
};

const AnalysisHistory: React.FC<{ onBack: () => void; onViewReport: (tenderId: number) => void }> = ({ onBack, onViewReport }) => {
  const [rows, setRows] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorText, setErrorText] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      setErrorText(null);
      try {
        const res = await fetch(getApiUrl('/tenders/ai-analysis/history?limit=50'));
        const data: HistoryResponse = await res.json();
        if (!data.success) {
          throw new Error(data.msg);
        }
        setRows(data.data || []);
      } catch (error) {
        setRows([]);
        setErrorText('加载分析历史失败');
      } finally {
        setLoading(false);
      }
    };
    void fetchHistory();
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 60) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const formatRelativeTime = (value: string) => {
    if (!value) return '—';
    const normalized = value.replace(' ', 'T');
    const date = new Date(normalized);
    if (Number.isNaN(date.getTime())) return value;
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);
    if (diffMinutes < 60) return `${Math.max(diffMinutes, 1)}分钟前`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}小时前`;
    const diffDays = Math.floor(diffHours / 24);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    if (diffDays === 1) return `昨天 ${hours}:${minutes}`;
    if (diffDays < 7) return `${diffDays}天前`;
    const diffWeeks = Math.floor(diffDays / 7);
    return `${diffWeeks}周前`;
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-[1920px] mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={onBack}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">分析历史记录</h2>
            <p className="text-sm text-slate-500">查看过往生成的 AI 分析报告与策略建议</p>
          </div>
        </div>
        <div className="flex gap-3">
            <Button variant="outline"><Filter className="mr-2 h-4 w-4"/> 筛选</Button>
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input className="pl-9 h-10 rounded-lg border border-slate-200 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="搜索历史记录..." />
            </div>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
           <div className="overflow-x-auto">
             <table className="w-full text-left">
               <thead className="text-sm font-semibold text-slate-500 bg-slate-50/50 border-b border-slate-200">
                 <tr>
                    <th className="px-6 py-4">项目名称</th>
                    <th className="px-6 py-4">分析时间</th>
                    <th className="px-6 py-4">AI 推荐分</th>
                    <th className="px-6 py-4">核心风险标签</th>
                    <th className="px-6 py-4">决策建议</th>
                    <th className="px-6 py-4 text-right">操作</th>
                 </tr>
               </thead>
               <tbody className="divide-y divide-slate-100 text-base">
                 {loading && (
                   <tr>
                     <td className="px-6 py-5 text-slate-500" colSpan={6}>加载中...</td>
                   </tr>
                 )}
                 {!loading && errorText && (
                   <tr>
                     <td className="px-6 py-5 text-red-600" colSpan={6}>{errorText}</td>
                   </tr>
                 )}
                 {!loading && !errorText && rows.map((item) => (
                   <tr key={item.analysisId} className="hover:bg-slate-50/50 transition-colors">
                     <td className="px-6 py-5 font-medium text-slate-900">{item.projectName}</td>
                     <td className="px-6 py-5 text-slate-500 flex items-center gap-2">
                        <Clock className="h-4 w-4" /> {formatRelativeTime(item.analysisTime)}
                      </td>
                      <td className="px-6 py-5">
                         <span className={`px-2.5 py-1 rounded-md font-bold text-sm border ${getScoreColor(item.score)}`}>
                           {item.score}
                         </span>
                      </td>
                      <td className="px-6 py-5">
                        <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200 max-w-[140px] truncate" title={item.riskTag}>
                          {item.riskTag || '—'}
                         </span>
                      </td>
                      <td className="px-6 py-5">
                        <span className={`inline-flex items-center gap-1.5 text-sm font-medium ${item.score >= 80 ? 'text-emerald-600' : item.score >= 60 ? 'text-indigo-600' : 'text-slate-500'}`}>
                          {item.score < 60 ? <AlertTriangle className="h-4 w-4" /> : <FileCheck className="h-4 w-4" />}
                          {item.decisionConclusion || '—'}
                         </span>
                      </td>
                      <td className="px-6 py-5 text-right">
                        <Button variant="ghost" size="sm" className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50" onClick={() => onViewReport(item.tenderId)}>
                           查看报告
                         </Button>
                      </td>
                   </tr>
                 ))}
               </tbody>
             </table>
           </div>
           <div className="p-4 border-t border-slate-100 bg-slate-50/30 text-center">
             <span className="text-sm text-slate-400">已显示全部 {rows.length} 条记录</span>
           </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalysisHistory;
