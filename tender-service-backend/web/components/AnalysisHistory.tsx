import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { History, Clock, FileCheck, AlertTriangle, ArrowLeft, Search, Filter } from 'lucide-react';

// Mock History Data (Moved from AiAssistant)
const MOCK_HISTORY = [
  {
    id: 'h1',
    projectName: '2024年海淀区智慧校园二期建设项目',
    date: '2小时前',
    score: 88,
    riskLevel: 'low',
    riskTag: '资金充足',
    status: '已生成策略'
  },
  {
    id: 'h2',
    projectName: '通州区市政道路养护服务采购项目',
    date: '昨天 14:30',
    score: 65,
    riskLevel: 'high',
    riskTag: '回款周期长',
    status: '建议放弃'
  },
  {
    id: 'h3',
    projectName: '朝阳区老旧小区外立面改造工程',
    date: '3天前',
    score: 72,
    riskLevel: 'medium',
    riskTag: '工期紧张',
    status: '需联合体'
  },
  {
    id: 'h4',
    projectName: '北京市轨道交通13号线扩能提升工程',
    date: '5天前',
    score: 92,
    riskLevel: 'low',
    riskTag: '重点项目',
    status: '已生成标书'
  },
  {
    id: 'h5',
    projectName: '某部委机关办公楼修缮工程',
    date: '1周前',
    score: 58,
    riskLevel: 'high',
    riskTag: '资质不符',
    status: '建议放弃'
  }
];

const AnalysisHistory: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 60) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-red-600 bg-red-50 border-red-200';
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
                 {MOCK_HISTORY.map((item) => (
                   <tr key={item.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-5 font-medium text-slate-900">{item.projectName}</td>
                      <td className="px-6 py-5 text-slate-500 flex items-center gap-2">
                         <Clock className="h-4 w-4" /> {item.date}
                      </td>
                      <td className="px-6 py-5">
                         <span className={`px-2.5 py-1 rounded-md font-bold text-sm border ${getScoreColor(item.score)}`}>
                           {item.score}
                         </span>
                      </td>
                      <td className="px-6 py-5">
                         <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200">
                           {item.riskTag}
                         </span>
                      </td>
                      <td className="px-6 py-5">
                         <span className={`inline-flex items-center gap-1.5 text-sm font-medium ${item.riskLevel === 'low' ? 'text-emerald-600' : item.riskLevel === 'medium' ? 'text-indigo-600' : 'text-slate-500'}`}>
                           {item.status === '建议放弃' ? <AlertTriangle className="h-4 w-4" /> : <FileCheck className="h-4 w-4" />}
                           {item.status}
                         </span>
                      </td>
                      <td className="px-6 py-5 text-right">
                         <Button variant="ghost" size="sm" className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50">
                           查看报告
                         </Button>
                      </td>
                   </tr>
                 ))}
               </tbody>
             </table>
           </div>
           <div className="p-4 border-t border-slate-100 bg-slate-50/30 text-center">
              <span className="text-sm text-slate-400">已显示全部 5 条记录</span>
           </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalysisHistory;