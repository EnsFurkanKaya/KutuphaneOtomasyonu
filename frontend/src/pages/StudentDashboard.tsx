import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  BookmarkCheck,
  AlertTriangle,
  Clock,
  ArrowRight,
  RotateCcw,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import { Loan, ApiError } from '../types';
import { formatDate } from '../utils/formatters';
import { LoanStatusBadge } from '../components/common/StatusBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Alert } from '../components/common/Alert';
import { ConfirmDialog } from '../components/common/ConfirmDialog';

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [activeLoans, setActiveLoans] = useState<Loan[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // İade onay modalı
  const [returnModalOpen, setReturnModalOpen] = useState(false);
  const [selectedLoan, setSelectedLoan] = useState<Loan | null>(null);
  const [isReturning, setIsReturning] = useState(false);

  const fetchActiveLoans = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getMyLoans('active', 1, 10);
      setActiveLoans(data.items);
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveLoans();
  }, []);

  const openReturnModal = (loan: Loan) => {
    setSelectedLoan(loan);
    setReturnModalOpen(true);
  };

  const confirmReturn = async () => {
    if (!selectedLoan) return;
    setIsReturning(true);
    setError(null);
    try {
      await api.returnLoan(selectedLoan.id);
      setSuccessMessage(`"${selectedLoan.book.title}" kütüphaneye başarıyla iade edildi.`);
      setReturnModalOpen(false);
      setSelectedLoan(null);
      fetchActiveLoans();
    } catch (err: any) {
      setError(err as ApiError);
      setReturnModalOpen(false);
    } finally {
      setIsReturning(false);
    }
  };

  const overdueCount = activeLoans.filter((l) => l.is_overdue).length;

  return (
    <div className="space-y-6">
      {/* Karşılama Banner'ı */}
      <div className="bg-gradient-to-r from-brand-600 via-indigo-600 to-purple-600 rounded-3xl p-6 sm:p-8 text-white shadow-xl shadow-brand-500/15 relative overflow-hidden">
        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> Öğrenci Portali
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Hoş Geldiniz, {user?.full_name}!
          </h1>
          <p className="text-white/80 text-sm">
            Öğrenci No: <strong className="text-white">{user?.student_number}</strong> | Kütüphane hesabınızla aktif kitaplarınızı takip edebilir ve yeni kitaplar ödünç alabilirsiniz.
          </p>
        </div>
      </div>

      {successMessage && (
        <Alert type="success" message={successMessage} onClose={() => setSuccessMessage(null)} />
      )}

      {error && (
        <Alert
          type="error"
          title="Hata"
          message={error.message}
          details={error.details}
          onClose={() => setError(null)}
        />
      )}

      {/* İstatistik Özet Kartları */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              Aktif Ödünç Durumu
            </span>
            <div className="text-2xl font-bold text-slate-900">
              {activeLoans.length} <span className="text-sm font-normal text-slate-400">/ 3 Kitap</span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Kalan ödünç hakkınız: {Math.max(0, 3 - activeLoans.length)}
            </p>
          </div>
          <div className="p-3 bg-brand-50 text-brand-600 rounded-2xl">
            <BookmarkCheck className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              Gecikmiş Kitaplar
            </span>
            <div className={`text-2xl font-bold ${overdueCount > 0 ? 'text-rose-600' : 'text-slate-900'}`}>
              {overdueCount} <span className="text-sm font-normal text-slate-400">Adet</span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {overdueCount > 0 ? 'Lütfen en kısa sürede iade ediniz' : 'Gecikmiş kitabınız yok'}
            </p>
          </div>
          <div className={`p-3 rounded-2xl ${overdueCount > 0 ? 'bg-rose-50 text-rose-600' : 'bg-emerald-50 text-emerald-600'}`}>
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              Hızlı İşlem
            </span>
            <div className="text-sm font-semibold text-slate-900">Katalogda Arama Yap</div>
            <Link
              to="/kitaplar"
              className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1 mt-1"
            >
              Kitaplara Göz At <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl">
            <BookOpen className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Aktif Ödünç Kitaplar Tablosu */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Şu An Sizde Olan Kitaplar</h2>
            <p className="text-xs text-slate-500">
              Ödünç aldığınız ve henüz kütüphaneye teslim etmediğiniz kitaplar
            </p>
          </div>
          <Link
            to="/odunc-gecmisi"
            className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
          >
            Tüm Geçmişi Gör <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {isLoading ? (
          <LoadingSpinner message="Aktif ödünçler yükleniyor..." />
        ) : activeLoans.length === 0 ? (
          <EmptyState
            title="Aktif Ödünç Kitabınız Yok"
            description="Şu anda ödünç aldığınız bir kitap bulunmuyor. Kütüphane kataloğundan dilediğiniz kitabı hemen ödünç alabilirsiniz."
            action={
              <Link
                to="/kitaplar"
                className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
              >
                Kitap Kataloğunu İncele
              </Link>
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider rounded-xl">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Kitap Bilgisi</th>
                  <th className="py-3 px-4">Ödünç Alma</th>
                  <th className="py-3 px-4">Son İade Tarihi</th>
                  <th className="py-3 px-4">Durum</th>
                  <th className="py-3 px-4 text-right rounded-r-xl">İşlem</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {activeLoans.map((loan) => (
                  <tr key={loan.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{loan.book.title}</div>
                      <div className="text-xs text-slate-500 font-mono">ISBN: {loan.book.isbn}</div>
                    </td>
                    <td className="py-3 px-4 text-slate-600">{formatDate(loan.borrowed_at)}</td>
                    <td className="py-3 px-4">
                      <div className={`font-semibold ${loan.is_overdue ? 'text-rose-600 font-bold' : 'text-slate-800'}`}>
                        {formatDate(loan.due_at)}
                      </div>
                      {loan.is_overdue && (
                        <div className="text-[11px] text-rose-500 font-medium">
                          {loan.overdue_days} gün gecikti!
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <LoanStatusBadge status={loan.status} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => openReturnModal(loan)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-brand-50 text-slate-700 hover:text-brand-700 font-semibold text-xs transition-colors"
                      >
                        <RotateCcw className="w-3.5 h-3.5" /> İade Et
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* İade Onay Modalı */}
      <ConfirmDialog
        isOpen={returnModalOpen}
        title="Kitap İadesi Onayı"
        isLoading={isReturning}
        confirmLabel="İadeyi Tamamla"
        variant="primary"
        message={
          <div>
            <p className="mb-2">
              <strong className="text-slate-900 font-semibold">{selectedLoan?.book.title}</strong> kitabını teslim etmek üzeresiniz.
            </p>
            <p className="text-xs text-slate-500">
              Bu işlemle kütüphanedeki mevcut kitap stoğu 1 adet artırılacak ve aktif ödünç kaydınız tamamlanacaktır.
            </p>
          </div>
        }
        onConfirm={confirmReturn}
        onCancel={() => {
          setReturnModalOpen(false);
          setSelectedLoan(null);
        }}
      />
    </div>
  );
};
