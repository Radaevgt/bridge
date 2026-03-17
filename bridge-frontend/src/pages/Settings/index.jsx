import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import useAuthStore from '../../store/authStore';
import api from '../../api/axios';

export default function Settings() {
  const { user, fetchUser, logout } = useAuthStore();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [message, setMessage] = useState('');

  const updateMutation = useMutation({
    mutationFn: (data) => api.patch('/users/me', data),
    onSuccess: () => {
      fetchUser();
      setMessage('Settings saved successfully!');
      setTimeout(() => setMessage(''), 3000);
    },
    onError: (err) => {
      setMessage(err.response?.data?.detail || 'Failed to save settings.');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    updateMutation.mutate({ full_name: fullName });
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold text-primary-dark mb-8">Settings</h1>

      <div className="bg-white border border-border rounded-xl p-6 mb-6">
        <h2 className="text-lg font-semibold text-primary-dark mb-4">Account Information</h2>

        {message && (
          <p className={`text-sm mb-4 ${message.includes('success') ? 'text-success' : 'text-error'}`}>
            {message}
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1">Email</label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full border border-border rounded-lg px-4 py-2.5 text-sm text-text-secondary bg-gray-50 cursor-not-allowed"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1">Role</label>
            <input
              type="text"
              value={user?.role || ''}
              disabled
              className="w-full border border-border rounded-lg px-4 py-2.5 text-sm text-text-secondary bg-gray-50 cursor-not-allowed capitalize"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <button
            type="submit"
            disabled={updateMutation.isPending}
            className="bg-primary text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-50"
          >
            {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>

      <div className="bg-white border border-border rounded-xl p-6">
        <h2 className="text-lg font-semibold text-primary-dark mb-2">Danger Zone</h2>
        <p className="text-text-secondary text-sm mb-4">Log out of your account on this device.</p>
        <button
          onClick={logout}
          className="border border-error text-error px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors"
        >
          Log Out
        </button>
      </div>
    </div>
  );
}
