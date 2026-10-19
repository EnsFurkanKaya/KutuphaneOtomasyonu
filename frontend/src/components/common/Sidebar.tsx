import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  BookOpen,
  LayoutDashboard,
  BookmarkCheck,
  History,
  Tags,
  ClipboardList,
  AlertOctagon,
  Users,
  UserCheck,
  X,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { isAdmin, isStudent } = useAuth();

  const studentLinks = [
    { to: '/ogrenci', label: 'Kontrol Paneli', icon: LayoutDashboard },
    { to: '/kitaplar', label: 'Kitap Kataloğu & Arama', icon: BookOpen },
    { to: '/odunclerim', label: 'Aktif Ödünçlerim', icon: BookmarkCheck },
    { to: '/odunc-gecmisi', label: 'Ödünç Geçmişim', icon: History },
    { to: '/profil', label: 'Profil Bilgilerim', icon: UserCheck },
  ];

  const adminLinks = [
    { to: '/yonetici', label: 'Genel Bakış & Panel', icon: LayoutDashboard },
    { to: '/kitaplar', label: 'Kitap Kataloğu', icon: BookOpen },
    { to: '/yonetici/kitaplar', label: 'Kitap Yönetimi (Ekle/Düzenle)', icon: BookmarkCheck },
    { to: '/yonetici/kategoriler', label: 'Kategori Yönetimi', icon: Tags },
    { to: '/yonetici/oduncler', label: 'Tüm Ödünç İşlemleri', icon: ClipboardList },
    { to: '/yonetici/gecikme-raporu', label: 'Gecikme Raporu', icon: AlertOctagon },
    { to: '/yonetici/kullanicilar', label: 'Kullanıcı Listesi', icon: Users },
    { to: '/profil', label: 'Yönetici Profili', icon: UserCheck },
  ];

  const links = isAdmin ? adminLinks : isStudent ? studentLinks : [];

  return (
    <>
      {/* Mobil Karartma Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Paneli */}
      <aside
        className={`fixed lg:sticky top-16 z-40 h-[calc(100vh-4rem)] w-64 bg-white border-r border-slate-200 transition-transform duration-200 ease-in-out overflow-y-auto ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="p-4 flex items-center justify-between lg:hidden border-b border-slate-100">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Navigasyon
          </span>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-100 text-slate-500"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="p-4 space-y-1.5">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-3 py-1">
            {isAdmin ? 'Yönetim Modülü' : 'Öğrenci Kütüphanesi'}
          </div>

          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === '/kitaplar' || link.to === '/ogrenci' || link.to === '/yonetici'}
                onClick={() => onClose()}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-brand-50 text-brand-700 font-semibold shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      className={`w-4 h-4 shrink-0 ${
                        isActive ? 'text-brand-600' : 'text-slate-400 group-hover:text-slate-600'
                      }`}
                    />
                    <span className="truncate">{link.label}</span>
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </aside>
    </>
  );
};
