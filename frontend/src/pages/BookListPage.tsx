import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  Filter,
  BookOpen,
  ArrowUpDown,
  CheckCircle2,
  BookmarkPlus,
  Info,
} from 'lucide-react';
import { api } from '../services/api';
import { Book, Category, Page, ApiError } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { BookAvailabilityBadge } from '../components/common/StatusBadge';
import { Pagination } from '../components/common/Pagination';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Alert } from '../components/common/Alert';
import { ConfirmDialog } from '../components/common/ConfirmDialog';

export const BookListPage: React.FC = () => {
  const { isAuthenticated, isStudent, isAdmin } = useAuth();

  const [books, setBooks] = useState<Book[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Filtreler
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [availableOnly, setAvailableOnly] = useState(false);
  const [sortBy, setSortBy] = useState('title');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // Ödünç alma onay modalı
  const [borrowModalOpen, setBorrowModalOpen] = useState(false);
  const [selectedBookForBorrow, setSelectedBookForBorrow] = useState<Book | null>(null);
  const [isBorrowing, setIsBorrowing] = useState(false);

  const fetchCategories = async () => {
    try {
      const data = await api.getCategories();
      setCategories(data);
    } catch {
      // sessizce geç
    }
  };

  const fetchBooks = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data: Page<Book> = await api.getBooks({
        q: searchTerm || undefined,
        category_id: selectedCategory ? Number(selectedCategory) : undefined,
        available_only: availableOnly,
        sort: sortBy,
        order: sortOrder,
        page,
        page_size: 12,
      });
      setBooks(data.items);
      setTotalPages(data.pages);
      setTotalItems(data.total);
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchBooks();
  }, [page, selectedCategory, availableOnly, sortBy, sortOrder]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchBooks();
  };

  const openBorrowConfirm = (book: Book) => {
    setSelectedBookForBorrow(book);
    setBorrowModalOpen(true);
  };

  const confirmBorrow = async () => {
    if (!selectedBookForBorrow) return;
    setIsBorrowing(true);
    setError(null);
    try {
      await api.borrowBook(selectedBookForBorrow.id);
      setSuccessMessage(`"${selectedBookForBorrow.title}" başarıyla ödünç alındı. 14 gün içinde iade etmeyi unutmayınız.`);
      setBorrowModalOpen(false);
      setSelectedBookForBorrow(null);
      fetchBooks(); // Stok güncellensin
    } catch (err: any) {
      setError(err as ApiError);
      setBorrowModalOpen(false);
    } finally {
      setIsBorrowing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Başlık ve Açıklama */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Kütüphane Kitap Kataloğu</h1>
          <p className="text-sm text-slate-500 mt-1">
            Mevcut kitapları inceleyin, arayın ve kütüphaneden ödünç alın
          </p>
        </div>

        {isAdmin && (
          <Link
            to="/yonetici/kitaplar"
            className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
          >
            <BookmarkPlus className="w-4 h-4" /> Yeni Kitap Ekle
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

      {/* Arama ve Filtreleme Çubuğu */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Kitap adı, yazar, ISBN veya kategori ara..."
              className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm bg-slate-50/50"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium rounded-xl shadow-sm transition-colors"
          >
            Ara
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-slate-100 text-xs sm:text-sm">
          {/* Kategori Filtresi */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setPage(1);
              }}
              className="py-1.5 px-3 rounded-lg border border-slate-200 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              <option value="">Tüm Kategoriler</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          {/* Yalnızca Stokta Olanlar */}
          <label className="flex items-center gap-2 cursor-pointer select-none px-2 py-1 rounded-lg hover:bg-slate-50">
            <input
              type="checkbox"
              checked={availableOnly}
              onChange={(e) => {
                setAvailableOnly(e.target.checked);
                setPage(1);
              }}
              className="rounded border-slate-300 text-brand-600 focus:ring-brand-500"
            />
            <span className="text-slate-700">Yalnızca Stokta Olanlar</span>
          </label>

          {/* Sıralama */}
          <div className="flex items-center gap-2 ml-auto">
            <ArrowUpDown className="w-4 h-4 text-slate-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="py-1.5 px-3 rounded-lg border border-slate-200 bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              <option value="title">Kitap Adı</option>
              <option value="author">Yazar</option>
              <option value="publication_year">Yayın Yılı</option>
              <option value="available_copies">Mevcut Stok</option>
            </select>
            <button
              type="button"
              onClick={() => setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'))}
              className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600"
              title="Sıralama Yönü"
            >
              {sortOrder === 'asc' ? 'A-Z (Artan)' : 'Z-A (Azalan)'}
            </button>
          </div>
        </div>
      </div>

      {/* Kitap Kartları Listesi */}
      {isLoading ? (
        <LoadingSpinner message="Kitaplar listeleniyor..." />
      ) : books.length === 0 ? (
        <EmptyState
          title="Kitap Bulunamadı"
          description="Aradığınız kriterlere uygun kitap kaydı bulunamadı. Filtreleri temizleyip tekrar deneyin."
          action={
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('');
                setAvailableOnly(false);
                setPage(1);
                fetchBooks();
              }}
              className="px-4 py-2 bg-brand-50 text-brand-700 rounded-xl text-sm font-semibold hover:bg-brand-100 transition-colors"
            >
              Filtreleri Temizle
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {books.map((book) => (
            <div
              key={book.id}
              className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-[11px] font-semibold text-brand-600 bg-brand-50 px-2 py-0.5 rounded-md truncate max-w-[150px]">
                    {book.category?.name || 'Genel'}
                  </span>
                  <BookAvailabilityBadge
                    isAvailable={book.is_available}
                    copies={book.available_copies}
                  />
                </div>

                <Link
                  to={`/kitaplar/${book.id}`}
                  className="font-bold text-slate-900 text-base group-hover:text-brand-600 transition-colors line-clamp-2 mb-1"
                >
                  {book.title}
                </Link>

                <p className="text-xs text-slate-500 font-medium mb-3">{book.author}</p>

                {book.description && (
                  <p className="text-xs text-slate-600 line-clamp-2 mb-4 leading-relaxed">
                    {book.description}
                  </p>
                )}

                <div className="space-y-1 text-[11px] text-slate-500 border-t border-slate-100 pt-3">
                  <div className="flex justify-between">
                    <span>ISBN:</span>
                    <span className="font-mono text-slate-700">{book.isbn}</span>
                  </div>
                  {book.shelf_location && (
                    <div className="flex justify-between">
                      <span>Raf Konumu:</span>
                      <span className="font-medium text-slate-700">{book.shelf_location}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>Toplam Kopya:</span>
                    <span className="font-medium text-slate-700">{book.total_copies}</span>
                  </div>
                </div>
              </div>

              {/* Aksiyon Butonları */}
              <div className="pt-4 mt-3 border-t border-slate-100 flex items-center gap-2">
                <Link
                  to={`/kitaplar/${book.id}`}
                  className="flex-1 py-2 px-3 text-center text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors"
                >
                  Ayrıntılar
                </Link>

                {isStudent && (
                  <button
                    disabled={!book.is_available}
                    onClick={() => openBorrowConfirm(book)}
                    className="flex-1 py-2 px-3 text-center text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed rounded-xl transition-colors shadow-sm"
                  >
                    Ödünç Al
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Sayfalama */}
      <Pagination
        currentPage={page}
        totalPages={totalPages}
        totalItems={totalItems}
        pageSize={12}
        onPageChange={(p) => setPage(p)}
      />

      {/* Ödünç Alma Onay Modalı (İş Kuralı & Senaryo Onayı) */}
      <ConfirmDialog
        isOpen={borrowModalOpen}
        title="Kitap Ödünç Alma Onayı"
        isLoading={isBorrowing}
        confirmLabel="Evet, Ödünç Al"
        cancelLabel="Vazgeç"
        variant="primary"
        message={
          <div>
            <p className="mb-2">
              <strong className="text-slate-900 font-semibold">{selectedBookForBorrow?.title}</strong> isimli kitabı ödünç almak üzeresiniz.
            </p>
            <div className="bg-brand-50 p-3 rounded-xl text-xs text-brand-900 space-y-1">
              <p>• Varsayılan ödünç süresi <strong className="font-semibold">14 gün</strong>dür.</p>
              <p>• Aynı anda en fazla <strong className="font-semibold">3 aktif ödünç</strong> kaydınız bulunabilir.</p>
              <p>• Son iade tarihine kadar kütüphaneye teslim etmeniz rica olunur.</p>
            </div>
          </div>
        }
        onConfirm={confirmBorrow}
        onCancel={() => {
          setBorrowModalOpen(false);
          setSelectedBookForBorrow(null);
        }}
      />
    </div>
  );
};
