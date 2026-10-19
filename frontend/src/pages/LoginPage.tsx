import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LogIn, BookMarked, Lock, Mail } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Alert } from '../components/common/Alert';
import { ApiError } from '../types';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const { login, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || (isAdmin ? '/yonetici' : '/kitaplar');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login(email, password);
      // Başarılı giriş sonrası yönlendirme
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  const fillDemo = (e: string, p: string) => {
    setEmail(e);
    setPassword(p);
  };

  return (
    <div className="min-h-[80vh] flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 sm:p-10 rounded-3xl border border-slate-200 shadow-xl shadow-slate-100">
        <div className="text-center">
          <div className="w-14 h-14 bg-brand-600 rounded-2xl flex items-center justify-center text-white mx-auto shadow-lg shadow-brand-500/25 mb-4">
            <BookMarked className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Kütüphane Girişi</h2>
          <p className="mt-2 text-sm text-slate-500">
            Öğrenci veya yönetici hesabınızla sisteme giriş yapın
          </p>
        </div>

        {error && (
          <Alert
            type="error"
            title="Giriş Yapılamadı"
            message={error.message}
            details={error.details}
            onClose={() => setError(null)}
          />
        )}

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
              E-posta Adresi
            </label>
            <div className="relative">
              <Mail className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ornek@ogr.edu.tr"
                className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm bg-slate-50/50"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
              Parola
            </label>
            <div className="relative">
              <Lock className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm bg-slate-50/50"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-4 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isLoading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <LogIn className="w-5 h-5" />
            )}
            Giriş Yap
          </button>
        </form>

        <div className="text-center pt-2">
          <p className="text-sm text-slate-500">
            Hesabınız yok mu?{' '}
            <Link to="/kayit" className="font-semibold text-brand-600 hover:text-brand-700">
              Hemen Kayıt Olun
            </Link>
          </p>
        </div>

        {/* Test ve Değerlendirme İçin Hızlı Giriş Butonları */}
        <div className="pt-4 border-t border-slate-100">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 text-center">
            Ödev Değerlendirme İçin Hızlı Doldur
          </p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => fillDemo('admin@kutuphane.edu.tr', 'Admin12345!')}
              className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-center font-medium transition-colors"
            >
              Yönetici Hesabı
            </button>
            <button
              type="button"
              onClick={() => fillDemo('ahmet.yilmaz@ogr.edu.tr', 'Ogrenci12345!')}
              className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-center font-medium transition-colors"
            >
              Öğrenci Hesabı
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
