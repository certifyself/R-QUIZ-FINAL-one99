import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';
import { motion } from 'framer-motion';

export function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const currentLang = i18n.language;

  const toggleLanguage = () => {
    const newLang = currentLang === 'en' ? 'sk' : 'en';
    i18n.changeLanguage(newLang);
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={toggleLanguage}
      className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-teal-50 hover:bg-teal-100 text-teal-700 transition-colors border border-teal-200"
      data-testid="language-switcher"
      title={currentLang === 'en' ? 'Switch to Slovak' : 'Prepnúť na angličtinu'}
    >
      <Globe className="w-4 h-4" />
      <span className="text-sm font-semibold uppercase">{currentLang === 'en' ? 'SK' : 'EN'}</span>
    </motion.button>
  );
}
