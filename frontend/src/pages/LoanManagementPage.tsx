import React, { useState, useEffect } from 'react';
import {
  ClipboardList,
  Search,
  Filter,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Clock,
  User,
  BookOpen,
} from 'lucide-react';
import { api } from '../services/api';
import { Loan, Page, ApiError } from '../types';
import { formatDate } from '../utils/formatters';
import { LoanStatusBadge } from '../components/common/StatusBadge';
import { Pagination } from '../components/common/Pagination';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Alert } from '../components/common/Alert';
import { ConfirmDialog } from '../components/common/ConfirmDialog';

export const LoanManagementPage: React.FC = () => {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'overdue' | 'returned'>('all');
  const [searchTerm, setSearchTerm] = useState('');
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
      const data: Page<Loan> = await api.getAllLoans({
        status: statusFilter,
        q: searchTerm || undefined,
        page,
        page_size: 15,
      });
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
  }, [page, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchLoans();
  };

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
      setSuccessMessage(
        `"${selectedLoan.book.title}" kütüphaneye teslim alındı. Stok 1 artırıldı.`
      );
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Ödünç İşlemleri Denetimi</h1>
          <p className="text-sm text-slate-500 mt-1">
            Kütüphane genelindeki tüm ödünç ve iade süreçlerini inceleyin ve kitap teslimlerini onaylayın
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

      {/* Arama ve Filtreleme */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Öğrenci adı, no, kitap adı veya ISBN ara..."
              className="w-full pl-11 pr-4 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium rounded-xl transition-colors"
          >
            Filtrele
          </button>
        </form>

        <div className="flex items-center gap-2 pt-2 border-t border-slate-100 text-xs">
          <span className="font-semibold text-slate-500 uppercase tracking-wider">Durum:</span>
          {(['all', 'active', 'overdue', 'returned'] as const).map((st) => {
            const labels = {
              all: 'Tümü',
              active: 'Aktif Ödünçler',
              overdue: 'Gecikmişler',
              returned: 'İade Edilenler',
            };
            return (
              <button
                key={st}
                onClick={() => {
                  setStatusFilter(st);
                  setPage(1);
                }}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  statusFilter === st
                    ? 'bg-brand-600 text-white shadow-sm font-semibold'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {labels[st]}
              </button>
            );
          })}
        </div>
      </div>

      {isLoading ? (
        <LoadingSpinner message="Ödünç hareketleri listeleniyor..." />
      ) : loans.length === 0 ? (
        <EmptyState
          title="Ödünç Kaydı Bulunamadı"
          description="Seçilen arama veya filtre kriterlerine uyan bir işlem kaydı yok."
        />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider rounded-xl">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Öğrenci</th>
                  <th className="py-3 px-4">Kitap</th>
                  <th className="py-3 px-4">Ödünç Tarihi</th>
                  <th className="py-3 px-4">Son İade Tarihi</th>
                  <th className="py-3 px-4">İade Tarihi</th>
                  <th className="py-3 px-4">Durum</th>
                  <th className="py-3 px-4 text-right rounded-r-xl">Aksiyon</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loans.map((loan) => (
                  <tr key={loan.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-900">{loan.user.full_name}</div>
                      <div className="text-xs text-slate-400 font-mono">
                        {loan.user.student_number || loan.user.email}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-medium text-slate-800">{loan.book.title}</div>
                      <div className="text-xs text-slate-400 font-mono">ISBN: {loan.book.isbn}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">{formatDate(loan.borrowed_at)}</td>
                    <td className="py-3.5 px-4 text-slate-600">{formatDate(loan.due_at)}</td>
                    <td className="py-3.5 px-4">
                      {loan.returned_at ? (
                        <span className="text-emerald-700 font-medium">
                          {formatDate(loan.returned_at)}
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1.5">
                        <LoanStatusBadge status={loan.status} />
                        {loan.is_overdue && (
                          <span className="text-xs font-bold text-rose-600">
                            (+{loan.overdue_days} gün)
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {!loan.returned_at && (
                        <button
                          onClick={() => openReturnModal(loan)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-brand-600 text-white font-semibold text-xs shadow-sm transition-all"
                        >
                          <RotateCcw className="w-3.5 h-3.5" /> Teslim Al
                        </button>
                      )}
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
            pageSize={15}
            onPageChange={(p) => setPage(p)}
          />
        </div>
      )}

      {/* Teslim Alma Onay Modalı */}
      <ConfirmDialog
        isOpen={returnModalOpen}
        title="Kitap Teslim Alma Onayı"
        isLoading={isReturning}
        confirmLabel="Teslim Al ve Stoğu Artır"
        message={
          <div>
            <p className="mb-2">
              <strong className="text-slate-900">{selectedLoan?.user.full_name}</strong> isimli öğrencinin ödünç aldığı{' '}
              <strong className="text-slate-900">{selectedLoan?.book.title}</strong> kitabını kütüphaneye teslim almayı onaylıyor musunuz?
            </p>
            <p className="text-xs text-slate-500">
              Bu işlem ile kitap kütüphane envanterine geri eklenecektir (stok sayısı 1 artacaktır).
            </p>
          </div>
        }
        onConfirm={confirmReturn}
        onCancel={() => setReturnModalOpen(false)}
      />
    </div>
  );
};
