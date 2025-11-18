import React from 'react';
import { Loader2 } from 'lucide-react';

export function LoadingSpinner({ className = "" }) {
  return (
    <div className={`flex justify-center items-center ${className}`}>
      <Loader2 className="w-8 h-8 animate-spin text-teal-600" />
    </div>
  );
}

export function PageLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="text-center space-y-4">
        <Loader2 className="w-12 h-12 animate-spin text-teal-600 mx-auto" />
        <p className="text-sm text-slate-600">Loading...</p>
      </div>
    </div>
  );
}
