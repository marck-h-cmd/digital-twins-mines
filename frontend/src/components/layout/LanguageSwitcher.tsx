'use client';

import { useState, useRef, useEffect } from 'react';
import { useI18nStore } from '@/store/i18nStore';
import Image from 'next/image';

const languages = [
  { code: 'es', label: 'ES', flag: '/img/spain.png' },
  { code: 'en', label: 'EN', flag: '/img/united-states.png' }
] as const;

export function LanguageSwitcher() {
  const { locale, setLocale } = useI18nStore();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const activeLang = languages.find(l => l.code === locale) || languages[0];

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-border bg-card hover:bg-muted transition-colors"
      >
        <Image src={activeLang.flag} alt={activeLang.label} width={20} height={20} className="rounded-sm object-cover" />
        <span className="text-sm font-medium">{activeLang.label}</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-32 bg-card border border-border rounded-md shadow-lg overflow-hidden z-50">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => {
                setLocale(lang.code);
                setIsOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-muted transition-colors ${
                locale === lang.code ? 'bg-primary/10 text-primary font-semibold' : 'text-foreground'
              }`}
            >
              <Image src={lang.flag} alt={lang.label} width={20} height={20} className="rounded-sm object-cover" />
              {lang.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
