import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import AppLayout from './components/layout/AppLayout';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoginPage from './features/auth/LoginPage';
import RegisterPage from './features/auth/RegisterPage';
import SemanticCatalog from './features/semantic-catalog/SemanticCatalog';
import DataSourcesPage from './features/data-sources/DataSourcesPage';
import QueryBuilder from './features/query-builder/QueryBuilder';

export default function App() {
  return (
    <ConfigProvider theme={{ token: { colorPrimary: '#1890ff' } }}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/catalog" element={<SemanticCatalog />} />
              <Route path="/data-sources" element={<DataSourcesPage />} />
              <Route path="/query-builder" element={<QueryBuilder />} />
              <Route path="/" element={<Navigate to="/catalog" replace />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}
