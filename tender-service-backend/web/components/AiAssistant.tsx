import React, { useState, useEffect, useMemo, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { 
  Sparkles, Brain, AlertTriangle, FileText, CheckCircle2, 
  ChevronRight, Loader2, Target, BarChart4, History, 
  Layers, ShieldAlert, Lightbulb, TrendingUp, Briefcase, 
  Users, LineChart, Percent, ArrowRight, Award, BadgeCheck, Plus,
  Search, ChevronDown, X
} from 'lucide-react';
import { getApiUrl } from '../utils/api';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell
} from 'recharts';
import AnalysisHistory from './AnalysisHistory';

interface SimpleTender {
  tenderId: number;
  projectCode: string;
  projectName: string;
}

interface Competitor {
  name: string;
  reason: string;
  winRate: number;
  threatLevel: 'High' | 'Medium' | 'Low';
}

interface PriceDistribution {
  range: string;
  count: number;
}

interface AnalysisResult {
  score: number;
  summary: string;
  risks: string[];
  requirements: { label: string; value: string; met: boolean }[];
  strategy: string;
  // Extended fields for new UI
  radarData: { subject: string; A: number; fullMark: number }[];
  profitability: string;
  difficulty: string;
  competitors: Competitor[];
  priceStats: {
    avgDiscount: string;
    maxDiscount: string;
    distribution: PriceDistribution[];
  };
}

type PageResponse<T> = {
  code: number;
  msg: string;
  success: boolean;
  time: string;
  rows: T[];
  pageNum: number;
  pageSize: number;
  total: number;
  hasNext: boolean;
};

