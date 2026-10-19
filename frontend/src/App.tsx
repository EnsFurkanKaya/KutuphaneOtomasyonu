import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { MainLayout } from './layouts/MainLayout';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// Sayfalar
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { BookListPage } from './pages/BookListPage';
import { BookDetailPage } from './pages/BookDetailPage';
import { StudentDashboard } from './pages/StudentDashboard';
import { MyLoansPage } from './pages/MyLoansPage';
import { LoanHistoryPage } from './pages/LoanHistoryPage';
import { AdminDashboard } from './pages/AdminDashboard';
import { BookManagementPage } from './pages/BookManagementPage';
import { CategoryManagementPage } from './pages/CategoryManagementPage';
import { LoanManagementPage } from './pages/LoanManagementPage';
import { OverdueReportPage } from './pages/OverdueReportPage';
import { UserManagementPage } from './pages/UserManagementPage';
import { ProfilePage } from './pages/ProfilePage';
import { NotFoundPage } from './pages/NotFoundPage';
import { ForbiddenPage } from './pages/ForbiddenPage';

// Yetkilendirme Korumaları
const ProtectedRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingSpinner message="Oturum doğrulanıyor..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/giris" state={{ from: location }} replace />;
  }

  return children;
};

const AdminRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const { isAuthenticated, isAdmin, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner message="Yetki kontrol ediliyor..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/giris" replace />;
  }

  if (!isAdmin) {
    return <Navigate to="/yetkisiz" replace />;
  }

  return children;
};

const StudentRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const { isAuthenticated, isStudent, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner message="Yetki kontrol ediliyor..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/giris" replace />;
  }

  if (!isStudent) {
    return <Navigate to="/yetkisiz" replace />;
  }

  return children;
};

const HomeRedirect: React.FC = () => {
  const { isAuthenticated, isAdmin, isStudent, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner message="Yönlendiriliyor..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/kitaplar" replace />;
  }

  if (isAdmin) {
    return <Navigate to="/yonetici" replace />;
  }

  return <Navigate to="/ogrenci" replace />;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Genel Açık Sayfalar */}
          <Route path="/giris" element={<LoginPage />} />
          <Route path="/kayit" element={<RegisterPage />} />

          {/* Ana Düzen (MainLayout) İçindeki Sayfalar */}
          <Route element={<MainLayout />}>
            <Route path="/" element={<HomeRedirect />} />
            <Route path="/kitaplar" element={<BookListPage />} />
            <Route path="/kitaplar/:id" element={<BookDetailPage />} />

            {/* Öğrenciye Özel Sayfalar */}
            <Route
              path="/ogrenci"
              element={
                <StudentRoute>
                  <StudentDashboard />
                </StudentRoute>
              }
            />
            <Route
              path="/odunclerim"
              element={
                <StudentRoute>
                  <MyLoansPage />
                </StudentRoute>
              }
            />
            <Route
              path="/odunc-gecmisi"
              element={
                <StudentRoute>
                  <LoanHistoryPage />
                </StudentRoute>
              }
            />

            {/* Ortak Oturum Açılmış Sayfalar */}
            <Route
              path="/profil"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />

            {/* Yöneticiye Özel Sayfalar */}
            <Route
              path="/yonetici"
              element={
                <AdminRoute>
                  <AdminDashboard />
                </AdminRoute>
              }
            />
            <Route
              path="/yonetici/kitaplar"
              element={
                <AdminRoute>
                  <BookManagementPage />
                </AdminRoute>
              }
            />
            <Route
              path="/yonetici/kategoriler"
              element={
                <AdminRoute>
                  <CategoryManagementPage />
                </AdminRoute>
              }
            />
            <Route
              path="/yonetici/oduncler"
              element={
                <AdminRoute>
                  <LoanManagementPage />
                </AdminRoute>
              }
            />
            <Route
              path="/yonetici/gecikme-raporu"
              element={
                <AdminRoute>
                  <OverdueReportPage />
                </AdminRoute>
              }
            />
            <Route
              path="/yonetici/kullanicilar"
              element={
                <AdminRoute>
                  <UserManagementPage />
                </AdminRoute>
              }
            />

            {/* Hata Sayfaları */}
            <Route path="/yetkisiz" element={<ForbiddenPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};
