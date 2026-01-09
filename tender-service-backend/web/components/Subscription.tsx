import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Input, Select } from './ui/Input';
import { Plus, Trash2, BellRing, BellOff, MapPin, Tag } from 'lucide-react';
import { DISTRICTS } from '../constants';

interface SubItem {
  id: string;
  name: string;
  keywords: string;
  district: string;
  active: boolean;
  lastNotified?: string;
}

const Subscription: React.FC = () => {
  const [items, setItems] = useState<SubItem[]>([
    { id: '1', name: '朝阳区绿化重点监控', keywords: '绿化工程', district: '朝阳区', active: true, lastNotified: '2小时前' },
    { id: '2', name: '海淀智慧校园项目', keywords: '智慧校园, 多媒体', district: '海淀区', active: true, lastNotified: '1天前' },
    { id: '3', name: '全区医疗设备采购', keywords: '医疗设备, CT机', district: '所有区域', active: false },
  ]);

  const [isAdding, setIsAdding] = useState(false);
  const [newSub, setNewSub] = useState({ name: '', keywords: '', district: '' });

  const handleAdd = () => {
    if(!newSub.name || !newSub.keywords) return alert('请填写完整信息');
    setItems([...items, {
      id: Date.now().toString(),
      name: newSub.name,
      keywords: newSub.keywords,
      district: newSub.district || '所有区域',
      active: true
    }]);
    setIsAdding(false);
    setNewSub({ name: '', keywords: '', district: '' });
  };

  const toggleActive = (id: string) => {
    setItems(items.map(item => item.id === id ? { ...item, active: !item.active } : item));
  };

  const deleteItem = (id: string) => {
    if(confirm('确定要删除这条订阅规则吗？')) {
      setItems(items.filter(item => item.id !== id));
    }
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-6xl mx-auto">
       <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold text-slate-900">订阅管理</h2>
            <p className="text-base text-slate-500 mt-1">设置关键词监控，第一时间获取相关招标动态</p>
          </div>
          <Button onClick={() => setIsAdding(!isAdding)} variant={isAdding ? 'secondary' : 'primary'} size="lg">
            <Plus className="mr-2 h-5 w-5"/> {isAdding ? '取消添加' : '新建订阅'}
          </Button>
       </div>

       {isAdding && (
         <Card className="border-indigo-100 bg-indigo-50/30 animate-in slide-in-from-top-2 duration-200">
           <CardHeader><CardTitle className="text-lg text-indigo-900">添加新监控规则</CardTitle></CardHeader>
           <CardContent>
             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Input 
                  label="规则名称" 
                  placeholder="如：通州道路工程" 
                  value={newSub.name}
                  onChange={e => setNewSub({...newSub, name: e.target.value})}
                />
                <Input 
                  label="监控关键词" 
                  placeholder="多个关键词用逗号分隔" 
                  value={newSub.keywords}
                  onChange={e => setNewSub({...newSub, keywords: e.target.value})}
                />
                <Select 
                  label="限定区域" 
                  options={['所有区域', ...DISTRICTS]} 
                  value={newSub.district}
                  onChange={e => setNewSub({...newSub, district: e.target.value})}
                />
             </div>
             <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-indigo-100/50">
                <Button variant="ghost" onClick={() => setIsAdding(false)}>取消</Button>
                <Button onClick={handleAdd}>确认添加</Button>
             </div>
           </CardContent>
         </Card>
       )}

       <div className="grid gap-5">
         {items.length === 0 ? (
           <div className="text-center py-16 bg-white rounded-xl border border-dashed border-slate-300">
             <BellOff className="h-12 w-12 text-slate-300 mx-auto mb-4" />
             <p className="text-lg text-slate-500">暂无订阅规则，点击右上角添加</p>
           </div>
         ) : (
           items.map(item => (
              <Card key={item.id} className={`transition-all hover:shadow-md ${!item.active ? 'opacity-70 bg-slate-50' : ''}`}>
                 <div className="p-8 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                    <div className="flex items-start gap-5">
                       <div className={`mt-1 h-12 w-12 rounded-xl flex items-center justify-center shrink-0 transition-colors ${item.active ? 'bg-indigo-100 text-indigo-600' : 'bg-slate-200 text-slate-400'}`}>
                          {item.active ? <BellRing size={24} /> : <BellOff size={24} />}
                       </div>
                       <div>
                          <h3 className="font-bold text-slate-900 text-lg">{item.name}</h3>
                          <div className="flex flex-wrap gap-3 mt-3">
                             <span className="inline-flex items-center text-sm bg-slate-100 px-2.5 py-1 rounded-md text-slate-600 border border-slate-200">
                               <Tag size={14} className="mr-1.5" /> {item.keywords}
                             </span>
                             <span className="inline-flex items-center text-sm bg-slate-100 px-2.5 py-1 rounded-md text-slate-600 border border-slate-200">
                               <MapPin size={14} className="mr-1.5" /> {item.district}
                             </span>
                          </div>
                          {item.active && item.lastNotified && (
                            <p className="text-sm text-slate-400 mt-2.5">上次通知: {item.lastNotified}</p>
                          )}
                       </div>
                    </div>
                    
                    <div className="flex items-center gap-3 sm:self-center self-end">
                       <Button 
                         variant={item.active ? "secondary" : "outline"} 
                         size="md" 
                         onClick={() => toggleActive(item.id)}
                       >
                          {item.active ? '暂停监控' : '恢复监控'}
                       </Button>
                       <Button 
                         variant="ghost" 
                         size="icon" 
                         className="h-10 w-10 text-slate-400 hover:text-red-600 hover:bg-red-50"
                         onClick={() => deleteItem(item.id)}
                       >
                          <Trash2 size={20} />
                       </Button>
                    </div>
                 </div>
              </Card>
           ))
         )}
       </div>
    </div>
  )
}

export default Subscription;