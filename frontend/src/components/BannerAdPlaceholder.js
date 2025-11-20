import React, { useEffect, useState } from 'react';
import { userAPI } from '../lib/api';

export function BannerAdPlaceholder() {
  const [adConfig, setAdConfig] = useState(null);

  useEffect(() => {
    loadAdConfig();
  }, []);

  const loadAdConfig = async () => {
    try {
      const res = await userAPI.getAdsConfig();
      setAdConfig(res.data);
    } catch (error) {
      console.error('Failed to load ad config');
    }
  };

  useEffect(() => {
    if (adConfig?.google_adsense?.enabled && adConfig?.google_adsense?.banner_slot_id) {
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
  }, [adConfig]);

  // Show real Google Ad if configured
  if (adConfig?.google_adsense?.enabled && adConfig?.google_adsense?.banner_slot_id) {
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

  // Fallback to placeholder
  return (
    <div 
      className="w-full h-16 bg-slate-200 border border-slate-300 rounded-lg flex items-center justify-center"
      data-testid="banner-ad"
    >
      <span className="text-xs text-slate-500 font-medium">Banner Ad Placeholder (Configure in Admin → Ads)</span>
    </div>
  );
}
