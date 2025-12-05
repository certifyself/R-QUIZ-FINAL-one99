import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Trophy, Crown, Flame, Award, Zap, Gift, Sparkles,
  Sunrise, Moon, Star
} from 'lucide-react';

const iconMap = {
  Trophy, Crown, Flame, Award, Zap, Gift, Sparkles,
  Sunrise, Moon, Star
};

export function BadgeNotification({ badges, onClose }) {
  if (!badges || badges.length === 0) return null;
  
  return (
    <AnimatePresence>
      {badges.map((badge, index) => {
        const Icon = iconMap[badge.icon] || Award;
        
        return (
          <motion.div
            key={badge.id}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ 
              type: "spring",
              stiffness: 200,
              damping: 20,
              delay: index * 0.3
            }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
            onClick={onClose}
          >
            <motion.div
              initial={{ y: 50 }}
              animate={{ y: 0 }}
              className="bg-white rounded-2xl p-8 max-w-md mx-4 text-center shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Confetti Effect */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: [0, 1.2, 1] }}
                transition={{ duration: 0.5 }}
                className="text-6xl mb-4"
              >
                🎉
              </motion.div>
              
              <h2 className="text-2xl font-bold text-slate-900 mb-2">
                Badge Earned!
              </h2>
              
              {/* Badge Icon */}
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ 
                  type: "spring",
                  stiffness: 200,
                  damping: 15,
                  delay: 0.2
                }}
                className="w-32 h-32 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{
                  backgroundColor: `${badge.color}20`,
                  borderWidth: '4px',
                  borderColor: badge.color
                }}
              >
                <Icon 
                  className="w-16 h-16"
                  style={{ color: badge.color }}
                />
              </motion.div>
              
              {/* Badge Name */}
              <h3 className="text-2xl font-bold text-slate-900 mb-2">
                {badge.name.en}
              </h3>
              
              {/* Badge Description */}
              <p className="text-slate-600 mb-6">
                {badge.description.en}
              </p>
              
              <button
                onClick={onClose}
                className="px-6 py-2 bg-gradient-to-r from-teal-500 to-teal-600 text-white rounded-lg font-semibold hover:shadow-lg transition-shadow"
              >
                Awesome!
              </button>
            </motion.div>
          </motion.div>
        );
      })}
    </AnimatePresence>
  );
}
