import { Link } from 'react-router-dom';

const availabilityConfig = {
  available: { label: 'Available', className: 'bg-green-50 text-success' },
  busy: { label: 'Busy', className: 'bg-yellow-50 text-yellow-600' },
  vacation: { label: 'On Vacation', className: 'bg-gray-100 text-text-secondary' },
};

export default function SpecialistCard({ specialist }) {
  const profile = specialist;
  const user = profile?.user;
  const avail = availabilityConfig[profile?.availability] || availabilityConfig.available;

  return (
    <Link
      to={`/specialists/${profile?.id}`}
      className="block bg-white border border-border rounded-xl p-5 hover:shadow-md hover:border-primary/30 transition-all"
    >
      <div className="flex items-start gap-4">
        {user?.avatar_url ? (
          <img
            src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${user.avatar_url}`}
            alt={user.full_name}
            className="w-12 h-12 rounded-full object-cover flex-shrink-0"
          />
        ) : (
          <div className="w-12 h-12 rounded-full bg-primary-light text-primary flex items-center justify-center text-lg font-bold flex-shrink-0">
            {user?.full_name?.charAt(0) || '?'}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <h3 className="text-base font-semibold text-primary-dark truncate">{user?.full_name}</h3>
              {profile?.relevance_score != null && (
                <span className="bg-green-50 text-success text-xs font-semibold px-2 py-0.5 rounded-full flex-shrink-0">
                  {Math.round(profile.relevance_score)}% match
                </span>
              )}
            </div>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full flex-shrink-0 ${avail.className}`}>
              {avail.label}
            </span>
          </div>
          {profile?.headline && (
            <p className="text-sm text-text-secondary mt-0.5 truncate">{profile.headline}</p>
          )}
        </div>
      </div>

      {profile?.bio && (
        <p className="text-sm text-text-secondary mt-3 line-clamp-2">{profile.bio}</p>
      )}

      {profile?.domains?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {profile.domains.map((d) => (
            <span key={d.id} className="bg-primary-light text-primary text-xs font-medium px-2 py-0.5 rounded">
              {d.domain}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between mt-4 pt-3 border-t border-border">
        <div className="flex items-center gap-3 text-sm">
          <span className="text-text-primary font-semibold">
            ${profile?.hourly_rate || 0}/hr
          </span>
          <span className="text-text-secondary">
            &#9733; {profile?.avg_rating?.toFixed(1) || '0.0'} ({profile?.review_count || 0})
          </span>
        </div>
        {profile?.languages?.length > 0 && (
          <div className="text-xs text-text-secondary">
            {profile.languages.map((l) => l.language).join(', ')}
          </div>
        )}
      </div>
    </Link>
  );
}
