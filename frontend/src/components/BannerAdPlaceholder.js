import React from 'react';

export function BannerAdPlaceholder() {
  return (
    <div 
      className="w-full h-16 bg-slate-200 border border-slate-300 rounded-lg flex items-center justify-center"
      data-testid="banner-ad"
    >
      <span className="text-xs text-slate-500 font-medium">Banner Ad Placeholder</span>
    </div>
  );
}
