import React, { useState } from 'react';
import { User, Lock, Save, Shield, KeyRound, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import { ApiError } from '../types';
import { Alert } from '../components/common/Alert';
import { formatDate } from '../utils/formatters';

export const ProfilePage: React.FC = () => {
  const { user, refreshUser } = useAuth();

  // Profil Güncelleme
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<ApiError | null>(null);

  // Parola Değiştirme
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<ApiError | null>(null);

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUpdatingProfile(true);
    setProfileError(null);
    setProfileSuccess(null);
    try {
      await api.updateProfile(fullName);
      setProfileSuccess('Profil bilgileriniz başarıyla güncellendi.');
      await refreshUser();
    } catch (err: any) {
      setProfileError(err as ApiError);
    } finally {
      setIsUpdatingProfile(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(null);

    if (newPassword !== confirmPassword) {
      setPasswordError({
        code: 'PAROLA_UYUSMUYOR',
        message: 'Yeni parola ile parola tekrarı eşleşmiyor.',
      });
      return;
    }

    setIsChangingPassword(true);
    try {
      await api.changePassword(currentPassword, newPassword);
      setPasswordSuccess('Parolanız başarıyla değiştirildi.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      await refreshUser();
    } catch (err: any) {
      setPasswordError(err as ApiError);
    } finally {
      setIsChangingPassword(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Kullanıcı Profili</h1>
        <p className="text-sm text-slate-500 mt-1">
          Hesap bilgilerinizi inceleyin ve parolanızı güncelleyin
        </p>
      </div>

      {user?.must_change_password && (
        <Alert
          type="warning"
          title="Zorunlu Parola Değişikliği"
          message="Hesap güvenliğiniz için ilk kurulumda tanımlanan varsayılan parolanızı değiştirmeniz gerekmektedir."
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Profil Bilgileri Formu */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-5">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
            <div className="p-2.5 bg-brand-50 text-brand-600 rounded-xl">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Kişisel Bilgiler</h2>
              <p className="text-xs text-slate-500">Ad ve soyad bilgilerinizi güncelleyin</p>
            </div>
          </div>

          {profileSuccess && (
            <Alert type="success" message={profileSuccess} onClose={() => setProfileSuccess(null)} />
          )}

          {profileError && (
            <Alert
              type="error"
              title="Hata"
              message={profileError.message}
              details={profileError.details}
              onClose={() => setProfileError(null)}
            />
          )}

          <form onSubmit={handleProfileSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Ad Soyad
              </label>
              <input
                type="text"
                required
                minLength={3}
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">
                E-posta Adresi (Değiştirilemez)
              </label>
              <input
                type="email"
                disabled
                value={user?.email || ''}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50 text-slate-500 cursor-not-allowed font-medium"
              />
            </div>

            {user?.student_number && (
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Öğrenci Numarası (Değiştirilemez)
                </label>
                <input
                  type="text"
                  disabled
                  value={user.student_number}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm bg-slate-50 text-slate-500 cursor-not-allowed font-mono"
                />
              </div>
            )}

            <div className="pt-2">
              <button
                type="submit"
                disabled={isUpdatingProfile}
                className="w-full py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Save className="w-4 h-4" />
                {isUpdatingProfile ? 'Kaydediliyor...' : 'Bilgileri Güncelle'}
              </button>
            </div>
          </form>
        </div>

        {/* Parola Değiştirme Formu */}
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-5">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
            <div className="p-2.5 bg-purple-50 text-purple-600 rounded-xl">
              <KeyRound className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Parola Değiştir</h2>
              <p className="text-xs text-slate-500">Hesap güvenliğiniz için parolanızı yenileyin</p>
            </div>
          </div>

          {passwordSuccess && (
            <Alert type="success" message={passwordSuccess} onClose={() => setPasswordSuccess(null)} />
          )}

          {passwordError && (
            <Alert
              type="error"
              title="Hata"
              message={passwordError.message}
              details={passwordError.details}
              onClose={() => setPasswordError(null)}
            />
          )}

          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Mevcut Parola
              </label>
              <input
                type="password"
                required
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Yeni Parola
              </label>
              <input
                type="password"
                required
                minLength={8}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-purple-500"
              />
              <p className="text-[11px] text-slate-400 mt-1">En az 8 karakter, harf ve rakam içermelidir</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Yeni Parola (Tekrar)
              </label>
              <input
                type="password"
                required
                minLength={8}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={isChangingPassword}
                className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-sm font-semibold shadow-sm transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Lock className="w-4 h-4" />
                {isChangingPassword ? 'Değiştiriliyor...' : 'Parolayı Değiştir'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
