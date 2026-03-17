import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { loginUser } from '../../api/auth';
import useAuthStore from '../../store/authStore';

const schema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(1, 'Password is required'),
});

export default function Login() {
  const navigate = useNavigate();
  const { setTokens, fetchUser } = useAuthStore();
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (formData) => {
    setLoading(true);
    setApiError('');
    try {
      const { data } = await loginUser(formData);
      setTokens(data.access_token, data.refresh_token);
      await fetchUser();
      const currentUser = useAuthStore.getState().user;
      navigate(currentUser?.role === 'specialist' ? '/dashboard/specialist' : '/dashboard');
    } catch (err) {
      setApiError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white rounded-xl border border-border p-8">
        <h1 className="text-2xl font-bold text-primary-dark text-center mb-2">Welcome back</h1>
        <p className="text-text-secondary text-center mb-8">Sign in to your Bridge account</p>

        {apiError && (
          <div className="bg-red-50 border border-error text-error rounded-lg px-4 py-3 mb-6 text-sm">
            {apiError}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-1">Email</label>
            <input
              type="email"
              {...register('email')}
              className="w-full border border-border rounded-lg px-4 py-2.5 text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="you@example.com"
            />
            {errors.email && <p className="text-error text-sm mt-1">{errors.email.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-1">Password</label>
            <input
              type="password"
              {...register('password')}
              className="w-full border border-border rounded-lg px-4 py-2.5 text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="Enter your password"
            />
            {errors.password && <p className="text-error text-sm mt-1">{errors.password.message}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-white font-medium py-2.5 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="text-text-secondary text-sm text-center mt-6">
          Don&apos;t have an account?{' '}
          <Link to="/register" className="text-primary font-medium hover:underline">Register</Link>
        </p>
      </div>
    </div>
  );
}
