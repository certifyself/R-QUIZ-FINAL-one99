import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { ArrowLeft, Send, Bell, Users, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

export function AdminNotificationsPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [sendOpen, setSendOpen] = useState(false);
  const [sending, setSending] = useState(false);
  
  const [notificationForm, setNotificationForm] = useState({
    title: '',
    body: '',
    target: 'all'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [logsRes, statsRes] = await Promise.all([
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/notifications/logs`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        }),
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/notifications/stats`, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        })
      ]);
      
      const logsData = await logsRes.json();
      const statsData = await statsRes.json();
      
      setLogs(logsData.logs || []);
      setStats(statsData);
    } catch (error) {
      toast.error('Failed to load notification data');
    } finally {
      setLoading(false);
    }
  };

  const handleSendNotification = async (e) => {
    e.preventDefault();
    setSending(true);
    
    try {
      const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/notifications/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(notificationForm)
      });
      
      const data = await res.json();
      
      if (res.ok) {
        if (data.delivered === 0 && data.registered_devices === 0) {
          toast.warning(`No users have push notifications enabled. ${data.total_users} users found but 0 have registered devices.`);
        } else if (data.delivered === 0) {
          toast.warning(`Notification not delivered. ${data.registered_devices} users have notifications enabled but delivery failed.`);
        } else {
          toast.success(`Notification sent to ${data.delivered} of ${data.total_users} users!`);
        }
        setSendOpen(false);
        setNotificationForm({ title: '', body: '', target: 'all' });
        loadData();
      } else {
        toast.error(data.detail || 'Failed to send notification');
      }
    } catch (error) {
      toast.error('Failed to send notification');
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button onClick={() => navigate('/admin')} variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          <h1 className="text-3xl font-bold text-slate-900 font-['Space_Grotesk']">Push Notifications</h1>
        </div>
        
        <Dialog open={sendOpen} onOpenChange={setSendOpen}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-to-r from-teal-500 to-teal-600">
              <Send className="w-4 h-4 mr-2" />
              Send Notification
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Send Manual Notification</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSendNotification} className="space-y-4">
              <div>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  value={notificationForm.title}
                  onChange={(e) => setNotificationForm({...notificationForm, title: e.target.value})}
                  placeholder="e.g., New Feature Available!"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="body">Message</Label>
                <textarea
                  id="body"
                  value={notificationForm.body}
                  onChange={(e) => setNotificationForm({...notificationForm, body: e.target.value})}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  rows={3}
                  placeholder="e.g., Check out our new quiz categories!"
                  required
                />
              </div>

              <div>
                <Label htmlFor="target">Send To</Label>
                <select
                  id="target"
                  value={notificationForm.target}
                  onChange={(e) => setNotificationForm({...notificationForm, target: e.target.value})}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                >
                  <option value="all">All Users</option>
                  <option value="active">Active Users (last 7 days)</option>
                </select>
              </div>

              <Button type="submit" disabled={sending} className="w-full">
                {sending ? 'Sending...' : 'Send Notification'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center space-x-3 mb-2">
              <Bell className="w-6 h-6 text-teal-600" />
              <h3 className="font-semibold text-slate-700">Total Sent</h3>
            </div>
            <p className="text-3xl font-bold text-slate-900 font-['Azeret_Mono']">{stats.total_sent}</p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center space-x-3 mb-2">
              <Users className="w-6 h-6 text-emerald-600" />
              <h3 className="font-semibold text-slate-700">Delivered</h3>
            </div>
            <p className="text-3xl font-bold text-emerald-600 font-['Azeret_Mono']">
              {stats.stats_by_type.reduce((sum, s) => sum + (s.total_delivered || 0), 0)}
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-slate-200">
            <div className="flex items-center space-x-3 mb-2">
              <TrendingUp className="w-6 h-6 text-teal-600" />
              <h3 className="font-semibold text-slate-700">Delivery Rate</h3>
            </div>
            <p className="text-3xl font-bold text-teal-600 font-['Azeret_Mono']">
              {stats.total_sent > 0 ? (
                ((stats.stats_by_type.reduce((sum, s) => sum + (s.total_delivered || 0), 0) / stats.total_sent) * 100).toFixed(0)
              ) : 0}%
            </p>
          </div>
        </div>
      )}

      {/* Recent Logs */}
      <div className="bg-white rounded-xl p-6 border border-slate-200">
        <h2 className="text-xl font-bold text-slate-900 mb-4 font-['Space_Grotesk']">Recent Notifications</h2>
        
        {logs.length === 0 ? (
          <div className="text-center py-8 text-slate-600">
            <Bell className="w-12 h-12 text-slate-300 mx-auto mb-2" />
            <p>No notifications sent yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {logs.slice(0, 20).map((log) => (
              <div key={log._id} className="flex items-start justify-between p-4 bg-slate-50 rounded-lg border border-slate-200">
                <div className="flex-1">
                  <p className="font-semibold text-slate-900">{log.title}</p>
                  <p className="text-sm text-slate-600 mt-1">{log.body}</p>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-slate-500">
                    <span>To: {log.user_nickname}</span>
                    <span>Type: {log.type}</span>
                    <span>Sent: {new Date(log.sent_at).toLocaleString()}</span>
                  </div>
                </div>
                <div className="text-right ml-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    log.delivered_count > 0 
                      ? 'bg-emerald-100 text-emerald-700' 
                      : 'bg-rose-100 text-rose-700'
                  }`}>
                    {log.delivered_count > 0 ? 'Delivered' : 'Failed'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Setup Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="font-bold text-blue-900 mb-3">✅ Firebase Connected!</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p>Your Firebase project <strong>socraquest</strong> is now integrated.</p>
          <p><strong>What's Working:</strong></p>
          <ul className="list-disc list-inside ml-4 space-y-1">
            <li>Manual notifications (send to all/active users)</li>
            <li>Firebase Cloud Messaging ready</li>
            <li>Notification logging & analytics</li>
            <li>User preference management</li>
          </ul>
          <p className="mt-3"><strong>To enable automatic notifications:</strong></p>
          <ul className="list-decimal list-inside ml-4 space-y-1">
            <li>Set up cron jobs for daily reminders</li>
            <li>Enable streak tracking</li>
            <li>Configure time-based triggers</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
