import React, { useState, useEffect } from 'react';
import {
  Plus,
  Edit,
  Trash2,
  Search,
  Layers,
  Save,
  X,
  CheckCircle,
  AlertTriangle,
  RotateCcw,
} from 'lucide-react';
import { api } from '../services/api';
import { Book, Category, Page, ApiError } from '../types';
import { BookAvailabilityBadge } from '../components/common/StatusBadge';
import { Pagination } from '../components/common/Pagination';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Alert } from '../components/common/Alert';
import { ConfirmDialog } from '../components/common/ConfirmDialog';

export const BookManagementPage: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Modal Durumları
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form Değerleri
  const [formData, setFormData] = useState({
    isbn: '',
    title: '',
    author: '',
    publisher: '',
    publication_year: '',
    category_id: '',
    shelf_location: '',
    total_copies: 1,
    description: '',
    is_active: true,
  });

  // Stok Güncelleme Modalı
  const [stockModalOpen, setStockModalOpen] = useState(false);
  const [stockBook, setStockBook] = useState<Book | null>(null);
  const [newTotalCopies, setNewTotalCopies] = useState<number>(1);
  const [isUpdatingStock, setIsUpdatingStock] = useState(false);

  // Silme / Pasifleştirme Modalı
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [bookToDelete, setBookToDelete] = useState<Book | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchCategories = async () => {
    try {
      const data = await api.getCategories(true);
      setCategories(data);
    } catch {}
  };

  const fetchBooks = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data: Page<Book> = await api.getBooks({
        q: searchTerm || undefined,
        include_inactive: true,
        page,
        page_size: 10,
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
  }, [page]);

  const openCreateModal = () => {
    setEditingBook(null);
    setFormData({
      isbn: '',
      title: '',
      author: '',
      publisher: '',
      publication_year: '',
      category_id: categories[0]?.id ? String(categories[0].id) : '',
      shelf_location: '',
      total_copies: 1,
      description: '',
      is_active: true,
    });
    setEditModalOpen(true);
  };

  const openEditModal = (book: Book) => {
    setEditingBook(book);
    setFormData({
      isbn: book.isbn,
      title: book.title,
      author: book.author,
      publisher: book.publisher || '',
      publication_year: book.publication_year ? String(book.publication_year) : '',
      category_id: book.category_id ? String(book.category_id) : '',
      shelf_location: book.shelf_location || '',
      total_copies: book.total_copies,
      description: book.description || '',
      is_active: book.is_active,
    });
    setEditModalOpen(true);
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const payload: any = {
      isbn: formData.isbn,
      title: formData.title,
      author: formData.author,
      publisher: formData.publisher || undefined,
      publication_year: formData.publication_year ? Number(formData.publication_year) : undefined,
      category_id: formData.category_id ? Number(formData.category_id) : undefined,
      shelf_location: formData.shelf_location || undefined,
      description: formData.description || undefined,
    };

    try {
      if (editingBook) {
        payload.is_active = formData.is_active;
        await api.updateBook(editingBook.id, payload);
        setSuccessMessage(`"${formData.title}" başarıyla güncellendi.`);
      } else {
        payload.total_copies = Number(formData.total_copies);
        await api.createBook(payload);
        setSuccessMessage(`"${formData.title}" sisteme başarıyla eklendi.`);
      }
      setEditModalOpen(false);
      fetchBooks();
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsSubmitting(false);
    }
  };

  const openStockModal = (book: Book) => {
    setStockBook(book);
    setNewTotalCopies(book.total_copies);
    setStockModalOpen(true);
  };

  const handleStockSubmit = async () => {
    if (!stockBook) return;
    setIsUpdatingStock(true);
    setError(null);
    try {
      await api.updateBookStock(stockBook.id, newTotalCopies);
      setSuccessMessage(`"${stockBook.title}" stok sayısı güncellendi.`);
      setStockModalOpen(false);
      fetchBooks();
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsUpdatingStock(false);
    }
  };

  const openDeleteModal = (book: Book) => {
    setBookToDelete(book);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!bookToDelete) return;
    setIsDeleting(true);
    setError(null);
    try {
      const res = await api.deleteBook(bookToDelete.id);
      setSuccessMessage(res.message);
      setDeleteModalOpen(false);
      fetchBooks();
    } catch (err: any) {
      setError(err as ApiError);
      setDeleteModalOpen(false);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Kitap Yönetimi</h1>
          <p className="text-sm text-slate-500 mt-1">
            Yeni kitap ekleyin, stokları yönetin ve kütüphane envanterini güncelleyin
          </p>
        </div>

        <button
          onClick={openCreateModal}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
        >
          <Plus className="w-4 h-4" /> Yeni Kitap Ekle
        </button>
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

      {/* Arama */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            setPage(1);
            fetchBooks();
          }}
          className="flex gap-2"
        >
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Başlık, yazar, ISBN ara..."
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
      </div>

      {isLoading ? (
        <LoadingSpinner message="Kitaplar getiriliyor..." />
      ) : books.length === 0 ? (
        <EmptyState
          title="Kitap Bulunamadı"
          description="Sistemde kayıtlı kitap bulunmuyor."
          action={
            <button
              onClick={openCreateModal}
              className="px-4 py-2 bg-brand-600 text-white rounded-xl text-sm font-semibold"
            >
              İlk Kitabı Ekle
            </button>
          }
        />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider rounded-xl">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Kitap Bilgisi</th>
                  <th className="py-3 px-4">Kategori</th>
                  <th className="py-3 px-4">Raf</th>
                  <th className="py-3 px-4">Stok (Uygun / Toplam)</th>
                  <th className="py-3 px-4">Aktiflik</th>
                  <th className="py-3 px-4 text-right rounded-r-xl">Aksiyonlar</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {books.map((book) => (
                  <tr key={book.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{book.title}</div>
                      <div className="text-xs text-slate-500">
                        {book.author} • <span className="font-mono text-slate-400">{book.isbn}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-xs font-medium text-slate-700 bg-slate-100 px-2.5 py-1 rounded-lg">
                        {book.category?.name || 'Genel'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-medium">
                      {book.shelf_location || '-'}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900">{book.available_copies}</span>
                        <span className="text-slate-400">/</span>
                        <span className="text-slate-600">{book.total_copies}</span>
                        <button
                          onClick={() => openStockModal(book)}
                          className="p-1 hover:bg-slate-200 text-slate-500 rounded-md ml-1"
                          title="Stok Güncelle"
                        >
                          <Layers className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      {book.is_active ? (
                        <span className="inline-flex items-center gap-1 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full font-semibold border border-emerald-200">
                          Aktif
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-full font-semibold border border-slate-200">
                          Pasif
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right space-x-1">
                      <button
                        onClick={() => openEditModal(book)}
                        className="p-1.5 text-slate-600 hover:text-brand-600 hover:bg-slate-100 rounded-lg transition-colors"
                        title="Düzenle"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => openDeleteModal(book)}
                        className="p-1.5 text-slate-600 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                        title="Sil / Pasifleştir"
                      >
                        <Trash2 className="w-4 h-4" />
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

      {/* Kitap Ekleme / Düzenleme Modalı */}
      {editModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-3xl max-w-xl w-full shadow-2xl border border-slate-100 overflow-hidden my-8">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-900">
                {editingBook ? 'Kitap Bilgilerini Düzenle' : 'Yeni Kitap Ekle'}
              </h3>
              <button
                onClick={() => setEditModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleFormSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    ISBN Numarası *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.isbn}
                    onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                    placeholder="9780000000000"
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Kategori
                  </label>
                  <select
                    value={formData.category_id}
                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500 bg-white"
                  >
                    <option value="">Seçiniz...</option>
                    {categories.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Kitap Adı *
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Kitap başlığı"
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Yazar *
                </label>
                <input
                  type="text"
                  required
                  value={formData.author}
                  onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                  placeholder="Yazar adı"
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Yayınevi
                  </label>
                  <input
                    type="text"
                    value={formData.publisher}
                    onChange={(e) => setFormData({ ...formData, publisher: e.target.value })}
                    placeholder="Yayınevi"
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Yayın Yılı
                  </label>
                  <input
                    type="number"
                    value={formData.publication_year}
                    onChange={(e) => setFormData({ ...formData, publication_year: e.target.value })}
                    placeholder="2023"
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Raf Konumu
                  </label>
                  <input
                    type="text"
                    value={formData.shelf_location}
                    onChange={(e) => setFormData({ ...formData, shelf_location: e.target.value })}
                    placeholder="A-101"
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </div>

              {!editingBook && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Toplam Kopya Sayısı (Başlangıç Stoğu) *
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={10000}
                    required
                    value={formData.total_copies}
                    onChange={(e) => setFormData({ ...formData, total_copies: Number(e.target.value) })}
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              )}

              {editingBook && (
                <div className="flex items-center gap-2 pt-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="rounded text-brand-600 focus:ring-brand-500"
                  />
                  <label htmlFor="is_active" className="text-sm font-medium text-slate-700 cursor-pointer">
                    Kitap aktif durumda olsun (ödünç verilmeye açık)
                  </label>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Açıklama / Özet
                </label>
                <textarea
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Kitap hakkında özet bilgi..."
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setEditModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Vazgeç
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all disabled:opacity-50 flex items-center gap-1.5"
                >
                  <Save className="w-4 h-4" />
                  {isSubmitting ? 'Kaydediliyor...' : 'Kaydet'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Stok Güncelleme Modalı */}
      <ConfirmDialog
        isOpen={stockModalOpen}
        title="Kitap Stok Sayısını Güncelle"
        isLoading={isUpdatingStock}
        confirmLabel="Stoku Güncelle"
        message={
          <div className="space-y-3">
            <p className="text-sm">
              <strong className="text-slate-900">{stockBook?.title}</strong> için toplam fiziksel kopya sayısını giriniz:
            </p>
            <input
              type="number"
              min={0}
              max={10000}
              value={newTotalCopies}
              onChange={(e) => setNewTotalCopies(Number(e.target.value))}
              className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-brand-500"
            />
            <p className="text-xs text-slate-500">
              Mevcut uygun stok, ödünçte bulunan kopyalar dikkate alınarak otomatik olarak hesaplanacaktır.
            </p>
          </div>
        }
        onConfirm={handleStockSubmit}
        onCancel={() => setStockModalOpen(false)}
      />

      {/* Silme / Pasifleştirme Modalı */}
      <ConfirmDialog
        isOpen={deleteModalOpen}
        title="Kitap Silme / Pasifleştirme"
        isLoading={isDeleting}
        variant="danger"
        confirmLabel="Onayla"
        message={
          <div>
            <p className="mb-2">
              <strong className="text-slate-900">{bookToDelete?.title}</strong> kitabını silmek istediğinizden emin misiniz?
            </p>
            <div className="bg-amber-50 p-3 rounded-xl text-xs text-amber-800 space-y-1">
              <p>• Eğer kitabın geçmiş veya aktif ödünç kaydı varsa, veri geçmişini korumak için <strong>fiziksel olarak silinmez, pasifleştirilir</strong>.</p>
              <p>• Hiçbir ödünç kaydı bulunmayan kitaplar veritabanından kalıcı olarak silinir.</p>
            </div>
          </div>
        }
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteModalOpen(false)}
      />
    </div>
  );
};
