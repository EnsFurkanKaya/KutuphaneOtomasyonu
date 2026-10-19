import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, Home, ArrowLeft } from 'lucide-react';

export const ForbiddenPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center">
      <div className="w-20 h-20 bg-rose-50 text-rose-600 rounded-3xl flex items-center justify-center mb-6 border border-rose-100">
        <ShieldAlert className="w-10 h-10" />
      </div>
      <span className="text-sm font-bold text-rose-600 uppercase tracking-widest mb-2 block">
        403 Yetkisiz Erişim
      </span>
      <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-3 tracking-tight">
        Erişim Engellendi
      </h1>
      <p className="text-sm text-slate-500 max-w-md mb-8 leading-relaxed">
        Bu sayfayı görüntülemek veya bu işlemi gerçekleştirmek için gerekli yetkiye sahip değilsiniz. Bu alan yalnızca sistem yöneticilerine açıktır.
      </p>
      <div className="flex items-center gap-3">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
        >
          <Home className="w-4 h-4" /> Ana Sayfaya Dön
        </Link>
      </div>
    </div>
  );
};
