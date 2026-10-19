import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Calendar,
  Search,
  Filter,
  FileDown,
  User,
  BookOpen,
} from 'lucide-react';
import { api } from '../services/api';
import { OverdueReport, ApiError } from '../types';
import { formatDate } from '../utils/formatters';
import { Pagination } from '../components/common/Pagination';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Alert } from '../components/common/Alert';

export const OverdueReportPage: React.FC = () => {
  const [report, setReport] = useState<OverdueReport | null>(null);
  const [page, setPage] = useState(1);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [studentFilter, setStudentFilter] = useState('');
  const [bookFilter, setBookFilter] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchReport = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data: OverdueReport = await api.getOverdueReport({
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        student: studentFilter || undefined,
        book: bookFilter || undefined,
        page,
        page_size: 15,
      });
      setReport(data);
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [page]);

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchReport();
  };

  const handleResetFilters = () => {
    setStartDate('');
    setEndDate('');
    setStudentFilter('');
    setBookFilter('');
    setPage(1);
    setTimeout(() => {
      fetchReport();
    }, 0);
  };

  return (
    <div className="space-y-6">
      {/* Başlık ve Açıklama */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Gecikme Raporu</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200">
              Resmi Denetim
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Son iade tarihi geçmiş ve henüz kütüphaneye teslim edilmemiş tüm ödünç kayıtları
          </p>
        </div>
      </div>

      {error && (
        <Alert
          type="error"
          title="Rapor Üretim Hatası"
          message={error.message}
          details={error.details}
          onClose={() => setError(null)}
        />
      )}

      {/* Filtreleme Formu */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <form onSubmit={handleFilterSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                Son İade Başlangıç (YYYY-AA-GG)
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500 bg-slate-50/50"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                Son İade Bitiş (YYYY-AA-GG)
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500 bg-slate-50/50"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                Öğrenci (Ad Soyad / No)
              </label>
              <input
                type="text"
                placeholder="Örn: Ahmet veya 2026001"
                value={studentFilter}
                onChange={(e) => setStudentFilter(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500 bg-slate-50/50"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">
                Kitap (Başlık / ISBN)
              </label>
              <input
                type="text"
                placeholder="Örn: Temiz Kod veya ISBN"
                value={bookFilter}
                onChange={(e) => setBookFilter(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500 bg-slate-50/50"
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={handleResetFilters}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              Filtreleri Sıfırla
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl shadow-sm transition-colors"
            >
              Raporu Filtrele
            </button>
          </div>
        </form>
      </div>

      {/* Rapor Tablosu */}
      {isLoading ? (
        <LoadingSpinner message="Gecikme raporu derleniyor..." />
      ) : !report || report.items.length === 0 ? (
        <EmptyState
          title="Gecikmiş Kayıt Yok"
          description="Seçilen kriterlerde teslim süresi geçmiş aktif bir ödünç kaydı bulunmamaktadır. Kütüphane iade düzeni kusursuz!"
        />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 pb-2 border-b border-slate-100">
            <div>
              Rapor Üretilme Tarihi:{' '}
              <span className="font-semibold text-slate-800">{formatDate(report.generated_at)}</span>
            </div>
            <div className="font-bold text-rose-600 bg-rose-50 px-2.5 py-1 rounded-lg">
              Toplam {report.total} Adet Gecikmiş Kayıt
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider rounded-xl">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Öğrenci No</th>
                  <th className="py-3 px-4">Öğrenci Adı Soyadı</th>
                  <th className="py-3 px-4">Kitap Adı</th>
                  <th className="py-3 px-4">ISBN</th>
                  <th className="py-3 px-4">Ödünç Tarihi</th>
                  <th className="py-3 px-4">Son İade Tarihi</th>
                  <th className="py-3 px-4 text-right rounded-r-xl">Gecikme Günü</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {report.items.map((item) => (
                  <tr key={item.loan_id} className="hover:bg-rose-50/30 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-slate-900 font-semibold">
                      {item.student_number || '-'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-900 font-semibold">
                      {item.full_name}
                      <div className="text-xs text-slate-400 font-normal">{item.email}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-800">{item.book_title}</td>
                    <td className="py-3.5 px-4 font-mono text-xs text-slate-500">{item.isbn}</td>
                    <td className="py-3.5 px-4 text-slate-600">{formatDate(item.borrowed_at)}</td>
                    <td className="py-3.5 px-4 text-rose-700 font-bold">{formatDate(item.due_at)}</td>
                    <td className="py-3.5 px-4 text-right">
                      <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300">
                        <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                        {item.overdue_days} Gün
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Pagination
            currentPage={page}
            totalPages={report.pages}
            totalItems={report.total}
            pageSize={15}
            onPageChange={(p) => setPage(p)}
          />
        </div>
      )}
    </div>
  );
};