const AiAssistant: React.FC<{ onProgressChange?: (value: number) => void }> = ({ onProgressChange }) => {
  const [view, setView] = useState<'main' | 'history'>('main');
  const [selectedProject, setSelectedProject] = useState<number | null>(null);
  const [tenders, setTenders] = useState<SimpleTender[]>([]);
  const [isLoadingTenders, setIsLoadingTenders] = useState(false);
  const [isSearchingTenders, setIsSearchingTenders] = useState(false);
  const [searchResults, setSearchResults] = useState<SimpleTender[]>([]);
  
  const [isSelectOpen, setIsSelectOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchTimerRef = useRef<number | null>(null);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [progress, setProgress] = useState(0);
  const [stepMessage, setStepMessage] = useState("");
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'insight' | 'risk' | 'strategy'>('insight');
  const progressRafRef = useRef<number | null>(null);
  const progressRef = useRef<number>(0);
  const progressTargetRef = useRef<number>(0);
  const progressSpeedRef = useRef<number>(0);
  const desiredSpeedRef = useRef<number>(0);
  const lastFrameRef = useRef<number>(0);
  const pauseUntilRef = useRef<number>(0);
  const pendingMilestoneRef = useRef<boolean>(false);
  const resumeTargetRef = useRef<number>(0);
  const isAnalyzingRef = useRef<boolean>(false);
  const progressCallbackRef = useRef<(value: number) => void>(() => {});
  const flashTimeoutRef = useRef<number | null>(null);
  const [milestoneFlash, setMilestoneFlash] = useState(false);

  const [qualifications, setQualifications] = useState<string[]>([
    "具有良好的商业信誉和健全的财务会计制度",
    "具有施工劳务资质",
    "具有市政公用工程施工总承包贰级",
    "具有环保工程专业承包贰级",
    "具有两名一级市政公用工程建造师的项目经理",
    "具备有效的安全生产考核合格证书",
    "有履行合同所需的资金、技术能力、设备能力和人员",
    "没有处于被责令停业；财产被接管、冻结或破产状态",
    "近年内有多项园林绿化工程项目业绩"
  ]);

  const fetchTenderOptions = async (opts: { pageSize: number; projectCode?: string; projectName?: string }) => {
    const params = new URLSearchParams();
    params.set('page_num', '1');
    params.set('page_size', String(opts.pageSize));
    params.set('project_stage', '招标公告');
    if (opts.projectCode) params.set('project_code', opts.projectCode);
    if (opts.projectName) params.set('project_name', opts.projectName);
    const res = await fetch(getApiUrl(`/tenders?${params.toString()}`));
    const json = (await res.json()) as PageResponse<Partial<SimpleTender>>;
    if (!res.ok || !json.success) {
      return [];
    }
    return (json.rows || [])
      .map((r) => ({
        tenderId: Number(r.tenderId),
        projectCode: String(r.projectCode || ''),
        projectName: String(r.projectName || ''),
      }))
      .filter((r) => Boolean(r.tenderId) && (r.projectCode || r.projectName));
  };

  useEffect(() => {
    const run = async () => {
      setIsLoadingTenders(true);
      try {
        const items = await fetchTenderOptions({ pageSize: 50 });
        setTenders(items);
      } catch (error) {
        console.error("Failed to fetch tenders:", error);
        setTenders([]);
      } finally {
        setIsLoadingTenders(false);
      }
    };
    void run();
  }, []);

  useEffect(() => {
    isAnalyzingRef.current = isAnalyzing;
  }, [isAnalyzing]);

  useEffect(() => {
    if (onProgressChange) {
      progressCallbackRef.current = onProgressChange;
    }
  }, [onProgressChange]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsSelectOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (!isSelectOpen) {
      setIsSearchingTenders(false);
      setSearchResults([]);
      if (searchTimerRef.current) {
        window.clearTimeout(searchTimerRef.current);
        searchTimerRef.current = null;
      }
      return;
    }

    const term = searchTerm.trim();
    if (!term) {
      setIsSearchingTenders(false);
      setSearchResults([]);
      if (searchTimerRef.current) {
        window.clearTimeout(searchTimerRef.current);
        searchTimerRef.current = null;
      }
      return;
    }

    if (searchTimerRef.current) {
      window.clearTimeout(searchTimerRef.current);
      searchTimerRef.current = null;
    }

    searchTimerRef.current = window.setTimeout(() => {
      const run = async () => {
        setIsSearchingTenders(true);
        try {
          const [byCode, byName] = await Promise.all([
            fetchTenderOptions({ pageSize: 50, projectCode: term }),
            fetchTenderOptions({ pageSize: 50, projectName: term }),
          ]);
          const mergedMap = new Map<number, SimpleTender>();
          [...byCode, ...byName].forEach((item) => {
            if (item && item.tenderId) {
              mergedMap.set(item.tenderId, item);
            }
          });
          const merged = Array.from(mergedMap.values());
          setSearchResults(merged);
        } catch (error) {
          console.error("Failed to search tenders:", error);
          setSearchResults([]);
        } finally {
          setIsSearchingTenders(false);
        }
      };
      void run();
    }, 250);
  }, [isSelectOpen, searchTerm]);

  const augmentResult = (base: any): AnalysisResult => {
    // Backend now returns these fields, but we keep safe fallbacks just in case
    // Note: Check both camelCase and snake_case to handle potential serialization differences
    return {
        ...base,
        score: base.score || 0,
        profitability: base.profitability || "测算中...",
        difficulty: base.difficulty || "评估中...",
        radarData: base.radarData || base.radar_data || [],
        competitors: base.competitors || [],
        priceStats: base.priceStats || base.price_stats || {
          avgDiscount: '-',
          maxDiscount: '-',
          distribution: []
        },
        features: base.features || [],
        decisionConclusion: base.decisionConclusion || base.decision_conclusion || '',
        focusPoints: base.focusPoints || base.focus_points || []
    };
  };

  const updateProgress = (value: number) => {
    progressRef.current = value;
    setProgress(value);
    progressCallbackRef.current(value);
  };

  const stopProgressAnimation = () => {
    if (progressRafRef.current) {
      cancelAnimationFrame(progressRafRef.current);
      progressRafRef.current = null;
    }
  };

  const flashMilestone = () => {
    setMilestoneFlash(true);
    if (flashTimeoutRef.current) {
      window.clearTimeout(flashTimeoutRef.current);
    }
    flashTimeoutRef.current = window.setTimeout(() => {
      setMilestoneFlash(false);
      flashTimeoutRef.current = null;
    }, 450);
  };

  const BASE_SPEED = 0.001; // 4% per second
  const BOOST_SPEED = 0.012; // 12% per second
  const PROGRESS_STAGES = [20, 40, 60, 80, 95];

  const startProgressAnimation = () => {
    stopProgressAnimation();
    progressSpeedRef.current = BASE_SPEED;
    desiredSpeedRef.current = BASE_SPEED;
    lastFrameRef.current = 0;

    const step = (ts: number) => {
      if (!isAnalyzingRef.current) {
        stopProgressAnimation();
        return;
      }
      if (!lastFrameRef.current) {
        lastFrameRef.current = ts;
        progressRafRef.current = requestAnimationFrame(step);
        return;
      }
      const dt = ts - lastFrameRef.current;
      lastFrameRef.current = ts;
      if (pauseUntilRef.current > ts) {
        progressRafRef.current = requestAnimationFrame(step);
        return;
      }
      progressSpeedRef.current += (desiredSpeedRef.current - progressSpeedRef.current) * 0.08;
      const next = Math.min(progressRef.current + progressSpeedRef.current * dt, progressTargetRef.current);
      updateProgress(next);
      if (next >= progressTargetRef.current - 0.01) {
        if (pendingMilestoneRef.current) {
          pendingMilestoneRef.current = false;
          pauseUntilRef.current = ts + 500;
          if (resumeTargetRef.current > progressTargetRef.current) {
            progressTargetRef.current = resumeTargetRef.current;
            desiredSpeedRef.current = BASE_SPEED;
          }
          flashMilestone();
        }
      }
      progressRafRef.current = requestAnimationFrame(step);
    };

    progressRafRef.current = requestAnimationFrame(step);
  };

  const handleAnalyze = () => {
    if (!selectedProject) return;
    setIsAnalyzing(true);
    setResult(null);
    updateProgress(0);
    setStepMessage("准备开始分析...");
    setAnalyzeError(null);
    setActiveTab('insight');
    
    // Initial creep to first stage
    const firstStage = PROGRESS_STAGES[0];
    progressTargetRef.current = firstStage;
    resumeTargetRef.current = firstStage;
    
    pauseUntilRef.current = 0;
    pendingMilestoneRef.current = false;
    progressRef.current = 0;
    startProgressAnimation();

    const params = new URLSearchParams();
    if (qualifications.length > 0) {
      params.set('qualifications', JSON.stringify(qualifications));
    }
    const query = params.toString();
    const url = getApiUrl(`/tenders/${selectedProject}/ai-analysis/stream${query ? `?${query}` : ''}`);
    const eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (typeof data.progress === 'number') {
          const target = Math.min(data.progress, 99);
          if (target > progressRef.current) {
            progressTargetRef.current = target;
            
            // Calculate next stage to creep towards
            const nextStage = PROGRESS_STAGES.find(s => s > target) || 99;
            resumeTargetRef.current = nextStage;
            
            desiredSpeedRef.current = BOOST_SPEED;
            pendingMilestoneRef.current = true;
          }
        }
        if (data.message) {
          setStepMessage(data.message);
        }
        if (data.result) {
          setResult(augmentResult(data.result));
          progressTargetRef.current = 100;
          updateProgress(100);
          setIsAnalyzing(false);
          stopProgressAnimation();
          eventSource.close();
        }
      } catch (error) {
        console.error("Error parsing SSE data", error);
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE Error", error);
      eventSource.close();
      setAnalyzeError("分析过程中出现错误，请稍后重试");
      setIsAnalyzing(false);
      stopProgressAnimation();
    };
  };

  const handleViewReport = async (tenderId: number) => {
    setView('main');
    setSelectedProject(tenderId);
    setIsAnalyzing(true);
    setAnalyzeError(null);
    setProgress(100);
    setStepMessage("加载历史分析结果...");
    try {
      const res = await fetch(getApiUrl(`/tenders/${tenderId}/ai-analysis`));
      const data = await res.json();
      if (!data.success || !data.data) {
        throw new Error(data.msg || '加载失败');
      }
      setResult(augmentResult(data.data));
      setActiveTab('insight');
    } catch (error) {
      setAnalyzeError("加载历史分析失败，请稍后重试");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAddQualification = () => {
    const q = window.prompt("请输入新的资质名称（如：机电工程施工总承包三级）：");
    if(q) setQualifications([...qualifications, q]);
  };

  const baseOptions = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    const source = term ? searchResults : tenders;
    if (!term) return source;
    return source.filter(
      (t) =>
        (t.projectName || '').toLowerCase().includes(term) ||
        (t.projectCode || '').toLowerCase().includes(term)
    );
  }, [searchResults, tenders, searchTerm]);

  const scoreMeta = useMemo(() => {
    if (!result) return null;
    
    // Default meta based on score ranges for color/styling
    let meta = {
      label: '风险较高',
      badgeClassName: 'bg-red-50 text-red-800 border-red-200',
      dotColor: 'text-red-500',
      hint: '建议谨慎参与',
    };

    if (result.score >= 80) {
      meta = {
        label: '胜算高',
        badgeClassName: 'bg-emerald-50 text-emerald-800 border-emerald-200',
        dotColor: 'text-emerald-500',
        hint: '击败了 85% 的类似项目',
      };
    } else if (result.score >= 60) {
      meta = {
        label: '机会适中',
        badgeClassName: 'bg-amber-50 text-amber-800 border-amber-200',
        dotColor: 'text-amber-500',
        hint: '建议谨慎参与',
      };
    }
    
    return {
        ...meta,
        // Use backend data if available, otherwise fall back to generic messages based on score
        conclusion: result.decisionConclusion || (
            result.score >= 80 ? '整体来看，该项目胜算较高，建议作为重点目标积极推进。' :
            result.score >= 60 ? '整体来看，该项目机会与风险并存，建议进行详细评估后再做决策。' :
            '整体来看，该项目存在较大风险，建议谨慎参与或放弃。'
        ),
        features: result.features && result.features.length > 0 ? result.features : (
            result.score >= 80 ? ['资质完美匹配', '预算充足', '竞争烈度低'] :
            result.score >= 60 ? ['资质符合', '存在价格博弈'] :
            ['风险极高', '利润空间低']
        )
    };
  }, [result]);

  const selectedTenderObj = tenders.find(t => t.tenderId === selectedProject) || searchResults.find(t => t.tenderId === selectedProject);

  if (view === 'history') return <AnalysisHistory onBack={() => setView('main')} onViewReport={handleViewReport} />;

  return (
    <div className="space-y-6 animate-fade-in max-w-[1920px] mx-auto h-full flex flex-col">
      {/* Header Area */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-2">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <Sparkles className="h-6 w-6 text-indigo-600" />
            AI 智能参谋
          </h2>
          <p className="text-sm text-slate-500 mt-1">企业级大模型驱动 | 深度标书解析 | 实时风险风控</p>
        </div>
        <div className="flex items-center gap-3">
           <Button 
             variant="secondary" 
             onClick={() => setView('history')} 
             className="bg-white border border-slate-200 shadow-sm text-slate-600 hover:bg-slate-50"
           >
             <History className="mr-2 h-4 w-4 text-slate-500" /> 分析历史
           </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
        {/* Left Config Panel & Credentials */}
        <div className="lg:col-span-3 space-y-6 h-fit sticky top-6">
          {/* Config Card */}
          <Card className="border-slate-200 shadow-sm bg-white">
            <CardHeader className="py-4 border-b border-slate-100">
              <CardTitle className="text-sm uppercase tracking-wider text-slate-500 font-bold">
                配置面板
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="space-y-2" ref={dropdownRef}>
                <label className="text-sm font-semibold text-slate-700 flex items-center gap-1">
                  <span>目标项目</span>
                  <span
                    className="ml-1 inline-flex items-center justify-center w-4 h-4 text-[10px] rounded-full bg-slate-200 text-slate-600 cursor-help"
                    title="目标项目仅支持招标公告"
                  >
                    i
                  </span>
                </label>
                {/* Custom Searchable Select */}
                <div className="relative">
                  <div 
                    className={`flex items-center justify-between w-full h-10 px-3 py-2 text-sm bg-white border rounded-md cursor-pointer transition-all ${isSelectOpen ? 'border-indigo-500 ring-2 ring-indigo-100' : 'border-slate-200 hover:border-slate-300'}`}
                    onClick={() => {
                        setIsSelectOpen(!isSelectOpen);
                        if (!isSelectOpen) setSearchTerm("");
                    }}
                  >
                    <span className={`block truncate ${selectedTenderObj ? 'text-slate-900' : 'text-slate-400'}`}>
                      {selectedTenderObj 
                        ? `${selectedTenderObj.projectName}（${selectedTenderObj.projectCode}）`
                        : (isLoadingTenders ? "加载项目中..." : "-- 请选择或搜索项目 --")}
                    </span>
                    <div className="flex items-center">
                        {selectedProject && (
                            <div 
                                className="p-1 hover:bg-slate-100 rounded-full mr-1 cursor-pointer"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedProject(null);
                                }}
                            >
                                <X className="h-3 w-3 text-slate-400" />
                            </div>
                        )}
                        <ChevronDown className={`h-4 w-4 text-slate-400 transition-transform ${isSelectOpen ? 'rotate-180' : ''}`} />
                    </div>
                  </div>

                  {isSelectOpen && (
                    <div className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg animate-in fade-in zoom-in-95 duration-100">
                      <div className="p-2 border-b border-slate-100">
                        <div className="relative">
                            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
                            <input 
                                type="text"
                                className="w-full pl-9 pr-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                                placeholder="输入编号或名称搜索..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                onClick={(e) => e.stopPropagation()}
                                autoFocus
                            />
                        </div>
                      </div>
                      <div className="max-h-60 overflow-y-auto py-1 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
                        {isSearchingTenders ? (
                          <div className="px-4 py-3 text-sm text-slate-400 text-center flex items-center justify-center gap-2">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            搜索中...
                          </div>
                        ) : baseOptions.length === 0 ? (
                          <div className="px-4 py-3 text-sm text-slate-400 text-center">
                            {searchTerm.trim() ? "无相关项目" : (isLoadingTenders ? "加载中..." : "暂无项目")}
                          </div>
                        ) : (
                            baseOptions.map(t => (
                                <div 
                                    key={t.tenderId}
                                    className={`px-3 py-2 text-sm cursor-pointer hover:bg-indigo-50 transition-colors ${selectedProject === t.tenderId ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-700'}`}
                                    onClick={() => {
                                        setSelectedProject(t.tenderId);
                                        setIsSelectOpen(false);
                                    }}
                                >
                                    <div className="flex items-center justify-between gap-2">
                                        <span className="truncate flex-1">{t.projectName}</span>
                                        <span className="text-xs text-slate-400 shrink-0">{t.projectCode}</span>
                                    </div>
                                </div>
                            ))
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">分析模式</label>
                <div className="space-y-2">
                   {['深度全维分析', '快速风险筛查', '商务报价测算'].map((mode, i) => (
                      <div key={i} className={`flex items-center p-2.5 rounded-lg border text-sm cursor-pointer transition-all ${i === 0 ? 'border-indigo-600 bg-indigo-50/50 text-indigo-700 font-medium' : 'border-transparent hover:bg-slate-50 text-slate-600'}`}>
                         <div className={`w-2 h-2 rounded-full mr-3 ${i === 0 ? 'bg-indigo-600' : 'bg-slate-300'}`}></div>
                         {mode}
                      </div>
                   ))}
                </div>
              </div>

              <Button 
                className="w-full" 
                size="lg" 
                disabled={!selectedProject || isAnalyzing}
                onClick={handleAnalyze}
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    {stepMessage || "分析中..."} ({Math.floor(progress)}%)
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

          {/* Credentials Card */}
          <Card className="border-slate-200 shadow-sm bg-white">
             <CardHeader className="py-4 border-b border-slate-100">
               <CardTitle className="flex items-center gap-2 text-sm uppercase tracking-wider text-slate-500 font-bold">
                 <Award className="h-4 w-4" />
                 企业资质档案
               </CardTitle>
             </CardHeader>
             <CardContent className="space-y-4 pt-6">
                <div className="space-y-2">
                   {qualifications.map((q, i) => (
                     <div key={i} className="flex items-center gap-2 p-2.5 bg-slate-50 border border-slate-100 rounded-md text-sm text-slate-700 transition-colors hover:border-slate-300">
                        <BadgeCheck className="h-4 w-4 text-emerald-500 shrink-0" />
                        <span className="truncate" title={q}>{q}</span>
                     </div>
                   ))}
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full border-dashed border-slate-300 text-slate-500 hover:text-indigo-600 hover:border-indigo-300 hover:bg-indigo-50"
                  onClick={handleAddQualification}
                >
                  <Plus className="h-4 w-4 mr-1.5" /> 添加新资质
                </Button>
                <div className="text-xs text-slate-400 bg-slate-50/50 p-3 rounded leading-relaxed border border-slate-50">
                   AI 将读取以上资质信息，在“硬性门槛自查”环节自动比对招标文件要求。
                </div>
             </CardContent>
          </Card>
        </div>

        {/* Right Results Panel */}
        <div className="lg:col-span-9 space-y-6">
          {analyzeError && (
            <div className="h-[600px] flex flex-col items-center justify-center bg-white border border-red-200 rounded-xl shadow-sm p-12">
              <div className="h-16 w-16 bg-red-50 rounded-full flex items-center justify-center mb-6">
                <AlertTriangle className="h-8 w-8 text-red-500" />
              </div>
              <h3 className="text-lg font-bold text-red-700">{analyzeError}</h3>
              <p className="text-slate-500 text-sm mt-2">请检查网络或稍后重试</p>
              <div className="mt-6">
                <Button 
                  onClick={handleAnalyze} 
                  disabled={!selectedProject}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  重新尝试分析
                </Button>
              </div>
            </div>
          )}
          {!result && !isAnalyzing && (
            <div className="h-[600px] flex flex-col items-center justify-center text-slate-400 bg-white border border-dashed border-slate-200 rounded-xl shadow-sm">
              <div className="h-16 w-16 bg-slate-50 rounded-full flex items-center justify-center mb-6">
                <Brain className="h-8 w-8 text-slate-300" />
              </div>
              <p className="text-base font-medium text-slate-600">等待输入指令</p>
              <p className="text-sm text-slate-400 mt-1">请在左侧选择项目以启动 AI 参谋引擎</p>
            </div>
          )}

          {isAnalyzing && (
             <div className="h-[600px] flex flex-col items-center justify-center bg-white border border-slate-200 rounded-xl shadow-sm p-12">
                <div className="relative mb-6">
                  <div className="h-20 w-20 rounded-full border-4 border-slate-100"></div>
                  <div className="absolute top-0 left-0 h-20 w-20 rounded-full border-4 border-indigo-600 border-t-transparent animate-spin"></div>
                  <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-indigo-900 font-bold text-lg ${milestoneFlash ? 'animate-pulse' : ''}`}>
                    {Math.floor(progress)}%
                  </div>
                </div>
                <h3 className="text-lg font-bold text-slate-900 animate-pulse">{stepMessage || "正在进行深度分析..."}</h3>
                <p className="text-slate-500 text-sm mt-2">读取招标文件 / 构建知识图谱 / 评估风险实体</p>
                
                {/* Progress Steps */}
                <div className="flex justify-between text-xs text-slate-400 mt-8 w-full max-w-md px-4">
                   <span className={progress >= 10 ? "text-indigo-600 font-medium" : ""}>文件获取</span>
                   <span className={progress >= 30 ? "text-indigo-600 font-medium" : ""}>智能解析</span>
                   <span className={progress >= 60 ? "text-indigo-600 font-medium" : ""}>核心分析</span>
                   <span className={progress >= 90 ? "text-indigo-600 font-medium" : ""}>策略生成</span>
                </div>
                <div className="w-full max-w-md bg-slate-100 h-1 mt-2 rounded-full overflow-hidden">
                   <div className={`h-full bg-indigo-600 ${milestoneFlash ? 'shadow-[0_0_12px_rgba(99,102,241,0.7)]' : ''}`} style={{ width: `${progress}%` }}></div>
                </div>
             </div>
          )}

          {result && !isAnalyzing && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
              
              {/* 1. Score Overview Cards (Clean White Style) */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="border-slate-200 shadow-sm overflow-hidden relative">
                  {/* Decorative Target Icon */}
                  <div className="absolute top-4 right-4 pointer-events-none">
                     <div className="h-10 w-10 rounded-full bg-indigo-50/80 flex items-center justify-center">
                       <Target className="h-5 w-5 text-indigo-600" />
                     </div>
                  </div>

                  <CardContent className="min-h-[220px] flex flex-col pt-6 pb-6">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 w-full text-left">综合推荐指数</p>
                    
                    <div className="flex-1 flex flex-col items-center justify-center w-full">
                      {/* 分值 */}
                      <div className="flex items-baseline gap-2 leading-none mb-4">
                        <span className="text-6xl font-bold text-indigo-600 tracking-tight">
                          {result.score}
                        </span>
                        <span className="text-base text-slate-400 pb-2">/ 100</span>
                      </div>

                      {/* 状态提示框 */}
                      <div 
                        className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg border text-sm font-medium transition-colors mb-4 w-full max-w-[80%] ${scoreMeta?.badgeClassName}`}
                      >
                        <span className={`text-[10px] ${scoreMeta?.dotColor} shrink-0`}>●</span>
                        <span className="truncate">模型判断：{scoreMeta?.label}</span>
                      </div>

                      {/* AI 特征标签 */}
                      <div className="flex gap-2 flex-wrap justify-center w-full max-h-[60px] overflow-hidden">
                          {scoreMeta?.features?.map((feature, i) => (
                             <span key={i} className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200 truncate max-w-[100%]">
                                #{feature}
                             </span>
                          ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-slate-200 shadow-sm">
                  <CardContent className="h-[220px] flex flex-col pt-6">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                      评分依据（能力维度雷达）
                    </p>
                    <div className="flex-1 flex items-center justify-center">
                      <div className="w-full" style={{ height: 170 }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart cx="50%" cy="50%" outerRadius="78%" data={result.radarData}>
                            <PolarGrid stroke="#f1f5f9" />
                            <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                            <Radar name="Project" dataKey="A" stroke="#6366f1" strokeWidth={2} fill="#6366f1" fillOpacity={0.1} />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-slate-200 shadow-sm">
                  <CardContent className="min-h-[220px] flex flex-col pt-6 pb-6">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">决策建议</p>
                    <div className="mt-2 text-xl font-bold text-slate-900 leading-snug line-clamp-4" title={scoreMeta?.conclusion}>
                      {scoreMeta?.conclusion}
                    </div>
                    <div className="mt-4 grid grid-cols-2 gap-4">
                      <div className="min-w-0">
                        <p className="text-xs text-slate-400 uppercase font-semibold truncate">预估利润率</p>
                        <p className="text-lg font-bold text-slate-900 mt-1 truncate" title={result.profitability}>{result.profitability}</p>
                      </div>
                      <div className="border-l border-slate-100 pl-4 min-w-0">
                        <p className="text-xs text-slate-400 uppercase font-semibold truncate">实施难度</p>
                        <p className="text-lg font-bold text-slate-900 mt-1 truncate" title={result.difficulty}>{result.difficulty}</p>
                      </div>
                    </div>
                    <div className="mt-auto pt-4 border-t border-slate-100 flex items-center justify-between">
                      <span className="text-xs text-slate-500">
                        关键风险点 <span className="font-bold text-amber-600">{result.risks.length}</span>
                      </span>
                      <ArrowRight size={14} className="text-slate-300" />
                    </div>
                  </CardContent>
                </Card>
              </div>



              {/* 2. Detailed Tabs (Clean Underline Style) */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm min-h-[500px]">
                <div className="flex items-center px-6 border-b border-slate-100">
                   {[
                     { id: 'insight', label: '项目透视', icon: Layers },
                     { id: 'risk', label: '风险雷达', icon: ShieldAlert },
                     { id: 'strategy', label: '破局策略', icon: Lightbulb }
                   ].map((tab) => (
                     <button 
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`flex items-center gap-2 px-4 py-5 text-sm font-medium transition-all border-b-2 ${
                           activeTab === tab.id 
                           ? 'border-indigo-600 text-indigo-600' 
                           : 'border-transparent text-slate-500 hover:text-slate-900'
                        }`}
                     >
                        <tab.icon size={16} />
                        {tab.label}
                     </button>
                   ))}
                </div>

                <div className="p-8">
                   {activeTab === 'insight' && (
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 animate-in fade-in duration-300">
                         <div className="lg:col-span-2 space-y-8">
                            <div>
                               <h3 className="text-lg font-bold text-slate-900 mb-3">核心摘要</h3>
                               <p className="text-slate-700 leading-7 text-base text-justify whitespace-pre-wrap">{result.summary}</p>
                            </div>
                            
                            <div>
                               <h3 className="text-base font-bold text-slate-900 mb-4">硬性门槛自查</h3>
                               <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                  {result.requirements.map((req, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-3.5 rounded-lg border border-slate-100 bg-slate-50/50">
                                       <div className="flex flex-col min-w-0 pr-4">
                                          <span className="text-xs text-slate-500 mb-0.5">{req.label}</span>
                                          <span className="font-medium text-slate-900 text-sm truncate" title={req.value}>{req.value}</span>
                                       </div>
                                       {req.met ? <CheckCircle2 className="text-emerald-500 h-4 w-4 shrink-0"/> : <AlertTriangle className="text-red-500 h-4 w-4 shrink-0"/>}
                                    </div>
                                  ))}
                               </div>
                            </div>
                         </div>
                            <div className="bg-slate-50 rounded-xl p-6 border border-slate-100 h-fit">
                            <h4 className="font-bold text-slate-900 mb-4 flex items-center gap-2 text-sm uppercase tracking-wide">
                              <Target size={16} className="text-indigo-600"/> 重点关注
                            </h4>
                            <ul className="space-y-4">
                               {result.focusPoints && result.focusPoints.length > 0 ? (
                                   result.focusPoints.map((point, idx) => (
                                       <li key={idx} className="flex gap-3 text-base text-slate-700">
                                          <span className="font-bold text-slate-400">{String(idx + 1).padStart(2, '0')}</span>
                                          <span>{point}</span>
                                       </li>
                                   ))
                               ) : (
                                   // Fallback if no focus points (e.g. old data or analysis failed)
                                   <>
                                       <li className="flex gap-3 text-base text-slate-700">
                                          <span className="font-bold text-slate-400">01</span>
                                          <span>工期极其紧张，需提前锁定劳务班组。</span>
                                       </li>
                                       <li className="flex gap-3 text-base text-slate-700">
                                          <span className="font-bold text-slate-400">02</span>
                                          <span>主要材料不调差，需与供应商锁定价格。</span>
                                       </li>
                                       <li className="flex gap-3 text-base text-slate-700">
                                          <span className="font-bold text-slate-400">03</span>
                                          <span>数字化平台为加分项，建议引用过往案例。</span>
                                       </li>
                                   </>
                               )}
                            </ul>
                         </div>
                      </div>
                   )}

                   {activeTab === 'risk' && (
                      <div className="space-y-8 animate-in fade-in duration-300">
                      <div className="grid grid-cols-1 gap-8">
                             <div>
                                <h4 className="font-bold text-slate-900 text-base mb-4">关键风险项 ({result.risks.length})</h4>
                                <ul className="space-y-3">
                                   {result.risks.map((risk, i) => (
                                    <li key={i} className="flex gap-3 text-base text-slate-800 bg-amber-50/50 p-4 rounded-lg border border-amber-100">
                                       <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-amber-100 text-xs font-bold text-amber-700 mt-0.5">{i + 1}</span>
                                       <span className="leading-relaxed">{risk}</span>
                                     </li>
                                   ))}
                                </ul>
                             </div>
                          </div>
                      </div>
                   )}

                   {activeTab === 'strategy' && (
                      <div className="space-y-6 animate-in fade-in duration-300">
                          <div className="prose max-w-none text-slate-800 text-base">
                             <div className="bg-slate-50 p-6 rounded-xl border border-slate-100">
                               <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
                                  <Lightbulb className="h-5 w-5 text-indigo-600" />
                                  AI 破局策略建议
                               </h3>
                               <div className="leading-relaxed">
                                  <ReactMarkdown
                                    components={{
                                      h1: ({node, ...props}) => <h1 className="text-xl font-bold mb-4 mt-6 text-slate-900 border-b border-slate-200 pb-2" {...props} />,
                                      h2: ({node, ...props}) => <h2 className="text-lg font-bold mb-3 mt-5 text-slate-900" {...props} />,
                                      h3: ({node, ...props}) => <h3 className="text-base font-bold mb-2 mt-4 text-slate-900" {...props} />,
                                      p: ({node, ...props}) => <p className="mb-3 text-slate-700 leading-7" {...props} />,
                                      ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-2 mb-4 text-slate-700" {...props} />,
                                      ol: ({node, ...props}) => <ol className="list-decimal list-inside space-y-2 mb-4 text-slate-700" {...props} />,
                                      li: ({node, ...props}) => <li className="pl-1 marker:text-indigo-400" {...props} />,
                                      strong: ({node, ...props}) => <strong className="font-semibold text-slate-900 bg-indigo-50 px-1 rounded" {...props} />,
                                      blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-indigo-300 pl-4 py-2 my-4 bg-white rounded-r italic text-slate-600 shadow-sm" {...props} />,
                                      code: ({node, ...props}) => <code className="bg-slate-100 text-pink-600 px-1.5 py-0.5 rounded text-sm font-mono" {...props} />,
                                    }}
                                  >
                                    {result.strategy}
                                  </ReactMarkdown>
                               </div>
                             </div>
                          </div>
                      </div>
                   )}
                </div>
              </div>

              <Card className="border-slate-200 shadow-sm">
                 <CardContent className="pt-6">
                    <div className="flex items-center gap-2 mb-6">
                        <TrendingUp className="h-5 w-5 text-indigo-600" />
                        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">市场情报与竞争态势</h3>
                    </div>
                    
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Left Column: Competitors */}
                        <div>
                            <h4 className="font-bold text-slate-900 text-sm mb-4">潜在竞争对手预测</h4>
                            <div className="overflow-hidden rounded-lg border border-slate-200">
                                <table className="w-full text-left text-sm">
                                    <thead className="bg-slate-50 text-slate-500">
                                        <tr>
                                            <th className="px-4 py-2 font-medium">企业名称</th>
                                            <th className="px-4 py-2 font-medium">历史胜率</th>
                                            <th className="px-4 py-2 font-medium">威胁等级</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {result.competitors.map((comp, idx) => (
                                            <tr key={idx} className="bg-white hover:bg-slate-50/50">
                                                <td className="px-4 py-3 font-medium text-slate-900">{comp.name}</td>
                                                <td className="px-4 py-3 text-slate-500">{comp.winRate}%</td>
                                                <td className="px-4 py-3">
                                                    <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium border ${
                                                        comp.threatLevel === 'High' ? 'bg-red-50 text-red-700 border-red-100' :
                                                        comp.threatLevel === 'Medium' ? 'bg-amber-50 text-amber-700 border-amber-100' :
                                                        'bg-slate-50 text-slate-600 border-slate-200'
                                                    }`}>
                                                        {comp.threatLevel}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* Right Column: Price Distribution */}
                        <div>
                            <div className="flex justify-between items-center mb-4">
                                <h4 className="font-bold text-slate-900 text-sm">同类项目报价分布</h4>
                                <div className="text-xs text-slate-500">
                                    平均下浮: <span className="font-bold text-slate-900">{result.priceStats.avgDiscount}</span>
                                    <span className="mx-2">|</span>
                                    最大下浮: <span className="font-bold text-slate-900">{result.priceStats.maxDiscount}</span>
                                </div>
                            </div>
                            <div className="h-[200px] w-full">
                               <ResponsiveContainer width="100%" height="100%">
                                  <BarChart data={result.priceStats.distribution}>
                                     <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                     <XAxis dataKey="range" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} dy={10} />
                                     <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                                     <Tooltip 
                                        cursor={{ fill: '#f8fafc' }}
                                        contentStyle={{ borderRadius: '6px', border: '1px solid #e2e8f0', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', fontSize: '12px' }}
                                     />
                                     <Bar dataKey="count" fill="#cbd5e1" radius={[2, 2, 0, 0]} barSize={24}>
                                       {result.priceStats.distribution.map((entry, index) => (
                                          <Cell key={`cell-${index}`} fill={index === 2 ? '#6366f1' : '#cbd5e1'} />
                                       ))}
                                     </Bar>
                                  </BarChart>
                               </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                 </CardContent>
              </Card>

              {/* 4. Tip Section */}
              <div className="mt-8 mb-4 p-4 rounded-lg bg-indigo-50/50 border border-indigo-100 flex items-start gap-3">
                  <div className="bg-indigo-100 p-1.5 rounded-full mt-0.5">
                     <Lightbulb className="h-4 w-4 text-indigo-600" />
                  </div>
                  <div>
                     <h5 className="text-sm font-bold text-indigo-900 mb-1">💡 小贴士</h5>
                     <p className="text-sm text-indigo-900/70 leading-relaxed">
                        AI 分析基于招标文件文本，结果仅供参考。重大决策请务必由专业人员复核原始文件。
                     </p>
                  </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AiAssistant;
