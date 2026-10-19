import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Tags, Save, X, BookOpen } from 'lucide-react';
import { api } from '../services/api';
import { Category, ApiError } from '../types';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Alert } from '../components/common/Alert';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { formatDate } from '../utils/formatters';

export const CategoryManagementPage: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Modal Durumu
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form State
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isActive, setIsActive] = useState(true);

  // Silme Modalı
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [catToDelete, setCatToDelete] = useState<Category | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchCategories = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getCategories(true);
      setCategories(data);
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const openCreateModal = () => {
    setEditingCategory(null);
    setName('');
    setDescription('');
    setIsActive(true);
    setModalOpen(true);
  };

  const openEditModal = (cat: Category) => {
    setEditingCategory(cat);
    setName(cat.name);
    setDescription(cat.description || '');
    setIsActive(cat.is_active);
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      if (editingCategory) {
        await api.updateCategory(editingCategory.id, {
          name,
          description: description || undefined,
          is_active: isActive,
        });
        setSuccessMessage(`"${name}" kategorisi başarıyla güncellendi.`);
      } else {
        await api.createCategory({
          name,
          description: description || undefined,
        });
        setSuccessMessage(`"${name}" kategorisi başarıyla oluşturuldu.`);
      }
      setModalOpen(false);
      fetchCategories();
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsSubmitting(false);
    }
  };

  const openDeleteModal = (cat: Category) => {
    setCatToDelete(cat);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!catToDelete) return;
    setIsDeleting(true);
    setError(null);
    try {
      const res = await api.deleteCategory(catToDelete.id);
      setSuccessMessage(res.message);
      setDeleteModalOpen(false);
      fetchCategories();
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
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Kategori Yönetimi</h1>
          <p className="text-sm text-slate-500 mt-1">
            Kütüphane kitap kategorilerini tanımlayın, güncelleyin ve düzenleyin
          </p>
        </div>

        <button
          onClick={openCreateModal}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-semibold shadow-sm transition-all"
        >
          <Plus className="w-4 h-4" /> Yeni Kategori Ekle
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

      {isLoading ? (
        <LoadingSpinner message="Kategoriler getiriliyor..." />
      ) : categories.length === 0 ? (
        <EmptyState
          title="Kategori Bulunamadı"
          description="Sistemde henüz bir kategori tanımlanmamış."
          action={
            <button
              onClick={openCreateModal}
              className="px-4 py-2 bg-brand-600 text-white rounded-xl text-sm font-semibold"
            >
              İlk Kategoriyi Ekle
            </button>
          }
        />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider rounded-xl">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Kategori Adı</th>
                  <th className="py-3 px-4">Açıklama</th>
                  <th className="py-3 px-4">Bağlı Kitap Sayısı</th>
                  <th className="py-3 px-4">Durum</th>
                  <th className="py-3 px-4">Oluşturulma</th>
                  <th className="py-3 px-4 text-right rounded-r-xl">Aksiyonlar</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {categories.map((cat) => (
                  <tr key={cat.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-slate-900">
                      <div className="flex items-center gap-2">
                        <Tags className="w-4 h-4 text-brand-500" />
                        {cat.name}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 max-w-xs truncate">
                      {cat.description || '-'}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-800">
                      <span className="inline-flex items-center gap-1 bg-slate-100 px-2.5 py-0.5 rounded-lg text-xs">
                        <BookOpen className="w-3.5 h-3.5 text-slate-500" /> {cat.book_count} Kitap
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      {cat.is_active ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          Aktif
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                          Pasif
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-500">{formatDate(cat.created_at)}</td>
                    <td className="py-3.5 px-4 text-right space-x-1">
                      <button
                        onClick={() => openEditModal(cat)}
                        className="p-1.5 text-slate-600 hover:text-brand-600 hover:bg-slate-100 rounded-lg transition-colors"
                        title="Düzenle"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => openDeleteModal(cat)}
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
        </div>
      )}

      {/* Kategori Ekleme / Düzenleme Modalı */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full shadow-2xl border border-slate-100 overflow-hidden">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-900">
                {editingCategory ? 'Kategoriyi Düzenle' : 'Yeni Kategori Ekle'}
              </h3>
              <button
                onClick={() => setModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Kategori Adı *
                </label>
                <input
                  type="text"
                  required
                  minLength={2}
                  maxLength={80}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Örn: Bilgisayar & Yazılım"
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Açıklama
                </label>
                <textarea
                  rows={3}
                  maxLength={500}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Kategori hakkında kısa açıklama..."
                  className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
                />
              </div>

              {editingCategory && (
                <div className="flex items-center gap-2 pt-2">
                  <input
                    type="checkbox"
                    id="cat_active"
                    checked={isActive}
                    onChange={(e) => setIsActive(e.target.checked)}
                    className="rounded text-brand-600 focus:ring-brand-500"
                  />
                  <label htmlFor="cat_active" className="text-sm font-medium text-slate-700 cursor-pointer">
                    Kategori aktif olsun
                  </label>
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
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

      {/* Silme / Pasifleştirme Modalı */}
      <ConfirmDialog
        isOpen={deleteModalOpen}
        title="Kategori Silme"
        isLoading={isDeleting}
        variant="danger"
        confirmLabel="Onayla"
        message={
          <div>
            <p className="mb-2">
              <strong className="text-slate-900">{catToDelete?.name}</strong> kategorisini silmek istediğinizden emin misiniz?
            </p>
            {catToDelete && catToDelete.book_count > 0 ? (
              <div className="bg-amber-50 p-3 rounded-xl text-xs text-amber-800">
                Bu kategoriye bağlı <strong>{catToDelete.book_count} adet kitap</strong> bulunmaktadır. Kitapların ilişkisini bozmamak için kategori <strong>silinmeyecek, pasifleştirilecektir</strong>.
              </div>
            ) : (
              <p className="text-xs text-slate-500">
                Bu kategoriye bağlı kitap bulunmadığı için veritabanından kalıcı olarak silinecektir.
              </p>
            )}
          </div>
        }
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteModalOpen(false)}
      />
    </div>
  );
};
