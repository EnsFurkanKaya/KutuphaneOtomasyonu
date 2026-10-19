import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookmarkCheck, RotateCcw, AlertTriangle, Clock } from 'lucide-react';
import { api } from '../services/api';
import { Loan, ApiError } from '../types';
import { formatDate } from '../utils/formatters';
import { LoanStatusBadge } from '../components/common/StatusBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Alert } from '../components/common/Alert';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { Pagination } from '../components/common/Pagination';

export const MyLoansPage: React.FC = () => {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // İade onay modalı
  const [returnModalOpen, setReturnModalOpen] = useState(false);
  const [selectedLoan, setSelectedLoan] = useState<Loan | null>(null);
  const [isReturning, setIsReturning] = useState(false);

  const fetchLoans = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getMyLoans('active', page, 10);
      setLoans(data.items);
      setTotalPages(data.pages);
      setTotalItems(data.total);
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLoans();
  }, [page]);

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
      fetchLoans();
    } catch (err: any) {
      setError(err as ApiError);
      setReturnModalOpen(false);
    } finally {
      setIsReturning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Aktif Ödünç Kitaplarım</h1>
        <p className="text-sm text-slate-500 mt-1">
          Şu an sizde bulunan kitapları ve son teslim tarihlerini takip edin
        </p>
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

      {isLoading ? (
        <LoadingSpinner message="Ödünç kayıtları yükleniyor..." />
      ) : loans.length === 0 ? (
        <EmptyState
          title="Aktif Ödünç Kitabınız Bulunmuyor"
          description="Şu an elinizde ödünç bir kitap bulunmamaktadır."
          action={
            <Link
              to="/kitaplar"
              className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
            >
              Kitap Kataloğuna Git
            </Link>
          }
        />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden p-6 space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider rounded-xl">
                <tr>
                  <th className="py-3.5 px-4 rounded-l-xl">Kitap</th>
                  <th className="py-3.5 px-4">Yazar</th>
                  <th className="py-3.5 px-4">Ödünç Alma Tarihi</th>
                  <th className="py-3.5 px-4">Son İade Tarihi</th>
                  <th className="py-3.5 px-4">Gecikme / Durum</th>
                  <th className="py-3.5 px-4 text-right rounded-r-xl">İşlem</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loans.map((loan) => (
                  <tr key={loan.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-4 px-4 font-semibold text-slate-900">
                      <Link to={`/kitaplar/${loan.book.id}`} className="hover:text-brand-600 transition-colors">
                        {loan.book.title}
                      </Link>
                      <div className="text-xs text-slate-400 font-mono mt-0.5">ISBN: {loan.book.isbn}</div>
                    </td>
                    <td className="py-4 px-4 text-slate-600">{loan.book.author}</td>
                    <td className="py-4 px-4 text-slate-600">{formatDate(loan.borrowed_at)}</td>
                    <td className="py-4 px-4">
                      <div className={`font-semibold ${loan.is_overdue ? 'text-rose-600 font-bold' : 'text-slate-900'}`}>
                        {formatDate(loan.due_at)}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <LoanStatusBadge status={loan.status} />
                        {loan.is_overdue && (
                          <span className="text-xs font-bold text-rose-600">
                            ({loan.overdue_days} gün gecikme)
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <button
                        onClick={() => openReturnModal(loan)}
                        className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-brand-600 text-white font-semibold text-xs shadow-sm transition-all"
                      >
                        <RotateCcw className="w-3.5 h-3.5" /> İade Et
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Pagination
            currentPage={page}
            totalPages={totalPages}
            totalItems={totalItems}
            pageSize={10}
            onPageChange={(p) => setPage(p)}
          />
        </div>
      )}

      {/* İade Onay Modalı */}
      <ConfirmDialog
        isOpen={returnModalOpen}
        title="Kitabı İade Et"
        isLoading={isReturning}
        confirmLabel="İade Et"
        message={
          <div>
            <p className="mb-2">
              <strong className="text-slate-900">{selectedLoan?.book.title}</strong> kitabını iade etmek istediğinizi onaylıyor musunuz?
            </p>
            <p className="text-xs text-slate-500">
              Kitap kütüphane envanterine geri aktarılacak ve aktif ödünç sayınız düşürülecektir.
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
