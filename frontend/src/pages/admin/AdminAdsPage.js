import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { ArrowLeft, Save, Video, Image as ImageIcon } from 'lucide-react';
import { toast } from 'sonner';

export function AdminAdsPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [manualAds, setManualAds] = useState([]);
  const [createAdOpen, setCreateAdOpen] = useState(false);
  const [adForm, setAdForm] = useState({
    name: '',
    type: 'banner',
    image_url: '',
    video_url: '',
    click_url: '',
    active: true
  });
  
  const [config, setConfig] = useState({
    google_adsense: {
      enabled: false,
      client_id: '',
      banner_slot_id: '',
      video_slot_id: ''
    },
    taboola: {
      enabled: false,
      publisher_id: '',
      placement_name: ''
    }
  });

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const [configRes, adsRes] = await Promise.all([
        adminAPI.getAdConfig(),
        adminAPI.getManualAds()
      ]);
      setConfig(configRes.data);
      setManualAds(adsRes.data.ads || []);
    } catch (error) {
      toast.error('Failed to load ad configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await adminAPI.updateAdConfig(config);
      toast.success('Ad configuration saved successfully!');
    } catch (error) {
      toast.error('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const updateGoogleAdsense = (field, value) => {
    setConfig(prev => ({
      ...prev,
      google_adsense: {
        ...prev.google_adsense,
        [field]: value
      }
    }));
  };

  const updateTaboola = (field, value) => {
    setConfig(prev => ({
      ...prev,
      taboola: {
        ...prev.taboola,
        [field]: value
      }
    }));
  };

  const handleCreateAd = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await adminAPI.createManualAd(adForm);
      toast.success('Manual ad created successfully!');
      setCreateAdOpen(false);
      setAdForm({
        name: '',
        type: 'banner',
        image_url: '',
        video_url: '',
        click_url: '',
        active: true
      });
      loadConfig();
    } catch (error) {
      toast.error('Failed to create ad');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAd = async (adId) => {
    if (!window.confirm('Are you sure you want to delete this ad?')) return;
    
    try {
      await adminAPI.deleteManualAd(adId);
      toast.success('Ad deleted successfully!');
      loadConfig();
    } catch (error) {
      toast.error('Failed to delete ad');
    }
  };

  const toggleAdStatus = async (ad) => {
    try {
      await adminAPI.updateManualAd(ad._id, { ...ad, active: !ad.active });
      toast.success(`Ad ${!ad.active ? 'activated' : 'deactivated'}!`);
      loadConfig();
    } catch (error) {
      toast.error('Failed to update ad');
    }
  };

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button onClick={() => navigate('/admin')} variant="ghost" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          <h1 className="text-3xl font-bold text-slate-900 font-['Space_Grotesk']">Ads Placement</h1>
        </div>
        
        <Button 
          onClick={handleSave} 
          disabled={saving}
          className="bg-gradient-to-r from-teal-500 to-teal-600"
          data-testid="save-ads-config"
        >
          <Save className="w-4 h-4 mr-2" />
          {saving ? 'Saving...' : 'Save Configuration'}
        </Button>
      </div>

      {/* Google AdSense */}
      <div className="bg-white rounded-xl p-6 border border-slate-200">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <ImageIcon className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 font-['Space_Grotesk']">Google AdSense</h2>
              <p className="text-sm text-slate-600">Banner ads and video ads</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={config.google_adsense.enabled}
              onChange={(e) => updateGoogleAdsense('enabled', e.target.checked)}
              className="w-5 h-5 text-teal-600 border-gray-300 rounded"
              id="google-enabled"
            />
            <Label htmlFor="google-enabled" className="font-semibold">
              {config.google_adsense.enabled ? 'Enabled' : 'Disabled'}
            </Label>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="google-client">Client ID (ca-pub-XXXXXXXXXXXXXXXX)</Label>
            <Input
              id="google-client"
              value={config.google_adsense.client_id}
              onChange={(e) => updateGoogleAdsense('client_id', e.target.value)}
              placeholder="ca-pub-1234567890123456"
              className="font-mono"
            />
            <p className="text-xs text-slate-500 mt-1">Get this from Google AdSense dashboard</p>
          </div>

          <div>
            <Label htmlFor="banner-slot">Banner Ad Slot ID</Label>
            <Input
              id="banner-slot"
              value={config.google_adsense.banner_slot_id}
              onChange={(e) => updateGoogleAdsense('banner_slot_id', e.target.value)}
              placeholder="1234567890"
              className="font-mono"
            />
            <p className="text-xs text-slate-500 mt-1">For quiz page banner ads</p>
          </div>

          <div>
            <Label htmlFor="video-slot">Rewarded Video Ad Slot ID</Label>
            <Input
              id="video-slot"
              value={config.google_adsense.video_slot_id}
              onChange={(e) => updateGoogleAdsense('video_slot_id', e.target.value)}
              placeholder="9876543210"
              className="font-mono"
            />
            <p className="text-xs text-slate-500 mt-1">For attempt 2 & 3 countdown gates</p>
          </div>
        </div>
      </div>

      {/* Taboola */}
      <div className="bg-white rounded-xl p-6 border border-slate-200">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Video className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 font-['Space_Grotesk']">Taboola</h2>
              <p className="text-sm text-slate-600">Content recommendation ads</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={config.taboola.enabled}
              onChange={(e) => updateTaboola('enabled', e.target.checked)}
              className="w-5 h-5 text-teal-600 border-gray-300 rounded"
              id="taboola-enabled"
            />
            <Label htmlFor="taboola-enabled" className="font-semibold">
              {config.taboola.enabled ? 'Enabled' : 'Disabled'}
            </Label>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="taboola-publisher">Publisher ID</Label>
            <Input
              id="taboola-publisher"
              value={config.taboola.publisher_id}
              onChange={(e) => updateTaboola('publisher_id', e.target.value)}
              placeholder="your-publisher-id"
              className="font-mono"
            />
            <p className="text-xs text-slate-500 mt-1">Get this from Taboola dashboard</p>
          </div>

          <div>
            <Label htmlFor="taboola-placement">Placement Name</Label>
            <Input
              id="taboola-placement"
              value={config.taboola.placement_name}
              onChange={(e) => updateTaboola('placement_name', e.target.value)}
              placeholder="Below Article Thumbnails"
              className="font-mono"
            />
            <p className="text-xs text-slate-500 mt-1">Widget placement identifier</p>
          </div>
        </div>
      </div>

      {/* Manual Ads Management */}
      <div className="bg-white rounded-xl p-6 border border-slate-200">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-slate-900 font-['Space_Grotesk']">Manual Ads</h2>
          <Dialog open={createAdOpen} onOpenChange={setCreateAdOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-teal-500 to-teal-600">
                <Plus className="w-4 h-4 mr-2" />
                Create Ad
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Manual Ad</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateAd} className="space-y-4">
                <div>
                  <Label htmlFor="ad-name">Ad Name</Label>
                  <Input
                    id="ad-name"
                    value={adForm.name}
                    onChange={(e) => setAdForm({...adForm, name: e.target.value})}
                    placeholder="e.g., Summer Sale Banner"
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="ad-type">Ad Type</Label>
                  <select
                    id="ad-type"
                    value={adForm.type}
                    onChange={(e) => setAdForm({...adForm, type: e.target.value})}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  >
                    <option value="banner">Banner Ad (Image)</option>
                    <option value="video">Video Ad</option>
                  </select>
                </div>

                {adForm.type === 'banner' && (
                  <div>
                    <Label htmlFor="image-url">Image URL</Label>
                    <Input
                      id="image-url"
                      value={adForm.image_url}
                      onChange={(e) => setAdForm({...adForm, image_url: e.target.value})}
                      placeholder="https://example.com/ad-image.jpg"
                      required
                    />
                  </div>
                )}

                {adForm.type === 'video' && (
                  <div>
                    <Label htmlFor="video-url">Video URL</Label>
                    <Input
                      id="video-url"
                      value={adForm.video_url}
                      onChange={(e) => setAdForm({...adForm, video_url: e.target.value})}
                      placeholder="https://example.com/ad-video.mp4"
                      required
                    />
                  </div>
                )}

                <div>
                  <Label htmlFor="click-url">Click URL (Optional)</Label>
                  <Input
                    id="click-url"
                    value={adForm.click_url}
                    onChange={(e) => setAdForm({...adForm, click_url: e.target.value})}
                    placeholder="https://yourwebsite.com/promo"
                  />
                  <p className="text-xs text-slate-500 mt-1">Where users go when clicking the ad</p>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={adForm.active}
                    onChange={(e) => setAdForm({...adForm, active: e.target.checked})}
                    className="w-4 h-4 text-teal-600 border-gray-300 rounded"
                    id="ad-active"
                  />
                  <Label htmlFor="ad-active">Active</Label>
                </div>

                <Button type="submit" disabled={saving} className="w-full">
                  {saving ? 'Creating...' : 'Create Ad'}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Manual Ads List */}
        {manualAds.length === 0 ? (
          <div className="text-center py-8 text-slate-600">
            <ImageIcon className="w-12 h-12 text-slate-300 mx-auto mb-2" />
            <p>No manual ads yet. Create your first ad!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {manualAds.map((ad) => (
              <div key={ad._id} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200">
                <div className="flex items-center space-x-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    ad.type === 'banner' ? 'bg-blue-100' : 'bg-purple-100'
                  }`}>
                    {ad.type === 'banner' ? (
                      <ImageIcon className={`w-5 h-5 ${ad.type === 'banner' ? 'text-blue-600' : 'text-purple-600'}`} />
                    ) : (
                      <Video className="w-5 h-5 text-purple-600" />
                    )}
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900">{ad.name}</p>
                    <p className="text-xs text-slate-600">{ad.type === 'banner' ? 'Banner Ad' : 'Video Ad'}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleAdStatus(ad)}
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      ad.active 
                        ? 'bg-emerald-100 text-emerald-700' 
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {ad.active ? 'Active' : 'Inactive'}
                  </button>
                  <Button
                    onClick={() => handleDeleteAd(ad._id)}
                    variant="ghost"
                    size="sm"
                    className="text-rose-600 hover:text-rose-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="font-bold text-blue-900 mb-3">How to Set Up Ads:</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <div>
            <strong>Google AdSense:</strong>
            <ol className="list-decimal list-inside ml-4 mt-1 space-y-1">
              <li>Go to <a href="https://www.google.com/adsense" target="_blank" rel="noopener" className="underline">Google AdSense</a></li>
              <li>Create ad units for banner and video ads</li>
              <li>Copy Client ID and Slot IDs</li>
              <li>Paste above and enable</li>
            </ol>
          </div>
          <div className="mt-3">
            <strong>Taboola:</strong>
            <ol className="list-decimal list-inside ml-4 mt-1 space-y-1">
              <li>Go to <a href="https://www.taboola.com" target="_blank" rel="noopener" className="underline">Taboola</a></li>
              <li>Get your Publisher ID from dashboard</li>
              <li>Create placement widget</li>
              <li>Enter details above and enable</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
