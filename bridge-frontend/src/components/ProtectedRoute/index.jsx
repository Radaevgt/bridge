import { Navigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

export default function ProtectedRoute({ children, requiredRole }) {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // If role check is needed but user data hasn't loaded yet, wait
  if (requiredRole && !user) {
    return null;
  }

  if (requiredRole && user.role !== requiredRole) {
    const fallback =
      user.role === 'specialist' ? '/dashboard/specialist' : '/dashboard';
    return <Navigate to={fallback} replace />;
  }

  return children;
}
