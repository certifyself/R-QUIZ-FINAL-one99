import React, { useEffect, useState } from 'react';
import { userAPI } from '../lib/api';

export function BannerAdPlaceholder() {
  const [adConfig, setAdConfig] = useState(null);
  const [manualAds, setManualAds] = useState([]);
  const [currentAd, setCurrentAd] = useState(null);

  useEffect(() => {
    loadAdConfig();
    loadManualAds();
  }, []);

  const loadAdConfig = async () => {
    try {
      const res = await userAPI.getAdsConfig();
      setAdConfig(res.data);
    } catch (error) {
      console.error('Failed to load ad config');
    }
  };

  const loadManualAds = async () => {
    try {
      const res = await userAPI.getManualAds('banner');
      if (res.data.ads && res.data.ads.length > 0) {
        // Random manual ad
        const randomAd = res.data.ads[Math.floor(Math.random() * res.data.ads.length)];
        setCurrentAd(randomAd);
      }
      setManualAds(res.data.ads || []);
    } catch (error) {
      console.error('Failed to load manual ads');
    }
  };

  // Priority: Manual Ads > Google AdSense > Placeholder
  
  // 1. Manual Ad (highest priority)
  if (currentAd) {
    return (
      <div className="w-full" data-testid="banner-ad">
        {currentAd.click_url ? (
          <a href={currentAd.click_url} target="_blank" rel="noopener noreferrer">
            <img 
              src={currentAd.image_url} 
              alt={currentAd.name}
              className="w-full h-24 object-cover rounded-lg border border-slate-200"
              onError={(e) => { e.target.style.display = 'none'; }}
            />
          </a>
        ) : (
          <img 
            src={currentAd.image_url} 
            alt={currentAd.name}
            className="w-full h-24 object-cover rounded-lg border border-slate-200"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
        )}
      </div>
    );
  }

  useEffect(() => {
    if (adConfig?.google_adsense?.enabled && adConfig?.google_adsense?.banner_slot_id && !currentAd) {
      // Load Google AdSense script
      const script = document.createElement('script');
      script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';
      script.async = true;
      script.setAttribute('data-ad-client', adConfig.google_adsense.client_id);
      document.head.appendChild(script);

      // Initialize ad
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      } catch (e) {
        console.error('AdSense error:', e);
      }
    }
  }, [adConfig, currentAd]);

  // 2. Show real Google Ad if configured and no manual ads
  if (adConfig?.google_adsense?.enabled && adConfig?.google_adsense?.banner_slot_id && !currentAd) {
    return (
      <div className="w-full" data-testid="banner-ad">
        <ins
          className="adsbygoogle"
          style={{ display: 'block' }}
          data-ad-client={adConfig.google_adsense.client_id}
          data-ad-slot={adConfig.google_adsense.banner_slot_id}
          data-ad-format="auto"
          data-full-width-responsive="true"
        ></ins>
      </div>
    );
  }

  // 3. Fallback to placeholder
  return (
    <div 
      className="w-full h-16 bg-slate-200 border border-slate-300 rounded-lg flex items-center justify-center"
      data-testid="banner-ad"
    >
      <span className="text-xs text-slate-500 font-medium">Banner Ad Placeholder (Configure in Admin → Ads)</span>
    </div>
  );
}
