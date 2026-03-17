# React + TanStack Query + Zustand Skill

> Trigger: React components, data fetching, state management, hooks, forms

## TanStack Query v5 Patterns

### Fetching Data (useQuery)
```jsx
import { useQuery } from '@tanstack/react-query';
import { searchSpecialists } from '../api/specialists';

export default function SpecialistList({ filters }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['specialists', filters],
    queryFn: () => searchSpecialists(filters).then(res => res.data),
  });

  if (isLoading) return <SkeletonList />;   // Loading skeletons, NOT spinners
  if (error) return <ErrorState message={error.message} />;
  if (!data?.length) return <EmptyState text="No specialists found" cta="Adjust filters" />;

  return data.map(s => <SpecialistCard key={s.id} specialist={s} />);
}
```

### Mutations (useMutation)
```jsx
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createReview } from '../api/reviews';

function ReviewForm({ specialistId }) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data) => createReview(specialistId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', specialistId] });
      // Show success toast
    },
    onError: (error) => {
      // Show error toast
    },
  });

  return (
    <form onSubmit={handleSubmit(data => mutation.mutate(data))}>
      <button disabled={mutation.isPending}>
        {mutation.isPending ? 'Submitting...' : 'Submit Review'}
      </button>
    </form>
  );
}
```

## Zustand Store Pattern
```jsx
import { create } from 'zustand';

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,

  setUser: (user) => set({ user, isAuthenticated: true }),
  logout: () => {
    localStorage.removeItem('access_token');
    set({ user: null, isAuthenticated: false });
  },
}));

// Usage in component:
const { user, isAuthenticated } = useAuthStore();
```

## React Hook Form + Zod
```jsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

function LoginForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(schema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} className="..." />
      {errors.email && <p className="text-error text-sm">{errors.email.message}</p>}
    </form>
  );
}
```

## Rules
- **Loading skeletons** (not spinners) for lists
- **Empty states** with helpful text + CTA button
- **Every form**: loading + error + success states
- Components in `src/components/Name/index.jsx`
- Pages in `src/pages/Name/index.jsx`
- API calls in `src/api/` — one file per resource
- Stores in `src/store/` — one file per domain
