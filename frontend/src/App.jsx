import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import BrowsePage from './pages/BrowsePage.jsx';
import ItemDetailPage from './pages/ItemDetailPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import AdminLayout from './pages/admin/AdminLayout.jsx';
import ItemsAdminPage from './pages/admin/ItemsAdminPage.jsx';
import ClaimsPage from './pages/admin/ClaimsPage.jsx';
import HistoryPage from './pages/admin/HistoryPage.jsx';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<BrowsePage />} />
        <Route path="/items/:id" element={<ItemDetailPage />} />
        <Route path="/admin/login" element={<LoginPage />} />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="items" replace />} />
          <Route path="items" element={<ItemsAdminPage />} />
          <Route path="claims" element={<ClaimsPage />} />
          <Route path="history" element={<HistoryPage />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

function NotFound() {
  return (
    <section className="page narrow">
      <h1>Page not found</h1>
      <p>The page you opened does not exist. Go back to the list of found items.</p>
    </section>
  );
}
