import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { adminAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Plus, Edit2, Trash2, ArrowLeft, CheckCircle2, XCircle } from 'lucide-react';
import { toast } from 'sonner';

export function AdminQuestionsPage() {
  const [searchParams] = useSearchParams();
  const topicFilter = searchParams.get('topic');
  const navigate = useNavigate();
  
  const [questions, setQuestions] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  
  const [formData, setFormData] = useState({
    topic_id: topicFilter || '',
    text: '',
    options: [
      { key: 'A', label: '' },
      { key: 'B', label: '' },
      { key: 'C', label: '' },
      { key: 'D', label: '' }
    ],
    correct_key: 'A',
    active: true
  });

  useEffect(() => {
    loadData();
  }, [topicFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [questionsRes, topicsRes] = await Promise.all([
        adminAPI.getQuestions(topicFilter),
        adminAPI.getTopics()
      ]);
      setQuestions(questionsRes.data.questions);
      setTopics(topicsRes.data.topics);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await adminAPI.createQuestion(formData);
      toast.success('Question created successfully!');
      setCreateOpen(false);
      resetForm();
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create question');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await adminAPI.updateQuestion(selectedQuestion._id, {
        text: formData.text,
        options: formData.options,
        correct_key: formData.correct_key,
        active: formData.active
      });
      toast.success('Question updated successfully!');
      setEditOpen(false);
      setSelectedQuestion(null);
      resetForm();
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update question');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (questionId) => {
    if (!window.confirm('Are you sure you want to delete this question?')) {
      return;
    }
    try {
      await adminAPI.deleteQuestion(questionId);
      toast.success('Question deleted successfully!');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete question');
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await adminAPI.downloadTemplate();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'questions_template.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Template downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download template');
    }
  };

  const handleBulkUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const res = await adminAPI.bulkUploadQuestions(file);
      toast.success(res.data.message);
      if (res.data.errors && res.data.errors.length > 0) {
        console.error('Upload errors:', res.data.errors);
        toast.warning(`${res.data.errors.length} rows had errors. Check console for details.`);
      }
      setUploadDialogOpen(false);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload file');
    } finally {
      setUploading(false);
      e.target.value = ''; // Reset file input
    }
  };

  const openEditDialog = (question) => {
    setSelectedQuestion(question);
    setFormData({
      topic_id: question.topic_id || '',
      text: question.text,
      options: question.options,
      correct_key: question.correct_key,
      active: question.active
    });
    setEditOpen(true);
  };

  const resetForm = () => {
    setFormData({
      topic_id: topicFilter || '',
      text: '',
      options: [
        { key: 'A', label: '' },
        { key: 'B', label: '' },
        { key: 'C', label: '' },
        { key: 'D', label: '' }
      ],
      correct_key: 'A',
      active: true
    });
  };

  const updateOption = (index, value) => {
    const newOptions = [...formData.options];
    newOptions[index].label = value;
    setFormData({ ...formData, options: newOptions });
  };

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button onClick={() => navigate('/admin/topics')} variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Topics
          </Button>
          <h1 className="text-3xl font-bold text-slate-900 font-['Space_Grotesk']">Manage Questions</h1>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button 
            onClick={handleDownloadTemplate} 
            variant="outline"
            data-testid="download-template-button"
          >
            Download Template
          </Button>
          
          <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" data-testid="bulk-upload-button">
                <Plus className="w-4 h-4 mr-2" />
                Bulk Upload
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Bulk Upload Questions</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <p className="text-sm text-slate-600">
                  Upload an Excel file with questions in both English and Slovak.
                </p>
                <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center">
                  <input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleBulkUpload}
                    className="hidden"
                    id="excel-upload"
                    disabled={uploading}
                  />
                  <label
                    htmlFor="excel-upload"
                    className="cursor-pointer inline-block"
                  >
                    <div className="text-slate-600">
                      <Plus className="w-12 h-12 mx-auto mb-2 text-slate-400" />
                      <p className="font-medium">
                        {uploading ? 'Uploading...' : 'Click to select Excel file'}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">.xlsx or .xls format</p>
                    </div>
                  </label>
                </div>
                <div className="bg-teal-50 border border-teal-200 rounded-lg p-3">
                  <p className="text-xs text-teal-800">
                    <strong>Tip:</strong> Download the template first to see the required format!
                  </p>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          
          <Dialog open={createOpen} onOpenChange={setCreateOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-teal-500 to-teal-600" data-testid="create-question-button">
                <Plus className="w-4 h-4 mr-2" />
                Create Question
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create New Question</DialogTitle>
              </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Label htmlFor="topic">Topic</Label>
                <select
                  id="topic"
                  value={formData.topic_id}
                  onChange={(e) => setFormData({ ...formData, topic_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  required
                >
                  <option value="">Select a topic</option>
                  {topics.filter(t => t.active).map(topic => (
                    <option key={topic._id} value={topic._id}>{topic.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <Label htmlFor="text">Question Text</Label>
                <textarea
                  id="text"
                  value={formData.text}
                  onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  rows={3}
                  required
                />
              </div>

              <div className="space-y-3">
                <Label>Answer Options</Label>
                {formData.options.map((option, index) => (
                  <div key={option.key} className="flex items-center space-x-2">
                    <span className="font-semibold w-8">{option.key}.</span>
                    <Input
                      value={option.label}
                      onChange={(e) => updateOption(index, e.target.value)}
                      placeholder={`Option ${option.key}`}
                      required
                    />
                  </div>
                ))}
              </div>

              <div>
                <Label htmlFor="correct">Correct Answer</Label>
                <select
                  id="correct"
                  value={formData.correct_key}
                  onChange={(e) => setFormData({ ...formData, correct_key: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                >
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                  <option value="D">D</option>
                </select>
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

              <Button type="submit" disabled={submitting} className="w-full">
                {submitting ? 'Creating...' : 'Create Question'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>
      </div>

      {/* Filter */}
      {topicFilter && (
        <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
          <p className="text-sm text-teal-800">
            Filtered by topic: <strong>{topics.find(t => t._id === topicFilter)?.name || 'Unknown'}</strong>
          </p>
        </div>
      )}

      {/* Questions List */}
      <div className="space-y-4">
        {questions.length === 0 ? (
          <div className="bg-white rounded-xl p-12 border border-slate-200 text-center">
            <p className="text-slate-600">No questions found. Create your first question to get started.</p>
          </div>
        ) : (
          questions.map((question) => {
            // Extract English text for display in admin panel
            const questionText = typeof question.text === 'object' ? question.text.en : question.text;
            
            return (
              <div key={question._id} className="bg-white rounded-xl p-6 border border-slate-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-xs font-medium px-2 py-1 bg-teal-100 text-teal-700 rounded">
                        {question.topic_name}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        question.active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {question.active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <p className="text-slate-900 font-medium">{questionText}</p>
                  </div>
                <div className="flex items-center space-x-2">
                  <Button
                    onClick={() => openEditDialog(question)}
                    variant="ghost"
                    size="sm"
                  >
                    <Edit2 className="w-4 h-4" />
                  </Button>
                  <Button
                    onClick={() => handleDelete(question._id)}
                    variant="ghost"
                    size="sm"
                    className="text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                {question.options.map((option) => {
                  // Extract English label for display
                  const optionLabel = typeof option.label === 'object' ? option.label.en : option.label;
                  
                  return (
                    <div
                      key={option.key}
                      className={`flex items-center space-x-3 p-3 rounded-lg ${
                        option.key === question.correct_key
                          ? 'bg-emerald-50 border border-emerald-200'
                          : 'bg-slate-50'
                      }`}
                    >
                      <span className="font-semibold text-slate-700">{option.key}.</span>
                      <span className="text-slate-700">{optionLabel}</span>
                      {option.key === question.correct_key && (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 ml-auto" />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Question</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEdit} className="space-y-4">
            <div>
              <Label htmlFor="edit-text">Question Text</Label>
              <textarea
                id="edit-text"
                value={formData.text}
                onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                rows={3}
                required
              />
            </div>

            <div className="space-y-3">
              <Label>Answer Options</Label>
              {formData.options.map((option, index) => (
                <div key={option.key} className="flex items-center space-x-2">
                  <span className="font-semibold w-8">{option.key}.</span>
                  <Input
                    value={option.label}
                    onChange={(e) => updateOption(index, e.target.value)}
                    required
                  />
                </div>
              ))}
            </div>

            <div>
              <Label htmlFor="edit-correct">Correct Answer</Label>
              <select
                id="edit-correct"
                value={formData.correct_key}
                onChange={(e) => setFormData({ ...formData, correct_key: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg"
              >
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
              </select>
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
              {submitting ? 'Updating...' : 'Update Question'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
