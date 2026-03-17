import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '../../api/auth';
import useAuthStore from '../../store/authStore';

const schema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  role: z.enum(['client', 'specialist'], { required_error: 'Choose a role' }),
});

export default function Register() {
  const navigate = useNavigate();
  const { setTokens, fetchUser } = useAuthStore();
  const [apiError, setApiError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  });

  const selectedRole = watch('role');

  const onSubmit = async (formData) => {
    setLoading(true);
    setApiError('');
    try {
      const { data } = await registerUser(formData);
      setTokens(data.access_token, data.refresh_token);
      await fetchUser();
      navigate(formData.role === 'specialist' ? '/dashboard/specialist' : '/requests/create');
    } catch (err) {
      setApiError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center bg-gray-50 px-4 py-8">
      <div className="w-full max-w-md bg-white rounded-xl border border-border p-8">
        <h1 className="text-2xl font-bold text-primary-dark text-center mb-2">Create your account</h1>
        <p className="text-text-secondary text-center mb-8">Join Bridge to connect with experts</p>

        {apiError && (
          <div className="bg-red-50 border border-error text-error rounded-lg px-4 py-3 mb-6 text-sm">
            {apiError}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">I want to...</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setValue('role', 'client', { shouldValidate: true })}
                className={`border rounded-lg p-4 text-center transition-all ${
                  selectedRole === 'client'
                    ? 'border-primary bg-primary-light text-primary font-medium'
                    : 'border-border text-text-secondary hover:border-primary/50'
                }`}
              >
                <div className="text-2xl mb-1">&#128269;</div>
                <div className="text-sm font-medium">Find Experts</div>
                <div className="text-xs text-text-secondary mt-1">I need help</div>
              </button>
              <button
                type="button"
                onClick={() => setValue('role', 'specialist', { shouldValidate: true })}
                className={`border rounded-lg p-4 text-center transition-all ${
                  selectedRole === 'specialist'
                    ? 'border-primary bg-primary-light text-primary font-medium'
                    : 'border-border text-text-secondary hover:border-primary/50'
                }`}
              >
                <div className="text-2xl mb-1">&#127891;</div>
                <div className="text-sm font-medium">Be an Expert</div>
                <div className="text-xs text-text-secondary mt-1">I offer services</div>
              </button>
            </div>
            {errors.role && <p className="text-error text-sm mt-1">{errors.role.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-1">Full Name</label>
            <input
              type="text"
              {...register('full_name')}
              className="w-full border border-border rounded-lg px-4 py-2.5 text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="John Doe"
            />
            {errors.full_name && <p className="text-error text-sm mt-1">{errors.full_name.message}</p>}
          </div>

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
              placeholder="At least 8 characters"
            />
            {errors.password && <p className="text-error text-sm mt-1">{errors.password.message}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-white font-medium py-2.5 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="text-text-secondary text-sm text-center mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-primary font-medium hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
