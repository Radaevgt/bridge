import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSpecialist } from '../../api/specialists';
import { getReviews, createReview } from '../../api/reviews';
import { createChat } from '../../api/chats';
import useAuthStore from '../../store/authStore';

const availabilityConfig = {
  available: { label: 'Available', className: 'bg-green-50 text-success border-success/30' },
  busy: { label: 'Busy', className: 'bg-yellow-50 text-yellow-600 border-yellow-300' },
  vacation: { label: 'On Vacation', className: 'bg-gray-100 text-text-secondary border-border' },
};

export default function SpecialistProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user, isAuthenticated } = useAuthStore();

  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState('');
  const [reviewError, setReviewError] = useState('');

  const { data: profileData, isLoading } = useQuery({
    queryKey: ['specialist', id],
    queryFn: () => getSpecialist(id),
  });

  const { data: reviewsData } = useQuery({
    queryKey: ['reviews', id],
    queryFn: () => getReviews(id),
  });

  const reviewMutation = useMutation({
    mutationFn: (data) => createReview(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', id] });
      queryClient.invalidateQueries({ queryKey: ['specialist', id] });
      setReviewComment('');
      setReviewRating(5);
      setReviewError('');
    },
    onError: (err) => {
      setReviewError(err.response?.data?.detail || 'Failed to submit review.');
    },
  });

  const handleStartChat = async () => {
    try {
      const { data } = await createChat(profile?.user_id);
      navigate(`/chats/${data.id}`);
    } catch {
      navigate('/chats');
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-8 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="h-4 bg-gray-200 rounded w-2/3 mb-2" />
        <div className="h-4 bg-gray-200 rounded w-1/2" />
      </div>
    );
  }

  const profile = profileData?.data;
  const reviews = reviewsData?.data || [];
  const avail = availabilityConfig[profile?.availability] || availabilityConfig.available;
  const isClient = user?.role === 'client';

  if (!profile) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-16 text-center">
        <h2 className="text-xl font-semibold text-primary-dark mb-2">Specialist not found</h2>
        <p className="text-text-secondary">This profile may have been removed or doesn&apos;t exist.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="bg-white border border-border rounded-xl p-6 mb-6">
        <div className="flex items-start gap-5">
          {profile.user?.avatar_url ? (
            <img
              src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${profile.user.avatar_url}`}
              alt={profile.user.full_name}
              className="w-16 h-16 rounded-full object-cover flex-shrink-0"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-primary-light text-primary flex items-center justify-center text-2xl font-bold flex-shrink-0">
              {profile.user?.full_name?.charAt(0) || '?'}
            </div>
          )}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-primary-dark">{profile.user?.full_name}</h1>
              <span className={`text-xs font-medium px-2.5 py-0.5 rounded-full border ${avail.className}`}>
                {avail.label}
              </span>
            </div>
            {profile.headline && (
              <p className="text-text-secondary mb-2">{profile.headline}</p>
            )}
            <div className="flex items-center gap-4 text-sm">
              <span className="font-semibold text-text-primary">${profile.hourly_rate}/hr</span>
              <span className="text-text-secondary">
                &#9733; {profile.avg_rating?.toFixed(1)} ({profile.review_count} reviews)
              </span>
            </div>
          </div>
          {isAuthenticated && isClient && (
            <button
              onClick={handleStartChat}
              className="bg-primary text-white px-6 py-2.5 rounded-lg font-medium hover:bg-primary-dark transition-colors flex-shrink-0"
            >
              Message
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Bio */}
          {profile.bio && (
            <div className="bg-white border border-border rounded-xl p-6">
              <h2 className="text-lg font-semibold text-primary-dark mb-3">About</h2>
              <p className="text-text-secondary whitespace-pre-line">{profile.bio}</p>
            </div>
          )}

          {/* Competencies */}
          {profile.competencies?.length > 0 && (
            <div className="bg-white border border-border rounded-xl p-6">
              <h2 className="text-lg font-semibold text-primary-dark mb-3">Credentials & Proof</h2>
              <ul className="space-y-2">
                {profile.competencies.map((c) => (
                  <li key={c.id} className="flex items-center gap-2">
                    <span className="text-primary">&#128279;</span>
                    <a href={c.url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm">
                      {c.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Reviews */}
          <div className="bg-white border border-border rounded-xl p-6">
            <h2 className="text-lg font-semibold text-primary-dark mb-4">
              Reviews ({reviews.length})
            </h2>
            {reviews.length === 0 ? (
              <p className="text-text-secondary text-sm">No reviews yet. Be the first to leave one!</p>
            ) : (
              <div className="space-y-4">
                {reviews.map((r) => (
                  <div key={r.id} className="border-b border-border pb-4 last:border-0 last:pb-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-text-primary">
                        {'&#9733;'.repeat(r.rating)}{'&#9734;'.repeat(5 - r.rating)}
                      </span>
                      <span className="text-xs text-text-secondary">
                        {new Date(r.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {r.comment && <p className="text-sm text-text-secondary">{r.comment}</p>}
                  </div>
                ))}
              </div>
            )}

            {/* Leave review form */}
            {isAuthenticated && isClient && (
              <div className="mt-6 pt-4 border-t border-border">
                <h3 className="text-sm font-semibold text-primary-dark mb-3">Leave a Review</h3>
                {reviewError && (
                  <p className="text-error text-sm mb-2">{reviewError}</p>
                )}
                <div className="flex items-center gap-1 mb-3">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => setReviewRating(star)}
                      className={`text-xl ${star <= reviewRating ? 'text-yellow-400' : 'text-gray-300'}`}
                    >
                      &#9733;
                    </button>
                  ))}
                </div>
                <textarea
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  placeholder="Share your experience..."
                  rows={3}
                  className="w-full border border-border rounded-lg px-4 py-2 text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary mb-3"
                />
                <button
                  onClick={() => reviewMutation.mutate({ rating: reviewRating, comment: reviewComment })}
                  disabled={reviewMutation.isPending}
                  className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-50"
                >
                  {reviewMutation.isPending ? 'Submitting...' : 'Submit Review'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {profile.domains?.length > 0 && (
            <div className="bg-white border border-border rounded-xl p-6">
              <h2 className="text-sm font-semibold text-primary-dark mb-3">Domains</h2>
              <div className="flex flex-wrap gap-2">
                {profile.domains.map((d) => (
                  <span key={d.id} className="bg-primary-light text-primary text-xs font-medium px-3 py-1 rounded-full">
                    {d.domain}
                  </span>
                ))}
              </div>
            </div>
          )}

          {profile.languages?.length > 0 && (
            <div className="bg-white border border-border rounded-xl p-6">
              <h2 className="text-sm font-semibold text-primary-dark mb-3">Languages</h2>
              <ul className="space-y-1.5">
                {profile.languages.map((l) => (
                  <li key={l.id} className="flex items-center justify-between text-sm">
                    <span className="text-text-primary">{l.language}</span>
                    <span className="text-text-secondary capitalize">{l.proficiency}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
