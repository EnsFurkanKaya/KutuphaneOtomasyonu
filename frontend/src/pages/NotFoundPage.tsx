import React from 'react';
import { Link } from 'react-router-dom';
import { FileQuestion, ArrowLeft, Home } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
      <div className="w-20 h-20 bg-slate-100 rounded-3xl flex items-center justify-center text-slate-400 mb-6">
        <FileQuestion className="w-10 h-10" />
      </div>
      <span className="text-sm font-bold text-brand-600 uppercase tracking-widest mb-2 block">
        404 Hatası
      </span>
      <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-3 tracking-tight">
        Sayfa Bulunamadı
      </h1>
      <p className="text-sm text-slate-500 max-w-md mb-8 leading-relaxed">
        Aradığınız sayfa silinmiş, taşınmış ya da geçici olarak erişilemiyor olabilir. Lütfen adresi kontrol edin veya ana sayfaya dönün.
      </p>
      <div className="flex items-center gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
        >
          <Home className="w-4 h-4" /> Ana Sayfaya Dön
        </Link>
      </div>
    </div>
  );
};
