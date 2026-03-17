import { Link, Navigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

const FEATURES = [
  {
    icon: '\uD83D\uDCDD',
    title: 'Describe Your Task',
    desc: 'Tell us what you need help with, set your budget, and choose your timeline.',
  },
  {
    icon: '\uD83D\uDD0D',
    title: 'Get Matched',
    desc: 'Bridge instantly finds specialists in your domain who fit your budget and availability.',
  },
  {
    icon: '\uD83D\uDCAC',
    title: 'Connect & Collaborate',
    desc: 'Chat directly with specialists, review their credentials, and start working together.',
  },
];

const DOMAINS = [
  'AI/ML',
  'Law',
  'Finance',
  'Medicine',
  'Engineering',
  'Design',
  'Marketing',
  'Education',
  'Science',
  'Business',
  'Other',
];

export default function Landing() {
  const { isAuthenticated, user } = useAuthStore();

  if (isAuthenticated && user) {
    const target =
      user.role === 'specialist' ? '/dashboard/specialist' : '/dashboard';
    return <Navigate to={target} replace />;
  }

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl font-bold text-primary-dark mb-4">
          Expert Help,
          <br />
          One Task Away
        </h1>
        <p className="text-xl text-text-secondary max-w-2xl mx-auto mb-8">
          Bridge connects you with verified specialists who can solve your
          toughest challenges. Describe your task and get matched with the right
          expert instantly.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link
            to="/register"
            className="bg-primary text-white px-8 py-3 rounded-lg font-medium text-lg hover:bg-primary-dark transition-colors"
          >
            Get Started Free
          </Link>
          <Link
            to="/login"
            className="border border-primary text-primary px-8 py-3 rounded-lg font-medium text-lg hover:bg-primary-light transition-colors"
          >
            Log In
          </Link>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-5xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-primary-dark text-center mb-12">
            How Bridge Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {FEATURES.map((f, i) => (
              <div key={i} className="text-center">
                <div className="w-14 h-14 bg-primary-light text-primary rounded-full flex items-center justify-center text-2xl mx-auto mb-4">
                  {f.icon}
                </div>
                <h3 className="text-lg font-semibold text-primary-dark mb-2">
                  {f.title}
                </h3>
                <p className="text-text-secondary">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Domains */}
      <section className="py-16">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-primary-dark mb-4">
            Experts Across Every Domain
          </h2>
          <p className="text-text-secondary mb-8 max-w-2xl mx-auto">
            From artificial intelligence to business strategy, find specialists
            with proven credentials in the exact field you need.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            {DOMAINS.map((d) => (
              <span
                key={d}
                className="bg-primary-light text-primary text-sm font-medium px-4 py-2 rounded-lg"
              >
                {d}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Trust signals */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-primary mb-1">100%</div>
              <p className="text-text-secondary">Free to connect</p>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary mb-1">
                Real-Time
              </div>
              <p className="text-text-secondary">Instant chat with specialists</p>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary mb-1">
                Verified
              </div>
              <p className="text-text-secondary">
                Credential links on every profile
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="max-w-5xl mx-auto px-6 py-16 text-center">
        <h2 className="text-3xl font-bold text-primary-dark mb-4">
          Ready to find your expert?
        </h2>
        <p className="text-text-secondary mb-8">
          Create a free account and post your first task in under a minute.
        </p>
        <Link
          to="/register"
          className="bg-primary text-white px-8 py-3 rounded-lg font-medium text-lg hover:bg-primary-dark transition-colors"
        >
          Create Free Account
        </Link>
      </section>
    </div>
  );
}
