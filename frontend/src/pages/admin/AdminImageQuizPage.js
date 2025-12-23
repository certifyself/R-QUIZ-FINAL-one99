import React, { useState, useEffect, useRef } from 'react';
import { adminAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../components/ui/dialog';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Plus, Edit2, Trash2, Image, Upload, Link, X, CheckCircle2, FileSpreadsheet, Download, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

export function AdminImageQuizPage() {
  const [questions, setQuestions] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [bulkUploadOpen, setBulkUploadOpen] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [bulkUploading, setBulkUploading] = useState(false);
  const fileInputRef = useRef(null);
  const bulkFileInputRef = useRef(null);
  
  const [formData, setFormData] = useState({
    topic_id: '',
    text_en: '',
    text_sk: '',
    image_url: '',
    options: [
      { key: 'A', label_en: '', label_sk: '' },
      { key: 'B', label_en: '', label_sk: '' },
      { key: 'C', label_en: '', label_sk: '' },
      { key: 'D', label_en: '', label_sk: '' }
    ],
    correct_key: 'A',
    active: true
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [questionsRes, topicsRes] = await Promise.all([
        adminAPI.getQuestions(),
        adminAPI.getTopics()
      ]);
      // Filter to show only questions with images
      const imageQuestions = questionsRes.data.questions.filter(q => q.image_url);
      setQuestions(imageQuestions);
      setTopics(topicsRes.data.topics);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      topic_id: '',
      text_en: '',
      text_sk: '',
      image_url: '',
      options: [
        { key: 'A', label_en: '', label_sk: '' },
        { key: 'B', label_en: '', label_sk: '' },
        { key: 'C', label_en: '', label_sk: '' },
        { key: 'D', label_en: '', label_sk: '' }
      ],
      correct_key: 'A',
      active: true
    });
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setUploading(true);
    try {
      const formDataUpload = new FormData();
      formDataUpload.append('file', file);
      
      const response = await adminAPI.uploadImage(formDataUpload);
      const imageUrl = response.data.image_url;
      
      // Convert to full URL
      const fullUrl = `${window.location.origin}${imageUrl}`;
      setFormData(prev => ({ ...prev, image_url: fullUrl }));
      toast.success('Image uploaded successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    
    if (!formData.image_url) {
      toast.error('Please add an image URL or upload an image');
      return;
    }
    
    setSubmitting(true);
    try {
      // Transform form data to match API format
      const apiData = {
        topic_id: formData.topic_id,
        text: {
          en: formData.text_en,
          sk: formData.text_sk || formData.text_en
        },
        options: formData.options.map(opt => ({
          key: opt.key,
          label: {
            en: opt.label_en,
            sk: opt.label_sk || opt.label_en
          }
        })),
        correct_key: formData.correct_key,
        image_url: formData.image_url,
        active: formData.active
      };
      
      await adminAPI.createQuestion(apiData);
      toast.success('Image question created successfully!');
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
      const apiData = {
        topic_id: formData.topic_id,
        text: {
          en: formData.text_en,
          sk: formData.text_sk || formData.text_en
        },
        options: formData.options.map(opt => ({
          key: opt.key,
          label: {
            en: opt.label_en,
            sk: opt.label_sk || opt.label_en
          }
        })),
        correct_key: formData.correct_key,
        image_url: formData.image_url,
        active: formData.active
      };
      
      await adminAPI.updateQuestion(selectedQuestion._id, apiData);
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
    if (!window.confirm('Are you sure you want to delete this question?')) return;
    
    try {
      await adminAPI.deleteQuestion(questionId);
      toast.success('Question deleted');
      loadData();
    } catch (error) {
      toast.error('Failed to delete question');
    }
  };

  const openEditDialog = (question) => {
    setSelectedQuestion(question);
    
    // Extract text based on structure
    const textEn = typeof question.text === 'object' ? question.text.en : question.text;
    const textSk = typeof question.text === 'object' ? question.text.sk : question.text;
    
    setFormData({
      topic_id: question.topic_id,
      text_en: textEn || '',
      text_sk: textSk || '',
      image_url: question.image_url || '',
      options: question.options.map(opt => ({
        key: opt.key,
        label_en: typeof opt.label === 'object' ? opt.label.en : opt.label,
        label_sk: typeof opt.label === 'object' ? opt.label.sk : opt.label
      })),
      correct_key: question.correct_key,
      active: question.active !== false
    });
    setEditOpen(true);
  };

  const handleDownloadTemplate = async () => {
    try {
      await adminAPI.downloadImageQuizTemplate();
      toast.success('Template downloaded!');
    } catch (error) {
      toast.error('Failed to download template');
    }
  };

  const handleBulkUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setBulkUploading(true);
    toast.info('Uploading and generating images... This may take a few minutes.');
    
    try {
      const response = await adminAPI.bulkUploadImageQuiz(file);
      const { imported, errors } = response.data;
      
      if (imported > 0) {
        toast.success(`Successfully imported ${imported} image quiz questions with AI-generated images!`);
      }
      
      if (errors && errors.length > 0) {
        errors.slice(0, 3).forEach(err => toast.error(err));
        if (errors.length > 3) {
          toast.warning(`...and ${errors.length - 3} more errors`);
        }
      }
      
      setBulkUploadOpen(false);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Bulk upload failed');
    } finally {
      setBulkUploading(false);
      if (bulkFileInputRef.current) {
        bulkFileInputRef.current.value = '';
      }
    }
  };

  const QuestionForm = ({ onSubmit, submitText }) => (
    <form onSubmit={onSubmit} className="space-y-6">
      {/* Topic Selection */}
      <div>
        <Label>Topic *</Label>
        <select
          value={formData.topic_id}
          onChange={(e) => setFormData({ ...formData, topic_id: e.target.value })}
          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
          required
        >
          <option value="">Select a topic</option>
          {topics.map((topic) => (
            <option key={topic._id} value={topic._id}>
              {topic.name} ({topic.name_sk || topic.name})
            </option>
          ))}
        </select>
      </div>

      {/* Image Section */}
      <div className="space-y-3">
        <Label className="flex items-center space-x-2">
          <Image className="w-4 h-4" />
          <span>Question Image *</span>
        </Label>
        
        {/* Image Preview */}
        {formData.image_url && (
          <div className="relative inline-block">
            <img 
              src={formData.image_url} 
              alt="Question" 
              className="max-w-full max-h-48 rounded-lg border border-slate-200"
            />
            <button
              type="button"
              onClick={() => setFormData({ ...formData, image_url: '' })}
              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
        
        {/* Image URL Input */}
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <Link className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              type="url"
              placeholder="Paste image URL here..."
              value={formData.image_url}
              onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
              className="pl-10"
            />
          </div>
          <span className="text-slate-400 self-center">or</span>
          <div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageUpload}
              accept="image/*"
              className="hidden"
            />
            <Button
              type="button"
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="border-teal-300 text-teal-700 hover:bg-teal-50"
            >
              {uploading ? (
                <>
                  <LoadingSpinner className="w-4 h-4 mr-2" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Upload
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Question Text */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Question Text (English) *</Label>
          <Input
            value={formData.text_en}
            onChange={(e) => setFormData({ ...formData, text_en: e.target.value })}
            placeholder="What is shown in this image?"
            required
          />
        </div>
        <div>
          <Label>Question Text (Slovak)</Label>
          <Input
            value={formData.text_sk}
            onChange={(e) => setFormData({ ...formData, text_sk: e.target.value })}
            placeholder="Čo je zobrazené na tomto obrázku?"
          />
        </div>
      </div>

      {/* Answer Options */}
      <div className="space-y-3">
        <Label>Answer Options</Label>
        {formData.options.map((option, idx) => (
          <div key={option.key} className="flex items-center space-x-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
              formData.correct_key === option.key 
                ? 'bg-teal-500 text-white' 
                : 'bg-slate-200 text-slate-700'
            }`}>
              {option.key}
            </div>
            <div className="flex-1 grid grid-cols-2 gap-2">
              <Input
                placeholder={`Option ${option.key} (English)`}
                value={option.label_en}
                onChange={(e) => {
                  const newOptions = [...formData.options];
                  newOptions[idx].label_en = e.target.value;
                  setFormData({ ...formData, options: newOptions });
                }}
                required
              />
              <Input
                placeholder={`Option ${option.key} (Slovak)`}
                value={option.label_sk}
                onChange={(e) => {
                  const newOptions = [...formData.options];
                  newOptions[idx].label_sk = e.target.value;
                  setFormData({ ...formData, options: newOptions });
                }}
              />
            </div>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, correct_key: option.key })}
              className={`p-2 rounded-lg transition-colors ${
                formData.correct_key === option.key
                  ? 'bg-teal-100 text-teal-700'
                  : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
              }`}
              title="Mark as correct answer"
            >
              <CheckCircle2 className="w-5 h-5" />
            </button>
          </div>
        ))}
      </div>

      {/* Submit */}
      <div className="flex justify-end space-x-3 pt-4 border-t">
        <Button type="submit" disabled={submitting} className="bg-gradient-to-r from-teal-500 to-teal-600">
          {submitting ? 'Saving...' : submitText}
        </Button>
      </div>
    </form>
  );

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 font-['Space_Grotesk']">Image Quiz Questions</h1>
          <p className="text-slate-600 mt-1">Create and manage questions with AI-generated images</p>
        </div>
        <div className="flex space-x-2">
          <Button 
            onClick={() => setBulkUploadOpen(true)}
            variant="outline"
            className="border-teal-300 text-teal-700 hover:bg-teal-50"
            data-testid="bulk-upload-btn"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            Bulk Upload (AI Images)
          </Button>
          <Button 
            onClick={() => { resetForm(); setCreateOpen(true); }}
            className="bg-gradient-to-r from-teal-500 to-teal-600"
            data-testid="create-image-question-btn"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Question
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <p className="text-sm text-slate-600">Total Image Questions</p>
          <p className="text-2xl font-bold text-slate-900">{questions.length}</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <p className="text-sm text-slate-600">Active</p>
          <p className="text-2xl font-bold text-teal-600">{questions.filter(q => q.active !== false).length}</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-200">
          <p className="text-sm text-slate-600">Topics</p>
          <p className="text-2xl font-bold text-slate-900">{topics.length}</p>
        </div>
      </div>

      {/* Questions Grid */}
      {questions.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border border-slate-200">
          <Image className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No Image Questions Yet</h3>
          <p className="text-slate-600 mb-4">Upload an Excel file to auto-generate images with AI, or create questions manually.</p>
          <div className="flex justify-center space-x-3">
            <Button onClick={() => setBulkUploadOpen(true)} variant="outline" className="border-teal-300 text-teal-700">
              <Sparkles className="w-4 h-4 mr-2" />
              Bulk Upload (AI)
            </Button>
            <Button onClick={() => { resetForm(); setCreateOpen(true); }} className="bg-gradient-to-r from-teal-500 to-teal-600">
              <Plus className="w-4 h-4 mr-2" />
              Add Manually
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {questions.map((question) => {
            const topic = topics.find(t => t._id === question.topic_id);
            const questionText = typeof question.text === 'object' ? question.text.en : question.text;
            
            return (
              <div 
                key={question._id} 
                className="bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow"
                data-testid={`image-question-${question._id}`}
              >
                {/* Image */}
                <div className="aspect-video bg-slate-100 relative">
                  {question.image_url ? (
                    <img 
                      src={question.image_url} 
                      alt="Question" 
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Image className="w-12 h-12 text-slate-300" />
                    </div>
                  )}
                  {question.active === false && (
                    <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded">
                      Inactive
                    </div>
                  )}
                </div>
                
                {/* Content */}
                <div className="p-4">
                  <p className="text-sm text-teal-600 font-medium mb-1">{topic?.name || 'Unknown Topic'}</p>
                  <p className="text-slate-900 font-medium line-clamp-2 mb-3">{questionText}</p>
                  
                  {/* Options Preview */}
                  <div className="grid grid-cols-2 gap-1 text-xs mb-3">
                    {question.options.slice(0, 4).map(opt => {
                      const label = typeof opt.label === 'object' ? opt.label.en : opt.label;
                      return (
                        <div 
                          key={opt.key}
                          className={`px-2 py-1 rounded ${
                            opt.key === question.correct_key
                              ? 'bg-teal-100 text-teal-800'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {opt.key}: {label?.substring(0, 15)}{label?.length > 15 ? '...' : ''}
                        </div>
                      );
                    })}
                  </div>
                  
                  {/* Actions */}
                  <div className="flex justify-end space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => openEditDialog(question)}
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-red-600 hover:bg-red-50"
                      onClick={() => handleDelete(question._id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Image className="w-5 h-5 text-teal-600" />
              <span>Create Image Question</span>
            </DialogTitle>
          </DialogHeader>
          <QuestionForm onSubmit={handleCreate} submitText="Create Question" />
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Edit2 className="w-5 h-5 text-teal-600" />
              <span>Edit Image Question</span>
            </DialogTitle>
          </DialogHeader>
          <QuestionForm onSubmit={handleEdit} submitText="Update Question" />
        </DialogContent>
      </Dialog>
    </div>
  );
}
