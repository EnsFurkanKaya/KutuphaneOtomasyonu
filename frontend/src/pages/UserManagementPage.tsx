import React, { useState, useEffect } from 'react';
import { Users, Search, Shield, UserCheck, UserX, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import { User, Page, ApiError } from '../types';
import { formatDate } from '../utils/formatters';
import { Pagination } from '../components/common/Pagination';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { Alert } from '../components/common/Alert';
import { ConfirmDialog } from '../components/common/ConfirmDialog';

export const UserManagementPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<'STUDENT' | 'ADMIN' | ''>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Durum değiştirme modalı
  const [toggleModalOpen, setToggleModalOpen] = useState(false);
  const [targetUser, setTargetUser] = useState<User | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  const fetchUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data: Page<User> = await api.getUsers({
        q: searchTerm || undefined,
        role: roleFilter || undefined,
        page,
        page_size: 15,
      });
      setUsers(data.items);
      setTotalPages(data.pages);
      setTotalItems(data.total);
    } catch (err: any) {
      setError(err as ApiError);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [page, roleFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchUsers();
  };

  const openToggleStatusModal = (u: User) => {
    setTargetUser(u);
    setToggleModalOpen(true);
  };

  const handleToggleStatus = async () => {
    if (!targetUser) return;
    setIsUpdating(true);
    setError(null);
    try {
      await api.adminUpdateUser(targetUser.id, { is_active: !targetUser.is_active });
      setSuccessMessage(
        `"${targetUser.full_name}" kullanıcısı ${
          !targetUser.is_active ? 'aktif hale getirildi' : 'pasifleştirildi'
        }.`
      );
      setToggleModalOpen(false);
      setTargetUser(null);
      fetchUsers();
    } catch (err: any) {
      setError(err as ApiError);
      setToggleModalOpen(false);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Kullanıcı Listesi</h1>
        <p className="text-sm text-slate-500 mt-1">
          Kayıtlı öğrencileri ve sistem yöneticilerini görüntüleyin, aktiflik durumlarını denetleyin
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

      {/* Arama ve Filtre */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row gap-3">
        <form onSubmit={handleSearchSubmit} className="flex-1 flex gap-2">
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Ad soyad, e-posta veya öğrenci numarası..."
              className="w-full pl-11 pr-4 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-brand-500"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium rounded-xl transition-colors"
          >
            Ara
          </button>
        </form>

        <select
          value={roleFilter}
          onChange={(e) => {
            setRoleFilter(e.target.value as any);
            setPage(1);
          }}
          className="px-3 py-2 rounded-xl border border-slate-200 text-sm bg-white font-medium text-slate-700 focus:ring-2 focus:ring-brand-500"
        >
          <option value="">Tüm Roller</option>
          <option value="STUDENT">Öğrenciler</option>
          <option value="ADMIN">Yöneticiler</option>
        </select>
      </div>

      {isLoading ? (
        <LoadingSpinner message="Kullanıcılar listeleniyor..." />
      ) : users.length === 0 ? (
        <EmptyState
          title="Kullanıcı Bulunamadı"
          description="Arama kriterlerine uygun kullanıcı kaydı bulunamadı."
        />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider rounded-xl">
                <tr>
                  <th className="py-3 px-4 rounded-l-xl">Ad Soyad</th>
                  <th className="py-3 px-4">Öğrenci No / Bilgi</th>
                  <th className="py-3 px-4">Rol</th>
                  <th className="py-3 px-4">Durum</th>
                  <th className="py-3 px-4">Kayıt Tarihi</th>
                  <th className="py-3 px-4 text-right rounded-r-xl">Aksiyon</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-slate-900">
                      {u.full_name}
                      <div className="text-xs text-slate-400 font-normal">{u.email}</div>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-600">
                      {u.student_number || '-'}
                    </td>
                    <td className="py-3.5 px-4">
                      {u.role === 'ADMIN' ? (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
                          <Shield className="w-3 h-3" /> Yönetici
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200">
                          Öğrenci
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      {u.is_active ? (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <UserCheck className="w-3 h-3" /> Aktif
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                          <UserX className="w-3 h-3" /> Pasif
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-500">{formatDate(u.created_at)}</td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => openToggleStatusModal(u)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                          u.is_active
                            ? 'bg-rose-50 text-rose-700 hover:bg-rose-100'
                            : 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                        }`}
                      >
                        {u.is_active ? 'Pasifleştir' : 'Aktif Et'}
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
            pageSize={15}
            onPageChange={(p) => setPage(p)}
          />
        </div>
      )}

      {/* Durum Değiştirme Modalı */}
      <ConfirmDialog
        isOpen={toggleModalOpen}
        title="Kullanıcı Aktiflik Durumunu Değiştir"
        isLoading={isUpdating}
        variant={targetUser?.is_active ? 'warning' : 'primary'}
        confirmLabel={targetUser?.is_active ? 'Pasifleştir' : 'Aktif Et'}
        message={
          <div>
            <p className="mb-2">
              <strong className="text-slate-900">{targetUser?.full_name}</strong> kullanıcısını{' '}
              {targetUser?.is_active ? 'pasifleştirmek' : 'aktif hale getirmek'} istediğinize emin misiniz?
            </p>
            {targetUser?.is_active && (
              <p className="text-xs text-amber-700 bg-amber-50 p-2.5 rounded-xl">
                Pasifleştirilen kullanıcılar sisteme yeni ödünç kitap işlemi yapamazlar.
              </p>
            )}
          </div>
        }
        onConfirm={handleToggleStatus}
        onCancel={() => setToggleModalOpen(false)}
      />
    </div>
  );
};
