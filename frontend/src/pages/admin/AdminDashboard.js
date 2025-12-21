import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { adminAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Plus, Users, BookOpen, Calendar, BarChart, Bell, Image } from 'lucide-react';
import { toast } from 'sonner';

export function AdminDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [metricsRes, topicsRes] = await Promise.all([
        adminAPI.getMetrics(),
        adminAPI.getTopics()
      ]);
      setMetrics(metricsRes.data);
      setTopics(topicsRes.data.topics);
    } catch (error) {
      toast.error('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePack = async () => {
    const today = new Date().toISOString().split('T')[0];
    try {
      await adminAPI.generatePack(today);
      toast.success('Today\'s pack generated successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate pack');
    }
  };

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-slate-900 font-['Space_Grotesk']">Admin Dashboard</h1>
        <Button onClick={() => navigate('/')} variant="outline">Back to App</Button>
      </div>

      {/* Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center space-x-3 mb-2">
              <Users className="w-6 h-6 text-teal-600" />
              <h3 className="font-semibold text-slate-700">Total Users</h3>
            </div>
            <p className="text-3xl font-bold text-slate-900 font-['Azeret_Mono']">{metrics.total_users}</p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center space-x-3 mb-2">
              <BookOpen className="w-6 h-6 text-teal-600" />
              <h3 className="font-semibold text-slate-700">Quizzes Today</h3>
            </div>
            <p className="text-3xl font-bold text-slate-900 font-['Azeret_Mono']">{metrics.quizzes_played_today}</p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center space-x-3 mb-2">
              <BarChart className="w-6 h-6 text-teal-600" />
              <h3 className="font-semibold text-slate-700">Avg Success Rate</h3>
            </div>
            <p className="text-3xl font-bold text-slate-900 font-['Azeret_Mono']">{metrics.avg_success_rate}%</p>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-xl p-6 border border-slate-200">
        <h2 className="text-xl font-bold text-slate-900 mb-4 font-['Space_Grotesk']">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Button
            onClick={handleGeneratePack}
            className="h-20 bg-gradient-to-r from-teal-500 to-teal-600"
            data-testid="generate-pack-button"
          >
            <Calendar className="w-5 h-5 mr-2" />
            Generate Today's Pack
          </Button>
          <Button
            onClick={() => navigate('/admin/topics')}
            variant="outline"
            className="h-20"
          >
            <BookOpen className="w-5 h-5 mr-2" />
            Manage Topics & Questions
          </Button>
          <Button
            onClick={() => navigate('/admin/ads')}
            variant="outline"
            className="h-20"
          >
            <BarChart className="w-5 h-5 mr-2" />
            Ads Placement
          </Button>
          <Button
            onClick={() => navigate('/admin/notifications')}
            variant="outline"
            className="h-20"
          >
            <Bell className="w-5 h-5 mr-2" />
            Push Notifications
          </Button>
        </div>
      </div>

      {/* Topics Overview */}
      <div className="bg-white rounded-xl p-6 border border-slate-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-slate-900 font-['Space_Grotesk']">Topics Overview</h2>
          <Button onClick={() => navigate('/admin/topics')} size="sm">View All</Button>
        </div>
        <p className="text-slate-600">Total Topics: <span className="font-semibold">{topics.length}</span></p>
        <p className="text-slate-600">Active Topics: <span className="font-semibold">{topics.filter(t => t.active).length}</span></p>
      </div>
    </div>
  );
}
