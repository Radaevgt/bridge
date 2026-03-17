import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMyChats } from '../../api/chats';
import { getMyProfile, createOrUpdateProfile, addCompetency, deleteCompetency, updateAvailability, uploadAvatar } from '../../api/specialists';
import useAuthStore from '../../store/authStore';

export default function SpecialistDashboard() {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const formInitialized = useRef(false);

  const [profileForm, setProfileForm] = useState({
    headline: '', bio: '', hourly_rate: '', domains: '', languages: '',
  });
  const [compForm, setCompForm] = useState({ label: '', url: '' });
  const [profileMsg, setProfileMsg] = useState('');

  const { data: profileData } = useQuery({
    queryKey: ['myProfile'],
    queryFn: getMyProfile,
  });

  const profile = profileData?.data || null;

  // Populate form when profile data loads
  useEffect(() => {
    if (!profile || formInitialized.current) return;
    setProfileForm({
      headline: profile.headline || '',
      bio: profile.bio || '',
      hourly_rate: profile.hourly_rate || '',
      domains: profile.domains?.map((d) => d.domain).join(', ') || '',
      languages: profile.languages?.map((l) => l.language).join(', ') || '',
    });
    formInitialized.current = true;
  }, [profile]);

  const { data: chatsData } = useQuery({
    queryKey: ['chats'],
    queryFn: getMyChats,
  });

  const rooms = chatsData?.data || [];

  const profileMutation = useMutation({
    mutationFn: (data) => createOrUpdateProfile(data),
    onSuccess: () => {
      setProfileMsg('Profile updated successfully!');
      queryClient.invalidateQueries({ queryKey: ['myProfile'] });
      setTimeout(() => setProfileMsg(''), 3000);
    },
    onError: (err) => setProfileMsg(err.response?.data?.detail || 'Update failed'),
  });

  const availMutation = useMutation({
    mutationFn: (data) => updateAvailability(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['myProfile'] }),
  });

  const addCompMutation = useMutation({
    mutationFn: (data) => addCompetency(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myProfile'] });
      setCompForm({ label: '', url: '' });
    },
  });

  const deleteCompMutation = useMutation({
    mutationFn: (id) => deleteCompetency(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['myProfile'] }),
  });

  const avatarMutation = useMutation({
    mutationFn: (file) => uploadAvatar(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myProfile'] });
      setProfileMsg('Photo updated!');
      setTimeout(() => setProfileMsg(''), 3000);
    },
    onError: (err) => setProfileMsg(err.response?.data?.detail || 'Photo upload failed'),
  });

  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0];
    if (file) avatarMutation.mutate(file);
  };

  const avatarUrl = profile?.user?.avatar_url;

  const handleProfileSubmit = (e) => {
    e.preventDefault();
    const payload = {
      headline: profileForm.headline,
      bio: profileForm.bio,
      hourly_rate: parseFloat(profileForm.hourly_rate) || 0,
      domains: profileForm.domains.split(',').map((d) => d.trim()).filter(Boolean),
      languages: profileForm.languages.split(',').map((l) => ({ language: l.trim(), proficiency: 'fluent' })).filter((l) => l.language),
    };
    profileMutation.mutate(payload);
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-primary-dark">
          Welcome, {user?.full_name || 'Specialist'}
        </h1>
        <p className="text-text-secondary mt-1">Manage your profile and connect with clients.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main */}
        <div className="lg:col-span-2 space-y-6">
          {/* Profile form */}
          <div className="bg-white border border-border rounded-xl p-6">
            <h2 className="text-lg font-semibold text-primary-dark mb-4">Edit Profile</h2>
            {profileMsg && (
              <p className={`text-sm mb-3 ${profileMsg.includes('success') || profileMsg.includes('Photo') ? 'text-success' : 'text-error'}`}>
                {profileMsg}
              </p>
            )}

            {/* Avatar upload */}
            <div className="flex items-center gap-4 mb-6">
              <label className="relative cursor-pointer group">
                <input type="file" accept="image/jpeg,image/png,image/webp" onChange={handleAvatarChange} className="hidden" />
                {avatarUrl ? (
                  <img
                    src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${avatarUrl}`}
                    alt="Avatar"
                    className="w-20 h-20 rounded-full object-cover border-2 border-border group-hover:border-primary transition-colors"
                  />
                ) : (
                  <div className="w-20 h-20 rounded-full bg-primary-light text-primary flex items-center justify-center text-2xl font-bold border-2 border-border group-hover:border-primary transition-colors">
                    {user?.full_name?.charAt(0) || '?'}
                  </div>
                )}
                <div className="absolute inset-0 rounded-full bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="text-white text-xs font-medium">Change</span>
                </div>
              </label>
              <div>
                <p className="text-sm font-medium text-text-primary">Profile Photo</p>
                <p className="text-xs text-text-secondary">JPEG, PNG or WebP. Max 5 MB.</p>
                {avatarMutation.isPending && <p className="text-xs text-primary mt-1">Uploading...</p>}
              </div>
            </div>

            <form onSubmit={handleProfileSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">Headline</label>
                <input
                  type="text"
                  maxLength={200}
                  value={profileForm.headline}
                  onChange={(e) => setProfileForm((f) => ({ ...f, headline: e.target.value }))}
                  placeholder="Senior AI Researcher & Consultant"
                  className="w-full border border-border rounded-lg px-4 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">Bio</label>
                <textarea
                  rows={4}
                  value={profileForm.bio}
                  onChange={(e) => setProfileForm((f) => ({ ...f, bio: e.target.value }))}
                  placeholder="Tell clients about your expertise..."
                  className="w-full border border-border rounded-lg px-4 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">Hourly Rate ($)</label>
                <input
                  type="number"
                  value={profileForm.hourly_rate}
                  onChange={(e) => setProfileForm((f) => ({ ...f, hourly_rate: e.target.value }))}
                  placeholder="100"
                  className="w-full border border-border rounded-lg px-4 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">Domains (comma-separated)</label>
                <input
                  type="text"
                  value={profileForm.domains}
                  onChange={(e) => setProfileForm((f) => ({ ...f, domains: e.target.value }))}
                  placeholder="AI/ML, Engineering, Science"
                  className="w-full border border-border rounded-lg px-4 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">Languages (comma-separated)</label>
                <input
                  type="text"
                  value={profileForm.languages}
                  onChange={(e) => setProfileForm((f) => ({ ...f, languages: e.target.value }))}
                  placeholder="English, Spanish"
                  className="w-full border border-border rounded-lg px-4 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <button
                type="submit"
                disabled={profileMutation.isPending}
                className="bg-primary text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-50"
              >
                {profileMutation.isPending ? 'Saving...' : 'Save Profile'}
              </button>
            </form>
          </div>

          {/* Competencies */}
          <div className="bg-white border border-border rounded-xl p-6">
            <h2 className="text-lg font-semibold text-primary-dark mb-4">Credentials & Proof</h2>
            {profile?.competencies?.length > 0 && (
              <ul className="space-y-2 mb-4">
                {profile.competencies.map((c) => (
                  <li key={c.id} className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-2">
                    <a href={c.url} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline">
                      {c.label}
                    </a>
                    <button
                      onClick={() => deleteCompMutation.mutate(c.id)}
                      className="text-xs text-error hover:underline"
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Label (e.g. PhD Thesis)"
                value={compForm.label}
                onChange={(e) => setCompForm((f) => ({ ...f, label: e.target.value }))}
                className="flex-1 border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <input
                type="url"
                placeholder="URL"
                value={compForm.url}
                onChange={(e) => setCompForm((f) => ({ ...f, url: e.target.value }))}
                className="flex-1 border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button
                onClick={() => compForm.label && compForm.url && addCompMutation.mutate(compForm)}
                disabled={!compForm.label || !compForm.url}
                className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-dark disabled:opacity-50"
              >
                Add
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Primary CTA for specialist */}
          <Link
            to="/requests"
            className="block bg-primary text-white rounded-xl p-5 hover:bg-primary-dark transition-colors"
          >
            <h3 className="text-sm font-semibold">Incoming Requests</h3>
            <p className="text-xs text-white/80 mt-1">
              Browse tasks matching your expertise
            </p>
          </Link>

          {/* Availability */}
          <div className="bg-white border border-border rounded-xl p-6">
            <h2 className="text-sm font-semibold text-primary-dark mb-3">Availability</h2>
            <div className="space-y-2">
              {['available', 'busy', 'vacation'].map((s) => (
                <button
                  key={s}
                  onClick={() => availMutation.mutate({ availability: s })}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors capitalize ${
                    profile?.availability === s
                      ? 'bg-primary-light text-primary font-medium'
                      : 'text-text-secondary hover:bg-gray-50'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="bg-white border border-border rounded-xl p-6">
            <h2 className="text-sm font-semibold text-primary-dark mb-3">Stats</h2>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Rating</span>
                <span className="font-medium text-text-primary">&#9733; {profile?.avg_rating?.toFixed(1) || '0.0'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Reviews</span>
                <span className="font-medium text-text-primary">{profile?.review_count || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Conversations</span>
                <span className="font-medium text-text-primary">{rooms.length}</span>
              </div>
            </div>
          </div>

          {/* Quick links */}
          <div className="bg-white border border-border rounded-xl p-6">
            <h2 className="text-sm font-semibold text-primary-dark mb-3">Quick Links</h2>
            <div className="space-y-2">
              <Link to="/requests" className="block text-sm text-primary hover:underline">Incoming Requests</Link>
              <Link to="/chats" className="block text-sm text-primary hover:underline">Messages</Link>
              <Link to="/settings" className="block text-sm text-primary hover:underline">Settings</Link>
              {profile && (
                <Link to={`/specialists/${profile.id}`} className="block text-sm text-primary hover:underline">
                  View Public Profile
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
