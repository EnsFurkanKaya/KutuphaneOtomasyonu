import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  Copy,
  CheckCircle,
  BookmarkCheck,
  AlertTriangle,
  Users,
  Tags,
  ArrowRight,
  TrendingUp,
  Activity,
  Calendar,
} from 'lucide-react';
import { api } from '../services/api';
import { DashboardStats, ApiError } from '../types';
import { formatDateTime } from '../utils/formatters';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Alert } from '../components/common/Alert';

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchDashboard = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getDashboard();
      setStats(data);
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (isLoading) {
    return <LoadingSpinner message="Yönetici paneli istatistikleri hazırlanıyor..." />;
  }

  if (error || !stats) {
    return (
      <div className="space-y-4">
        <Alert
          type="error"
          title="İstatistikler Yüklenemedi"
          message={error?.message || 'Bir hata oluştu.'}
          details={error?.details}
        />
        <button
          onClick={fetchDashboard}
          className="px-4 py-2 bg-brand-600 text-white rounded-xl text-sm font-semibold"
        >
          Yeniden Dene
        </button>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Aktif Kitap Başlığı',
      value: stats.active_book_titles,
      sub: 'Kütüphanedeki farklı eserler',
      icon: BookOpen,
      color: 'text-indigo-600 bg-indigo-50',
    },
    {
      title: 'Toplam Kitap Kopyası',
      value: stats.total_copies,
      sub: 'Tüm fiziksel nüshalar',
      icon: Copy,
      color: 'text-blue-600 bg-blue-50',
    },
    {
      title: 'Ödünç Verilebilir Kopya',
      value: stats.available_copies,
      sub: 'Rafta hazır uygun stok',
      icon: CheckCircle,
      color: 'text-emerald-600 bg-emerald-50',
    },
    {
      title: 'Aktif Ödünç Kayıtları',
      value: stats.active_loans,
      sub: 'Şu anda öğrencilerde olan',
      icon: BookmarkCheck,
      color: 'text-purple-600 bg-purple-50',
    },
    {
      title: 'Gecikmiş Ödünçler',
      value: stats.overdue_loans,
      sub: 'Süresi geçen kitaplar',
      icon: AlertTriangle,
      color: stats.overdue_loans > 0 ? 'text-rose-600 bg-rose-50' : 'text-slate-600 bg-slate-100',
      urgent: stats.overdue_loans > 0,
    },
    {
      title: 'Aktif Öğrenci Sayısı',
      value: stats.active_students,
      sub: 'Kayıtlı ve aktif üyeler',
      icon: Users,
      color: 'text-amber-600 bg-amber-50',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Başlık ve Üst Çubuk */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Kütüphane Yönetim Paneli
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Sistem istatistikleri, stok uygunluk durumu ve güncel ödünç hareketleri
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to="/yonetici/gecikme-raporu"
            className="px-4 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-700 font-semibold rounded-xl text-xs sm:text-sm border border-rose-200 transition-colors flex items-center gap-1.5"
          >
            <AlertTriangle className="w-4 h-4" /> Gecikme Raporu
          </Link>
          <Link
            to="/yonetici/kitaplar"
            className="px-4 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-xl text-xs sm:text-sm shadow-sm transition-all flex items-center gap-1.5"
          >
            <BookOpen className="w-4 h-4" /> Kitap Yönetimi
          </Link>
        </div>
      </div>

      {/* 6 Temel İstatistik Kartı */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              className={`p-6 bg-white rounded-3xl border ${
                card.urgent ? 'border-rose-200 shadow-rose-100/50 shadow-md' : 'border-slate-200/80 shadow-sm'
              } flex items-start justify-between`}
            >
              <div className="space-y-1">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                  {card.title}
                </span>
                <div className={`text-3xl font-extrabold ${card.urgent ? 'text-rose-600' : 'text-slate-900'}`}>
                  {card.value}
                </div>
                <p className="text-xs text-slate-400 mt-1">{card.sub}</p>
              </div>
              <div className={`p-3.5 rounded-2xl ${card.color}`}>
                <Icon className="w-6 h-6" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Son Gerçekleştirilen Ödünç ve İade İşlemleri */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-4">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-slate-100 text-slate-700 rounded-xl">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Son Gerçekleştirilen İşlemler</h2>
              <p className="text-xs text-slate-500">
                Yakın zamanda gerçekleşen ödünç alma ve iade hareketleri
              </p>
            </div>
          </div>
          <Link
            to="/yonetici/oduncler"
            className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
          >
            Tüm Hareketleri Gör <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {stats.recent_activity.length === 0 ? (
          <p className="text-sm text-slate-500 py-6 text-center">Henüz bir kütüphane hareketi bulunmuyor.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider rounded-xl">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">İşlem Türü</th>
                  <th className="py-3 px-4">Öğrenci</th>
                  <th className="py-3 px-4">Kitap</th>
                  <th className="py-3 px-4 rounded-r-xl">Zaman</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {stats.recent_activity.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4">
                      {item.type === 'BORROW' ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-brand-50 text-brand-700 border border-brand-200">
                          <BookmarkCheck className="w-3.5 h-3.5" /> Ödünç Alındı
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <CheckCircle className="w-3.5 h-3.5" /> İade Edildi
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{item.full_name}</div>
                      <div className="text-xs text-slate-400 font-mono">{item.student_number}</div>
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-800">{item.book_title}</td>
                    <td className="py-3 px-4 text-xs text-slate-500">{formatDateTime(item.occurred_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
