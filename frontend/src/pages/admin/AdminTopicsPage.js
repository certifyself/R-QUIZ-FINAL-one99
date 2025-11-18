import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Plus, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

export function AdminTopicsPage() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    try {
      const res = await adminAPI.getTopics();
      setTopics(res.data.topics);
    } catch (error) {
      toast.error('Failed to load topics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <Button onClick={() => navigate('/admin')} variant="ghost">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Button>
        <h1 className="text-3xl font-bold text-slate-900 font-['Space_Grotesk']">Manage Topics</h1>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="divide-y divide-slate-200">
          {topics.map((topic) => (
            <div key={topic._id} className="p-4 flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-slate-900">{topic.name}</h3>
                <p className="text-sm text-slate-600">{topic.question_count || 0} questions</p>
              </div>
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                topic.active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'
              }`}>
                {topic.active ? 'Active' : 'Inactive'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
