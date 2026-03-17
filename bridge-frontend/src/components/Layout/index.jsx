import { useEffect } from 'react';
import { Link, Outlet } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

export default function Layout() {
  const { isAuthenticated, user, logout, fetchUser } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated && !user) {
      fetchUser();
    }
  }, [isAuthenticated, user, fetchUser]);

  const isClient = user?.role === 'client';
  const isSpecialist = user?.role === 'specialist';
  const dashboardPath = isSpecialist
    ? '/dashboard/specialist'
    : '/dashboard';

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-border px-6 py-3 flex items-center justify-between h-16">
        <Link
          to={isAuthenticated ? dashboardPath : '/'}
          className="text-xl font-bold text-primary"
        >
          Bridge
        </Link>
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <>
              {isClient && (
                <Link
                  to="/requests/create"
                  className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors"
                >
                  Create Task
                </Link>
              )}
              <Link
                to="/requests"
                className="text-sm text-text-secondary hover:text-primary transition-colors"
              >
                {isClient ? 'My Requests' : 'Requests'}
              </Link>
              <Link
                to="/chats"
                className="text-sm text-text-secondary hover:text-primary transition-colors"
              >
                Messages
              </Link>
              <Link
                to={dashboardPath}
                className="text-sm text-text-secondary hover:text-primary transition-colors"
              >
                Dashboard
              </Link>
              <Link
                to="/settings"
                className="text-sm text-text-secondary hover:text-primary transition-colors"
              >
                Settings
              </Link>
              <button
                onClick={logout}
                className="text-sm text-error hover:underline"
              >
                Log Out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm text-text-secondary hover:text-primary transition-colors"
              >
                Log In
              </Link>
              <Link
                to="/register"
                className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
