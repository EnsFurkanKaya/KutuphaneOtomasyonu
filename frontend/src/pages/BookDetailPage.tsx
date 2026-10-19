import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  BookOpen,
  Calendar,
  Building,
  MapPin,
  Barcode,
  Layers,
  CheckCircle,
  AlertTriangle,
  BookmarkCheck,
  Edit,
} from 'lucide-react';
import { api } from '../services/api';
import { Book, ApiError } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { BookAvailabilityBadge } from '../components/common/StatusBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Alert } from '../components/common/Alert';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { formatDate } from '../utils/formatters';

export const BookDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isStudent, isAdmin } = useAuth();

  const [book, setBook] = useState<Book | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Ödünç alma onay modalı
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [isBorrowing, setIsBorrowing] = useState(false);

  const fetchBook = async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getBook(Number(id));
      setBook(data);
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBook();
  }, [id]);

  const handleBorrow = async () => {
    if (!book) return;
    setIsBorrowing(true);
    setError(null);
    try {
      await api.borrowBook(book.id);
      setSuccessMessage(`"${book.title}" başarıyla ödünç alındı.`);
      setConfirmOpen(false);
      fetchBook(); // Stok güncellemesi
    } catch (err: any) {
      setError(err as ApiError);
      setConfirmOpen(false);
    } finally {
      setIsBorrowing(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Kitap bilgileri getiriliyor..." />;
  }

  if (!book && error) {
    return (
      <div className="space-y-4 max-w-2xl mx-auto">
        <Alert type="error" title="Hata" message={error.message} />
        <Link
          to="/kitaplar"
          className="inline-flex items-center gap-2 text-sm text-brand-600 font-semibold"
        >
          <ArrowLeft className="w-4 h-4" /> Kataloğa Geri Dön
        </Link>
      </div>
    );
  }

  if (!book) return null;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Üst Navigasyon */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900 font-medium transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Geri Dön
        </button>

        {isAdmin && (
          <Link
            to="/yonetici/kitaplar"
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition-colors"
          >
            <Edit className="w-3.5 h-3.5" /> Kitap Yönetim Paneli
          </Link>
        )}
      </div>

      {successMessage && (
        <Alert
          type="success"
          message={successMessage}
          onClose={() => setSuccessMessage(null)}
        />
      )}

      {error && (
        <Alert
          type="error"
          title="İşlem Hatası"
          message={error.message}
          details={error.details}
          onClose={() => setError(null)}
        />
      )}

      {/* Kitap Bilgi Kartı */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-8">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 pb-6 border-b border-slate-100">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-brand-700 bg-brand-50 px-2.5 py-1 rounded-lg">
                {book.category?.name || 'Kategori Belirtilmemiş'}
              </span>
              <BookAvailabilityBadge
                isAvailable={book.is_available}
                copies={book.available_copies}
              />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {book.title}
            </h1>
            <p className="text-base text-slate-600 font-medium">{book.author}</p>
          </div>

          {/* Ödünç Al Aksiyonu */}
          {isStudent && (
            <div className="shrink-0">
              <button
                disabled={!book.is_available}
                onClick={() => setConfirmOpen(true)}
                className="w-full sm:w-auto px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-2xl shadow-md shadow-brand-500/20 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
              >
                <BookmarkCheck className="w-5 h-5" />
                Bu Kitabı Ödünç Al
              </button>
            </div>
          )}
        </div>

        {/* Açıklama */}
        {book.description && (
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              Kitap Açıklaması
            </h3>
            <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line bg-slate-50/50 p-4 rounded-2xl border border-slate-100">
              {book.description}
            </p>
          </div>
        )}

        {/* Teknik ve Kütüphane Detayları */}
        <div>
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
            Kütüphane & Eser Bilgileri
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Barcode className="w-4 h-4 text-slate-400" />
                <span>ISBN Numarası</span>
              </div>
              <div className="font-mono font-semibold text-slate-900 text-sm">{book.isbn}</div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <MapPin className="w-4 h-4 text-slate-400" />
                <span>Raf Konumu</span>
              </div>
              <div className="font-semibold text-slate-900 text-sm">
                {book.shelf_location || 'Belirtilmedi'}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Layers className="w-4 h-4 text-slate-400" />
                <span>Kopya / Stok Durumu</span>
              </div>
              <div className="font-semibold text-slate-900 text-sm">
                {book.available_copies} uygun / {book.total_copies} toplam
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Building className="w-4 h-4 text-slate-400" />
                <span>Yayınevi</span>
              </div>
              <div className="font-semibold text-slate-900 text-sm">
                {book.publisher || 'Belirtilmedi'}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Calendar className="w-4 h-4 text-slate-400" />
                <span>Basım Yılı</span>
              </div>
              <div className="font-semibold text-slate-900 text-sm">
                {book.publication_year || 'Belirtilmedi'}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Calendar className="w-4 h-4 text-slate-400" />
                <span>Sisteme Eklenme</span>
              </div>
              <div className="font-semibold text-slate-900 text-sm">
                {formatDate(book.created_at)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Onay Modalı */}
      <ConfirmDialog
        isOpen={confirmOpen}
        title="Kitap Ödünç Alma Onayı"
        isLoading={isBorrowing}
        confirmLabel="Ödünç Al"
        message={
          <div>
            <p className="mb-2">
              <strong className="text-slate-900">{book.title}</strong> kitabını ödünç almak istediğinizden emin misiniz?
            </p>
            <p className="text-xs text-slate-500">
              Bu işlem sonrası kitabın uygun stok sayısı 1 azalacaktır ve ödünç süresi 14 gün olarak başlayacaktır.
            </p>
          </div>
        }
        onConfirm={handleBorrow}
        onCancel={() => setConfirmOpen(false)}
      />
    </div>
  );
};
