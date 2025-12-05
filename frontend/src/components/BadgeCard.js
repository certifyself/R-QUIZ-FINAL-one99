import React from 'react';
import {
  Trophy, Crown, Flame, Award, Zap, Gift, Sparkles,
  Sunrise, Moon, Star
} from 'lucide-react';

const iconMap = {
  Trophy, Crown, Flame, Award, Zap, Gift, Sparkles,
  Sunrise, Moon, Star
};

export function BadgeCard({ badge, locked = false, size = 'md' }) {
  const Icon = iconMap[badge.icon] || Award;
  
  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32'
  };
  
  const iconSizes = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };
  
  return (
    <div
      className={`relative flex flex-col items-center p-4 rounded-xl transition-all ${
        locked 
          ? 'bg-slate-100 opacity-60' 
          : 'bg-gradient-to-br from-white to-slate-50 border-2 shadow-lg'
      }`}
      style={{
        borderColor: locked ? '#e2e8f0' : badge.color
      }}
    >
      {/* Badge Icon */}
      <div
        className={`${sizeClasses[size]} rounded-full flex items-center justify-center mb-3 ${
          locked ? 'bg-slate-200' : 'bg-gradient-to-br'
        }`}
        style={{
          backgroundColor: locked ? undefined : `${badge.color}20`,
          borderWidth: '3px',
          borderColor: locked ? '#cbd5e1' : badge.color
        }}
      >
        <Icon 
          className={iconSizes[size]}
          style={{ color: locked ? '#94a3b8' : badge.color }}
        />
      </div>
      
      {/* Badge Name */}
      <h3 className={`font-bold text-center ${
        size === 'sm' ? 'text-sm' : size === 'md' ? 'text-base' : 'text-lg'
      } ${locked ? 'text-slate-500' : 'text-slate-900'}`}>
        {badge.name.en}
      </h3>
      
      {/* Badge Description */}
      <p className={`text-center mt-1 ${
        size === 'sm' ? 'text-xs' : 'text-sm'
      } ${locked ? 'text-slate-400' : 'text-slate-600'}`}>
        {badge.description.en}
      </p>
      
      {/* Locked Overlay */}
      {locked && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-4xl opacity-30">🔒</div>
        </div>
      )}
      
      {/* Earned Date */}
      {!locked && badge.earned_at && (
        <p className="text-xs text-slate-500 mt-2">
          Earned {new Date(badge.earned_at).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}
