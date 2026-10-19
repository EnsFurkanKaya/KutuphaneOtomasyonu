import React, { useState, useEffect } from 'react';
import { History, Filter, CheckCircle2, AlertTriangle, BookOpen } from 'lucide-react';
import { api } from '../services/api';
import { Loan, ApiError } from '../types';
import { formatDate } from '../utils/formatters';
import { LoanStatusBadge } from '../components/common/StatusBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Alert } from '../components/common/Alert';
import { Pagination } from '../components/common/Pagination';

export const LoanHistoryPage: React.FC = () => {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<'all' | 'returned' | 'overdue'>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getMyLoans(statusFilter, page, 10);
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
    fetchHistory();
  }, [page, statusFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Ödünç Geçmişim</h1>
          <p className="text-sm text-slate-500 mt-1">
            Kütüphaneden geçmişte aldığınız ve iade ettiğiniz tüm kitap kayıtları
          </p>
        </div>

        {/* Durum Filtresi */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as any);
              setPage(1);
            }}
            className="py-2 px-3 rounded-xl border border-slate-200 bg-white text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="all">Tüm Kayıtlar</option>
            <option value="returned">Yalnızca İade Edilenler</option>
            <option value="overdue">Gecikmiş Olanlar</option>
          </select>
        </div>
      </div>

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
        <LoadingSpinner message="Geçmiş kayıtlar yükleniyor..." />
      ) : loans.length === 0 ? (
        <EmptyState
          title="Kayıt Bulunamadı"
          description="Seçilen filtreye uygun geçmiş ödünç kaydınız bulunmamaktadır."
        />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider rounded-xl">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Kitap</th>
                  <th className="py-3 px-4">Yazar</th>
                  <th className="py-3 px-4">Ödünç Alma Tarihi</th>
                  <th className="py-3 px-4">Son İade Tarihi</th>
                  <th className="py-3 px-4">İade Tarihi</th>
                  <th className="py-3 px-4 rounded-r-xl">Durum</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loans.map((loan) => (
                  <tr key={loan.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-slate-900">
                      {loan.book.title}
                      <div className="text-xs text-slate-400 font-mono">ISBN: {loan.book.isbn}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">{loan.book.author}</td>
                    <td className="py-3.5 px-4 text-slate-600">{formatDate(loan.borrowed_at)}</td>
                    <td className="py-3.5 px-4 text-slate-600">{formatDate(loan.due_at)}</td>
                    <td className="py-3.5 px-4">
                      {loan.returned_at ? (
                        <div className="text-emerald-700 font-medium">
                          {formatDate(loan.returned_at)}
                          {loan.late_return_days > 0 && (
                            <span className="text-xs text-amber-600 ml-1">
                              ({loan.late_return_days} gün gecikmeli iade)
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <LoanStatusBadge status={loan.status} />
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
    </div>
  );
};
