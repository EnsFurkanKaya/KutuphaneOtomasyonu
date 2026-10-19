import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserPlus, BookMarked, User, Mail, Lock, Hash } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Alert } from '../components/common/Alert';
import { ApiError } from '../types';

export const RegisterPage: React.FC = () => {
  const [studentNumber, setStudentNumber] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [success, setSuccess] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await register(studentNumber, fullName, email, password);
      setSuccess(true);
      setTimeout(() => {
        navigate('/giris');
      }, 2000);
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6 bg-white p-8 sm:p-10 rounded-3xl border border-slate-200 shadow-xl shadow-slate-100">
        <div className="text-center">
          <div className="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center text-white mx-auto shadow-lg shadow-indigo-500/25 mb-4">
            <UserPlus className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Öğrenci Kaydı</h2>
          <p className="mt-2 text-sm text-slate-500">
            Online kütüphaneden kitap ödünç almak için hesap oluşturun
          </p>
        </div>

        {error && (
          <Alert
            type="error"
            title="Kayıt Başarısız"
            message={error.message}
            details={error.details}
            onClose={() => setError(null)}
          />
        )}

        {success && (
          <Alert
            type="success"
            title="Kayıt Başarılı!"
            message="Hesabınız başarıyla oluşturuldu. Giriş sayfasına yönlendiriliyorsunuz..."
          />
        )}

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
              Öğrenci Numarası
            </label>
            <div className="relative">
              <Hash className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                required
                pattern="\d{5,20}"
                value={studentNumber}
                onChange={(e) => setStudentNumber(e.target.value)}
                placeholder="Örn: 2026101"
                className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-slate-50/50"
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-1">5-20 haneli rakamlardan oluşmalıdır</p>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
              Ad Soyad
            </label>
            <div className="relative">
              <User className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                required
                minLength={3}
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Örn: Ahmet Yılmaz"
                className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-slate-50/50"
              />
            </div>
          </div>

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
                className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-slate-50/50"
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
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-slate-50/50"
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-1">En az 8 karakter, harf ve rakam içermelidir</p>
          </div>

          <button
            type="submit"
            disabled={isLoading || success}
            className="w-full mt-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl shadow-md shadow-indigo-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isLoading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <UserPlus className="w-5 h-5" />
            )}
            Hesap Oluştur
          </button>
        </form>

        <div className="text-center pt-2">
          <p className="text-sm text-slate-500">
            Zaten bir hesabınız var mı?{' '}
            <Link to="/giris" className="font-semibold text-indigo-600 hover:text-indigo-700">
              Giriş Yapın
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
