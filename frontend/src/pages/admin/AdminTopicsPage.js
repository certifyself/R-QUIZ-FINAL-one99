import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Plus, Edit2, Trash2, ArrowLeft, BookOpen, Upload, Download } from 'lucide-react';
import { toast } from 'sonner';

export function AdminTopicsPage() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [formData, setFormData] = useState({ name: '', active: true });
  const [submitting, setSubmitting] = useState(false);
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [deleting, setDeleting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    setLoading(true);
    try {
      const res = await adminAPI.getTopics();
      setTopics(res.data.topics);
    } catch (error) {
      toast.error('Failed to load topics');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await adminAPI.createTopic(formData);
      toast.success('Topic created successfully!');
      setCreateOpen(false);
      setFormData({ name: '', active: true });
      loadTopics();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create topic');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await adminAPI.updateTopic(selectedTopic._id, formData);
      toast.success('Topic updated successfully!');
      setEditOpen(false);
      setSelectedTopic(null);
      setFormData({ name: '', active: true });
      loadTopics();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update topic');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (topicId) => {
    if (!window.confirm('Are you sure you want to delete this topic? This will also delete all associated questions.')) {
      return;
    }
    try {
      await adminAPI.deleteTopic(topicId);
      toast.success('Topic deleted successfully!');
      loadTopics();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete topic');
    }
  };

  const toggleTopicSelection = (topicId) => {
    setSelectedTopics(prev => 
      prev.includes(topicId) 
        ? prev.filter(id => id !== topicId)
        : [...prev, topicId]
    );
  };

  const toggleSelectAll = () => {
    if (selectedTopics.length === topics.length) {
      setSelectedTopics([]);
    } else {
      setSelectedTopics(topics.map(t => t._id));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedTopics.length === 0) {
      toast.error('No topics selected');
      return;
    }

    if (!window.confirm(`Are you sure you want to delete ${selectedTopics.length} topic(s)? This will also delete all associated questions.`)) {
      return;
    }

    setDeleting(true);
    try {
      const res = await adminAPI.bulkDeleteTopics(selectedTopics);
      
      if (res.data.deleted_topics > 0) {
        toast.success(`Deleted ${res.data.deleted_topics} topic(s) and ${res.data.deleted_questions} question(s) successfully!`);
      }
      
      if (res.data.errors && res.data.errors.length > 0) {
        toast.error(`Failed to delete ${res.data.errors.length} topic(s).`);
      }
      
      setSelectedTopics([]);
      loadTopics();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete topics');
    } finally {
      setDeleting(false);
    }
  };

  const handleBulkActive = async () => {
    if (selectedTopics.length === 0) {
      toast.error('No topics selected');
      return;
    }

    setDeleting(true);
    try {
      const res = await adminAPI.bulkActivateTopics(selectedTopics);
      toast.success(`Activated ${res.data.updated_count} topic(s) successfully!`);
      setSelectedTopics([]);
      loadTopics();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to activate topics');
    } finally {
      setDeleting(false);
    }
  };

  const handleBulkInactive = async () => {
    if (selectedTopics.length === 0) {
      toast.error('No topics selected');
      return;
    }

    setDeleting(true);
    try {
      const res = await adminAPI.bulkDeactivateTopics(selectedTopics);
      toast.success(`Deactivated ${res.data.updated_count} topic(s) successfully!`);
      setSelectedTopics([]);
      loadTopics();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to deactivate topics');
    } finally {
      setDeleting(false);
    }
  };


  const handleDownloadTemplate = async () => {
    try {
      await adminAPI.downloadTemplate();
      toast.success('Template downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download template');
    }
  };

  const handleBulkUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      toast.error('Please select a file');
      return;
    }

    setUploading(true);
    try {
      const res = await adminAPI.bulkUploadQuestions(uploadFile);
      toast.success(res.data.message || `Imported ${res.data.imported} questions successfully!`);
      
      if (res.data.errors && res.data.errors.length > 0) {
        toast.warning(`${res.data.errors.length} rows had errors. Check console for details.`);
        console.error('Upload errors:', res.data.errors);
      }
      
      setUploadOpen(false);
      setUploadFile(null);
      loadTopics();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };


  const openEditDialog = (topic) => {
    setSelectedTopic(topic);
    setFormData({ name: topic.name, active: topic.active });
    setEditOpen(true);
  };

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button onClick={() => navigate('/admin')} variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-3xl font-bold text-slate-900 font-['Space_Grotesk']">Manage Topics</h1>
        </div>
        
        <div className="flex items-center space-x-2">
          {selectedTopics.length > 0 && (
            <>
              <Button 
                onClick={handleBulkActive}
                disabled={deleting}
                variant="outline"
                className="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
                data-testid="bulk-active-button"
              >
                {deleting ? 'Processing...' : `Activate ${selectedTopics.length}`}
              </Button>
              
              <Button 
                onClick={handleBulkInactive}
                disabled={deleting}
                variant="outline"
                className="border-amber-300 text-amber-700 hover:bg-amber-50"
                data-testid="bulk-inactive-button"
              >
                {deleting ? 'Processing...' : `Deactivate ${selectedTopics.length}`}
              </Button>
              
              <Button 
                onClick={handleBulkDelete}
                disabled={deleting}
                variant="outline"
                className="border-rose-300 text-rose-700 hover:bg-rose-50"
                data-testid="bulk-delete-button"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                {deleting ? 'Deleting...' : `Delete ${selectedTopics.length}`}
              </Button>
            </>
          )}
          
          {/* Bulk Upload Button */}
          <Dialog open={uploadOpen} onOpenChange={setUploadOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="border-violet-300 text-violet-700 hover:bg-violet-50" data-testid="bulk-upload-button">
                <Upload className="w-4 h-4 mr-2" />
                Bulk Upload
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Bulk Upload Questions</DialogTitle>
              </DialogHeader>
              
              {/* Download Template Button */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900 mb-2 font-medium">Need the template?</p>
                <Button 
                  type="button"
                  onClick={handleDownloadTemplate}
                  variant="outline"
                  className="w-full border-blue-300 text-blue-700 hover:bg-blue-100"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Excel Template
                </Button>
              </div>
              
              <form onSubmit={handleBulkUpload} className="space-y-4">
                <div className="space-y-2">
                  <Label>Excel File</Label>
                  <Input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={(e) => setUploadFile(e.target.files[0])}
                    required
                  />
                  <p className="text-xs text-slate-500">
                    Upload an Excel file with columns: topic_sk, topic_en, question_sk, question_en, a_sk, a_en, b_sk, b_en, c_sk, c_en, d_sk, d_en, correct, image
                  </p>
                </div>
                <Button type="submit" disabled={uploading} className="w-full bg-gradient-to-r from-teal-500 to-teal-600">
                  {uploading ? 'Uploading...' : 'Upload Questions'}
                </Button>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-teal-500 to-teal-600" data-testid="create-topic-button">
                <Plus className="w-4 h-4 mr-2" />
                Create Topic
              </Button>
            </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Topic</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Label htmlFor="name">Topic Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Science"
                  required
                  data-testid="topic-name-input"
                />
              </div>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="active"
                  checked={formData.active}
                  onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                  className="w-4 h-4 text-teal-600 border-gray-300 rounded"
                />
                <Label htmlFor="active">Active</Label>
              </div>
              <Button type="submit" disabled={submitting} className="w-full" data-testid="submit-topic">
                {submitting ? 'Creating...' : 'Create Topic'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
        </div>
      </div>

      {/* Topics List */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        {topics.length === 0 ? (
          <div className="p-12 text-center">
            <BookOpen className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">No topics yet. Create your first topic to get started.</p>
          </div>
        ) : (
          <div>
            {/* Select All Header */}
            <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center space-x-3">
              <input
                type="checkbox"
                checked={selectedTopics.length === topics.length && topics.length > 0}
                onChange={toggleSelectAll}
                className="w-5 h-5 text-teal-600 border-gray-300 rounded"
              />
              <span className="text-sm font-medium text-slate-700">
                {selectedTopics.length > 0 ? `${selectedTopics.length} selected` : 'Select All'}
              </span>
            </div>
            
            {/* Topics */}
            <div className="divide-y divide-slate-200">
              {topics.map((topic) => (
                <div key={topic._id} className="p-4 flex items-center space-x-4 hover:bg-slate-50">
                  <input
                    type="checkbox"
                    checked={selectedTopics.includes(topic._id)}
                    onChange={() => toggleTopicSelection(topic._id)}
                    className="w-5 h-5 text-teal-600 border-gray-300 rounded"
                  />
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h3 className="font-semibold text-slate-900 text-lg">{topic.name}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        topic.active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {topic.active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 mt-1">
                      {topic.question_count || 0} questions
                    </p>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      onClick={() => navigate(`/admin/questions?topic=${topic._id}`)}
                      variant="outline"
                      size="sm"
                    >
                      <BookOpen className="w-4 h-4 mr-2" />
                      Questions
                    </Button>
                    <Button
                      onClick={() => openEditDialog(topic)}
                      variant="ghost"
                      size="sm"
                      data-testid={`edit-topic-${topic._id}`}
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button
                      onClick={() => handleDelete(topic._id)}
                      variant="ghost"
                      size="sm"
                      className="text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                      data-testid={`delete-topic-${topic._id}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Topic</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEdit} className="space-y-4">
            <div>
              <Label htmlFor="edit-name">Topic Name</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="edit-active"
                checked={formData.active}
                onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                className="w-4 h-4 text-teal-600 border-gray-300 rounded"
              />
              <Label htmlFor="edit-active">Active</Label>
            </div>
            <Button type="submit" disabled={submitting} className="w-full">
              {submitting ? 'Updating...' : 'Update Topic'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}