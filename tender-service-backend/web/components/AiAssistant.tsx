import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Select } from './ui/Input';
import { Sparkles, Brain, AlertTriangle, FileText, CheckCircle2, ChevronRight, Loader2, Target, BarChart4, History, Clock, FileCheck } from 'lucide-react';
import { MOCK_TENDERS } from '../constants';

// Mock Analysis Result Type
interface AnalysisResult {
  score: number;
  summary: string;
  risks: string[];
  requirements: { label: string; value: string; met: boolean }[];
  strategy: string;
}

// Mock History Data
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
  }
];

const AiAssistant: React.FC = () => {
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  // Filter only active tenders for analysis
  const activeTenders = MOCK_TENDERS.slice(0, 5);

  const handleAnalyze = () => {
    if (!selectedProject) return;
    setIsAnalyzing(true);
    setResult(null);

    // Simulate AI Processing
    setTimeout(() => {
      setResult({
        score: Math.floor(Math.random() * 20) + 75, // 75-95
        summary: "本项目为典型的政府采购工程类项目，资金来源已落实。核心难点在于工期较紧（180天），且包含复杂的地下管网改造。招标文件对过往类似业绩（近三年3个以上）有强制要求，技术评分中对‘绿色施工方案’赋予了较高权重（15分）。",
        risks: [
          "工期风险：180天工期包含雨季施工，建议制定详细的雨季施工专项方案。",
          "付款方式：进度款支付比例仅为60%，对企业垫资能力有一定要求。",
          "违约责任：延期违约金为合同总额的千分之五/天，高于行业平均水平。"
        ],
        requirements: [
          { label: "企业资质", value: "市政公用工程施工总承包二级及以上", met: true },
          { label: "项目经理", value: "市政专业一级注册建造师，且无在建项目", met: true },
          { label: "财务要求", value: "近三年均盈利，净资产不低于5000万", met: true },
          { label: "业绩要求", value: "近三年完成过单项合同额5000万以上的类似项目", met: false } // Demo unmet requirement
        ],
        strategy: "建议采取‘技术标高分突破+商务标合理低价’的策略。重点润色《绿色施工组织设计》章节，强调数字化管理平台在工期控制中的应用。针对业绩要求，需确认联合体投标的可行性或补充相关证明材料。"
      });
      setIsAnalyzing(false);
    }, 2000);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 60) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-[1920px] mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <Sparkles className="h-8 w-8 text-indigo-600" />
            AI 智能参谋
          </h2>
          <p className="text-base text-slate-500 mt-2">基于大模型技术，为您提供深度的招标文件解读、风险预警及投标策略建议。</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Panel: Configuration */}
        <div className="lg:col-span-1 space-y-6">
          <Card className="border-indigo-100 shadow-md">
            <CardHeader className="bg-indigo-50/50 border-b border-indigo-100">
              <CardTitle className="flex items-center gap-2 text-indigo-900">
                <Brain className="h-5 w-5" />
                分析配置
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">选择待分析项目</label>
                <select
                  className="flex h-11 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                  value={selectedProject}
                  onChange={(e) => setSelectedProject(e.target.value)}
                >
                  <option value="">-- 请选择项目 --</option>
                  {activeTenders.map(t => (
                    <option key={t.id} value={t.id}>{t.projectCode} - {t.projectName.substring(0, 20)}...</option>
                  ))}
                </select>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-semibold text-slate-700">分析维度</label>
                <div className="grid grid-cols-1 gap-3">
                  <div className="flex items-center p-3 border border-indigo-200 bg-indigo-50 rounded-lg cursor-pointer transition-colors">
                     <FileText className="h-5 w-5 text-indigo-600 mr-3" />
                     <div className="flex-1">
                       <p className="font-medium text-indigo-900 text-sm">核心解读 & 摘要</p>
                       <p className="text-xs text-indigo-600/80">提取关键指标与资质要求</p>
                     </div>
                     <CheckCircle2 className="h-5 w-5 text-indigo-600" />
                  </div>
                  <div className="flex items-center p-3 border border-slate-200 hover:bg-slate-50 rounded-lg cursor-pointer transition-colors">
                     <AlertTriangle className="h-5 w-5 text-slate-500 mr-3" />
                     <div className="flex-1">
                       <p className="font-medium text-slate-900 text-sm">风险合规审查</p>
                       <p className="text-xs text-slate-500">识别合同陷阱与废标风险</p>
                     </div>
                     <div className="h-5 w-5 rounded-full border border-slate-300"></div>
                  </div>
                  <div className="flex items-center p-3 border border-slate-200 hover:bg-slate-50 rounded-lg cursor-pointer transition-colors">
                     <Target className="h-5 w-5 text-slate-500 mr-3" />
                     <div className="flex-1">
                       <p className="font-medium text-slate-900 text-sm">投标策略生成</p>
                       <p className="text-xs text-slate-500">生成针对性响应大纲</p>
                     </div>
                     <div className="h-5 w-5 rounded-full border border-slate-300"></div>
                  </div>
                </div>
              </div>

              <Button
                className="w-full mt-4"
                size="lg"
                disabled={!selectedProject || isAnalyzing}
                onClick={handleAnalyze}
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    AI 正在深度思考中...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-5 w-5" />
                    开始智能分析
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          <div className="bg-slate-100 p-4 rounded-xl text-sm text-slate-500 border border-slate-200">
            <p className="font-medium text-slate-700 mb-1">💡 小贴士</p>
            AI 分析基于招标文件文本，结果仅供参考。重大决策请务必由专业人员复核原始文件。
          </div>
        </div>

        {/* Right Panel: Results */}
        <div className="lg:col-span-2 space-y-6">
          {!result && !isAnalyzing && (
            <div className="h-full min-h-[400px] flex flex-col items-center justify-center text-slate-400 bg-white border border-dashed border-slate-300 rounded-xl">
              <Brain className="h-16 w-16 mb-4 text-slate-200" />
              <p className="text-lg font-medium">请在左侧选择项目并开始分析</p>
              <p className="text-sm">AI 将为您生成多维度的项目洞察报告</p>
            </div>
          )}

          {isAnalyzing && (
             <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-white border border-slate-200 rounded-xl space-y-8 p-12">
                <div className="relative">
                  <div className="h-24 w-24 rounded-full border-4 border-indigo-100 animate-pulse"></div>
                  <div className="absolute top-0 left-0 h-24 w-24 rounded-full border-4 border-indigo-600 border-t-transparent animate-spin"></div>
                  <Sparkles className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-indigo-600 h-8 w-8" />
                </div>
                <div className="space-y-3 text-center max-w-md">
                   <h3 className="text-xl font-bold text-slate-900">正在解析招标文件...</h3>
                   <div className="space-y-2">
                      <div className="flex items-center gap-3 text-sm text-slate-500">
                        <CheckCircle2 className="h-4 w-4 text-emerald-500" /> 读取项目基础信息
                      </div>
                      <div className="flex items-center gap-3 text-sm text-slate-500">
                        <CheckCircle2 className="h-4 w-4 text-emerald-500" /> 提取资质与评分标准
                      </div>
                      <div className="flex items-center gap-3 text-sm text-slate-600 font-medium animate-pulse">
                        <Loader2 className="h-4 w-4 animate-spin" /> 计算项目匹配度与风险模型
                      </div>
                   </div>
                </div>
             </div>
          )}

          {result && !isAnalyzing && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="md:col-span-2 bg-gradient-to-br from-indigo-600 to-violet-700 text-white border-none overflow-hidden">
                  <CardContent className="p-0">
                    <div className="flex flex-col md:flex-row items-stretch">
                      <div className="flex-1 p-8">
                        <p className="text-indigo-100 font-medium mb-2">AI 推荐指数</p>
                        <div className="flex items-baseline gap-3">
                          <h3 className="text-5xl font-bold tracking-tight leading-none">{result.score}</h3>
                          <span className="text-2xl font-normal text-indigo-200 leading-none">/100</span>
                        </div>
                        <div className="mt-5 flex flex-wrap gap-2">
                          <span className="px-3 py-1 rounded-full bg-white/15 text-sm backdrop-blur-sm">
                            值得一试
                          </span>
                          <span className="px-3 py-1 rounded-full bg-white/15 text-sm backdrop-blur-sm">
                            风险可控
                          </span>
                        </div>
                      </div>
                      <div className="hidden md:flex items-center justify-center pr-8">
                        <div className="h-24 w-24 rounded-full bg-white/10 flex items-center justify-center">
                          <BarChart4 className="h-12 w-12 text-indigo-100/70" />
                        </div>
                      </div>
                    </div>
                    <div className="px-8 pb-8 pt-6 border-t border-white/15 bg-black/5">
                      <p className="text-sm text-indigo-50 leading-relaxed">
                        {result.summary}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base text-slate-500">硬性资质预审</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {result.requirements.map((req, idx) => (
                        <div key={idx} className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                             <p className="text-xs text-slate-400">{req.label}</p>
                             <p className="text-sm font-medium text-slate-900 line-clamp-1" title={req.value}>{req.value}</p>
                          </div>
                          {req.met ? (
                            <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
                          ) : (
                            <AlertTriangle className="h-5 w-5 text-red-500 shrink-0" />
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Strategy & Risks */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                 <Card className="border-l-4 border-l-amber-400">
                    <CardHeader>
                       <CardTitle className="flex items-center gap-2 text-lg">
                         <AlertTriangle className="h-5 w-5 text-amber-500" />
                         风险预警
                       </CardTitle>
                    </CardHeader>
                    <CardContent>
                       <ul className="space-y-3">
                         {result.risks.map((risk, i) => (
                           <li key={i} className="flex gap-3 text-base text-slate-700">
                             <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-amber-100 text-xs font-bold text-amber-700">{i + 1}</span>
                             {risk}
                           </li>
                         ))}
                       </ul>
                    </CardContent>
                 </Card>

                 <Card className="border-l-4 border-l-emerald-500">
                    <CardHeader>
                       <CardTitle className="flex items-center gap-2 text-lg">
                         <Target className="h-5 w-5 text-emerald-600" />
                         响应策略建议
                       </CardTitle>
                    </CardHeader>
                    <CardContent>
                       <div className="text-base text-slate-700 leading-relaxed">
                         {result.strategy}
                       </div>
                       <Button variant="outline" className="mt-6 w-full text-indigo-600 border-indigo-200 hover:bg-indigo-50">
                         生成详细技术方案大纲 <ChevronRight className="ml-1 h-4 w-4" />
                       </Button>
                    </CardContent>
                 </Card>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom History Section */}
      <Card>
        <CardHeader className="border-b border-slate-100 pb-4">
           <CardTitle className="flex items-center gap-2">
             <History className="h-5 w-5 text-slate-500" />
             最近分析记录
           </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
           <div className="overflow-x-auto">
             <table className="w-full text-left">
               <thead className="text-sm font-semibold text-slate-500 bg-slate-50/50">
                 <tr>
                    <th className="px-6 py-3">项目名称</th>
                    <th className="px-6 py-3">分析时间</th>
                    <th className="px-6 py-3">AI 推荐分</th>
                    <th className="px-6 py-3">核心风险标签</th>
                    <th className="px-6 py-3">决策建议</th>
                    <th className="px-6 py-3 text-right">操作</th>
                 </tr>
               </thead>
               <tbody className="divide-y divide-slate-100 text-base">
                 {MOCK_HISTORY.map((item) => (
                   <tr key={item.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-900">{item.projectName}</td>
                      <td className="px-6 py-4 text-slate-500 flex items-center gap-2">
                         <Clock className="h-4 w-4" /> {item.date}
                      </td>
                      <td className="px-6 py-4">
                         <span className={`px-2.5 py-0.5 rounded-md font-bold text-sm border ${getScoreColor(item.score)}`}>
                           {item.score}
                         </span>
                      </td>
                      <td className="px-6 py-4">
                         <span className="inline-flex items-center px-2 py-1 rounded bg-slate-100 text-slate-600 text-xs font-medium">
                           {item.riskTag}
                         </span>
                      </td>
                      <td className="px-6 py-4">
                         <span className={`inline-flex items-center gap-1.5 text-sm font-medium ${item.riskLevel === 'low' ? 'text-emerald-600' : item.riskLevel === 'medium' ? 'text-indigo-600' : 'text-slate-500'}`}>
                           {item.status === '建议放弃' ? <AlertTriangle className="h-4 w-4" /> : <FileCheck className="h-4 w-4" />}
                           {item.status}
                         </span>
                      </td>
                      <td className="px-6 py-4 text-right">
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
              <Button variant="ghost" size="sm" className="text-slate-500">查看更多历史记录</Button>
           </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AiAssistant;
