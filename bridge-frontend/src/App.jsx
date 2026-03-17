import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Search from './pages/Search';
import SpecialistProfile from './pages/SpecialistProfile';
import Dashboard from './pages/Dashboard';
import SpecialistDashboard from './pages/SpecialistDashboard';
import Chats from './pages/Chats';
import ChatRoom from './pages/ChatRoom';
import Requests from './pages/Requests';
import CreateRequest from './pages/CreateRequest';
import RequestDetail from './pages/RequestDetail';
import Settings from './pages/Settings';

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            {/* Public routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected: any authenticated user */}
            <Route path="/search" element={
              <ProtectedRoute><Search /></ProtectedRoute>
            } />
            <Route path="/specialists/:id" element={
              <ProtectedRoute><SpecialistProfile /></ProtectedRoute>
            } />
            <Route path="/chats" element={
              <ProtectedRoute><Chats /></ProtectedRoute>
            } />
            <Route path="/chats/:roomId" element={
              <ProtectedRoute><ChatRoom /></ProtectedRoute>
            } />
            <Route path="/settings" element={
              <ProtectedRoute><Settings /></ProtectedRoute>
            } />

            {/* Client-only routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute requiredRole="client"><Dashboard /></ProtectedRoute>
            } />
            <Route path="/requests/create" element={
              <ProtectedRoute requiredRole="client"><CreateRequest /></ProtectedRoute>
            } />

            {/* Specialist-only routes */}
            <Route path="/dashboard/specialist" element={
              <ProtectedRoute requiredRole="specialist"><SpecialistDashboard /></ProtectedRoute>
            } />

            {/* Requests: any authenticated user */}
            <Route path="/requests" element={
              <ProtectedRoute><Requests /></ProtectedRoute>
            } />
            <Route path="/requests/:id" element={
              <ProtectedRoute><RequestDetail /></ProtectedRoute>
            } />

            {/* Catch-all redirect */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
