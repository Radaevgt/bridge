import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { searchSpecialists } from '../../api/specialists';
import SpecialistCard from '../../components/SpecialistCard';
import FilterPanel from '../../components/FilterPanel';
import useAuthStore from '../../store/authStore';

function SkeletonCard() {
  return (
    <div className="bg-white border border-border rounded-xl p-5 animate-pulse">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-gray-200" />
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
          <div className="h-3 bg-gray-200 rounded w-2/3" />
        </div>
      </div>
      <div className="h-3 bg-gray-200 rounded w-full mt-4" />
      <div className="h-3 bg-gray-200 rounded w-4/5 mt-2" />
      <div className="flex gap-2 mt-4">
        <div className="h-5 bg-gray-200 rounded w-14" />
        <div className="h-5 bg-gray-200 rounded w-14" />
      </div>
    </div>
  );
}

export default function Search() {
  const { user } = useAuthStore();
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({ sort: 'rating' });
  const [page, setPage] = useState(1);

  const params = {
    ...(search && { search }),
    ...(filters.domain && { domain: filters.domain }),
    ...(filters.language && { language: filters.language }),
    ...(filters.min_price && { min_price: filters.min_price }),
    ...(filters.max_price && { max_price: filters.max_price }),
    ...(filters.min_rating && { min_rating: filters.min_rating }),
    ...(filters.availability_only && { availability_only: true }),
    sort: filters.sort || 'rating',
    page,
  };

  const { data, isLoading, isError } = useQuery({
    queryKey: ['specialists', params],
    queryFn: () => searchSpecialists(params),
  });

  const specialists = data?.data || [];

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold text-primary-dark mb-6">Find Specialists</h1>

      {user?.role === 'client' && (
        <div className="bg-primary-light border border-primary/20 rounded-xl p-4 mb-6 flex items-center justify-between">
          <p className="text-sm text-primary">
            Looking for help? Create a task and let specialists come to you.
          </p>
          <Link
            to="/requests/create"
            className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors flex-shrink-0 ml-4"
          >
            Create Task
          </Link>
        </div>
      )}

      {/* Search bar */}
      <div className="mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          placeholder="Search by name, headline, or expertise..."
          className="w-full border border-border rounded-xl px-5 py-3 text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
        />
      </div>

      <div className="flex gap-6">
        {/* Sidebar filters */}
        <aside className="w-64 flex-shrink-0 hidden lg:block">
          <FilterPanel
            filters={filters}
            onFilterChange={(f) => { setFilters(f); setPage(1); }}
          />
        </aside>

        {/* Results */}
        <div className="flex-1">
          {isLoading ? (
            <div className="grid gap-4">
              {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
            </div>
          ) : isError ? (
            <div className="text-center py-16">
              <p className="text-error mb-2">Failed to load specialists</p>
              <p className="text-text-secondary text-sm">Please check your connection and try again.</p>
            </div>
          ) : specialists.length === 0 ? (
            <div className="text-center py-16">
              <div className="text-4xl mb-3">&#128270;</div>
              <h3 className="text-lg font-semibold text-primary-dark mb-1">No specialists found</h3>
              <p className="text-text-secondary text-sm">Try adjusting your search or filters.</p>
            </div>
          ) : (
            <>
              <div className="grid gap-4">
                {specialists.map((s) => (
                  <SpecialistCard key={s.id} specialist={s} />
                ))}
              </div>

              {/* Pagination */}
              {specialists.length >= 12 && (
                <div className="flex justify-center gap-2 mt-8">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border border-border rounded-lg text-sm text-text-primary hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="px-4 py-2 text-sm text-text-secondary">Page {page}</span>
                  <button
                    onClick={() => setPage((p) => p + 1)}
                    className="px-4 py-2 border border-border rounded-lg text-sm text-text-primary hover:bg-gray-50"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
