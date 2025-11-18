import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';

export function RewardedGate({ seconds = 15, onFinish, children }) {
  const [countdown, setCountdown] = useState(seconds);
  const [canContinue, setCanContinue] = useState(false);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setCanContinue(true);
    }
  }, [countdown]);

  if (canContinue && !children) {
    onFinish();
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black/75 flex items-center justify-center z-50 p-4" data-testid="rewarded-gate">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full text-center space-y-6">
        <div className="w-24 h-24 mx-auto bg-gradient-to-br from-teal-500 to-teal-600 rounded-full flex items-center justify-center">
          <span className="text-4xl font-bold text-white font-['Azeret_Mono']">{countdown}</span>
        </div>
        
        <div className="space-y-2">
          <h3 className="text-xl font-bold text-slate-900 font-['Space_Grotesk']">Ad Break</h3>
          <p className="text-sm text-slate-600">
            {canContinue ? 'Ready to continue!' : `Please wait ${countdown} seconds...`}
          </p>
        </div>

        <div className="bg-slate-100 border border-slate-200 rounded-lg p-6">
          <p className="text-xs text-slate-500">Rewarded Video Ad Placeholder</p>
        </div>

        {canContinue && (
          <Button 
            onClick={onFinish} 
            className="w-full bg-gradient-to-r from-teal-500 to-teal-600"
            data-testid="continue-button"
          >
            Continue
          </Button>
        )}
      </div>
    </div>
  );
}
