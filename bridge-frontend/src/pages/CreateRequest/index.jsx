import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { createTaskRequest } from '../../api/requests';

const DOMAINS = [
  { value: 'AI/ML', icon: '\uD83E\uDD16', desc: 'Machine learning, data science, AI systems' },
  { value: 'Law', icon: '\u2696\uFE0F', desc: 'Legal advice, contracts, compliance' },
  { value: 'Finance', icon: '\uD83D\uDCB0', desc: 'Investments, accounting, financial planning' },
  { value: 'Medicine', icon: '\uD83C\uDFE5', desc: 'Medical consultation, health, pharma' },
  { value: 'Engineering', icon: '\u2699\uFE0F', desc: 'Software, mechanical, civil engineering' },
  { value: 'Design', icon: '\uD83C\uDFA8', desc: 'UI/UX, graphic, product design' },
  { value: 'Marketing', icon: '\uD83D\uDCE3', desc: 'Digital marketing, SEO, branding' },
  { value: 'Education', icon: '\uD83D\uDCDA', desc: 'Tutoring, curriculum, academic research' },
  { value: 'Science', icon: '\uD83D\uDD2C', desc: 'Research, lab work, scientific writing' },
  { value: 'Business', icon: '\uD83D\uDCBC', desc: 'Strategy, management, consulting' },
  { value: 'Other', icon: '\uD83D\uDCCC', desc: 'Any other domain not listed above' },
];

const URGENCY_OPTIONS = [
  { value: 'low', label: 'Low', desc: 'No rush, flexible timeline' },
  { value: 'medium', label: 'Medium', desc: 'Within a few weeks' },
  { value: 'high', label: 'High', desc: 'Within a few days' },
  { value: 'urgent', label: 'Urgent', desc: 'Need help ASAP' },
];

const STEPS = ['Domain', 'Goals', 'Budget & Urgency', 'Review'];

export default function CreateRequest() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState({
    domain: '',
    comment: '',
    budget_min: '',
    budget_max: '',
    urgency: 'medium',
  });
  const [errors, setErrors] = useState({});
  const [successMsg, setSuccessMsg] = useState('');

  const mutation = useMutation({
    mutationFn: createTaskRequest,
    onSuccess: (res) => {
      setSuccessMsg('Task created successfully! Finding matching specialists...');
      setTimeout(() => navigate(`/requests/${res.data.id}`), 1200);
    },
  });

  const validateStep = () => {
    const newErrors = {};
    if (step === 0 && !formData.domain) {
      newErrors.domain = 'Please select a domain';
    }
    if (step === 1 && !formData.comment?.trim()) {
      newErrors.comment = 'Please describe what you need help with';
    }
    if (step === 2) {
      if (
        formData.budget_min &&
        formData.budget_max &&
        parseFloat(formData.budget_min) > parseFloat(formData.budget_max)
      ) {
        newErrors.budget = 'Minimum budget cannot exceed maximum';
      }
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep()) {
      setStep((s) => s + 1);
    }
  };

  const handleBack = () => setStep((s) => s - 1);

  const handleSubmit = () => {
    mutation.mutate({
      domain: formData.domain,
      urgency: formData.urgency,
      comment: formData.comment || null,
      budget_min: formData.budget_min ? parseFloat(formData.budget_min) : null,
      budget_max: formData.budget_max ? parseFloat(formData.budget_max) : null,
    });
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="mb-6">
        <Link
          to="/dashboard"
          className="text-sm text-text-secondary hover:text-primary"
        >
          &larr; Back to Dashboard
        </Link>
      </div>

      {/* Progress bar */}
      <div className="flex items-center gap-1 mb-8">
        {STEPS.map((label, i) => (
          <div key={label} className="flex-1">
            <div
              className={`h-1.5 rounded-full ${
                i <= step ? 'bg-primary' : 'bg-gray-200'
              }`}
            />
            <p
              className={`text-xs mt-1.5 ${
                i <= step
                  ? 'text-primary font-medium'
                  : 'text-text-secondary'
              }`}
            >
              {label}
            </p>
          </div>
        ))}
      </div>

      <div className="bg-white border border-border rounded-xl p-6">
        {/* Messages */}
        {successMsg && (
          <div className="bg-green-50 text-success text-sm rounded-lg px-4 py-3 mb-4">
            {successMsg}
          </div>
        )}
        {mutation.isError && (
          <div className="bg-red-50 text-error text-sm rounded-lg px-4 py-3 mb-4">
            {mutation.error?.response?.data?.detail || 'Something went wrong.'}
          </div>
        )}

        {/* Step 0: Domain selection */}
        {step === 0 && (
          <>
            <h2 className="text-xl font-bold text-primary-dark mb-1">
              What domain do you need help with?
            </h2>
            <p className="text-text-secondary text-sm mb-6">
              Select the area of expertise that best matches your task.
            </p>
            <div className="grid grid-cols-2 gap-3">
              {DOMAINS.map((d) => (
                <button
                  key={d.value}
                  type="button"
                  onClick={() => {
                    setFormData((f) => ({ ...f, domain: d.value }));
                    setErrors({});
                  }}
                  className={`text-left border rounded-xl p-4 transition-all ${
                    formData.domain === d.value
                      ? 'border-primary bg-primary-light'
                      : 'border-border hover:border-primary/30'
                  }`}
                >
                  <div className="text-xl mb-1">{d.icon}</div>
                  <div className="text-sm font-semibold text-primary-dark">
                    {d.value}
                  </div>
                  <div className="text-xs text-text-secondary mt-0.5">
                    {d.desc}
                  </div>
                </button>
              ))}
            </div>
            {errors.domain && (
              <p className="text-error text-xs mt-3">{errors.domain}</p>
            )}
          </>
        )}

        {/* Step 1: Describe goals */}
        {step === 1 && (
          <>
            <h2 className="text-xl font-bold text-primary-dark mb-1">
              Describe what you need
            </h2>
            <p className="text-text-secondary text-sm mb-6">
              The more detail you provide, the better specialists can understand
              your task.
            </p>
            <textarea
              rows={6}
              value={formData.comment}
              onChange={(e) => {
                setFormData((f) => ({ ...f, comment: e.target.value }));
                setErrors({});
              }}
              placeholder="Describe your task, goals, timeline, or any other details..."
              className="w-full border border-border rounded-lg px-4 py-3 text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            />
            {errors.comment && (
              <p className="text-error text-xs mt-1">{errors.comment}</p>
            )}
          </>
        )}

        {/* Step 2: Budget & Urgency */}
        {step === 2 && (
          <>
            <h2 className="text-xl font-bold text-primary-dark mb-1">
              Budget & Timeline
            </h2>
            <p className="text-text-secondary text-sm mb-6">
              Set your hourly budget range and how urgently you need help.
            </p>

            {/* Budget range */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-text-primary mb-2">
                Hourly Budget Range ($/hr)
                <span className="text-text-secondary font-normal ml-1">
                  (optional)
                </span>
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min="0"
                  placeholder="Min"
                  value={formData.budget_min}
                  onChange={(e) =>
                    setFormData((f) => ({ ...f, budget_min: e.target.value }))
                  }
                  className="flex-1 border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <span className="text-text-secondary">to</span>
                <input
                  type="number"
                  min="0"
                  placeholder="Max"
                  value={formData.budget_max}
                  onChange={(e) =>
                    setFormData((f) => ({ ...f, budget_max: e.target.value }))
                  }
                  className="flex-1 border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              {errors.budget && (
                <p className="text-error text-xs mt-1">{errors.budget}</p>
              )}
            </div>

            {/* Urgency */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Urgency
              </label>
              <div className="grid grid-cols-2 gap-3">
                {URGENCY_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() =>
                      setFormData((f) => ({ ...f, urgency: opt.value }))
                    }
                    className={`text-left border rounded-lg p-3 transition-all ${
                      formData.urgency === opt.value
                        ? 'border-primary bg-primary-light'
                        : 'border-border hover:border-primary/30'
                    }`}
                  >
                    <span className="text-sm font-medium text-text-primary">
                      {opt.label}
                    </span>
                    <p className="text-xs text-text-secondary mt-0.5">
                      {opt.desc}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Step 3: Review */}
        {step === 3 && (
          <>
            <h2 className="text-xl font-bold text-primary-dark mb-1">
              Review Your Task
            </h2>
            <p className="text-text-secondary text-sm mb-6">
              Make sure everything looks right before submitting.
            </p>

            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <span className="text-xs text-text-secondary uppercase tracking-wide">
                  Domain
                </span>
                <p className="text-sm font-medium text-text-primary mt-1">
                  {formData.domain}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <span className="text-xs text-text-secondary uppercase tracking-wide">
                  Description
                </span>
                <p className="text-sm text-text-primary mt-1 whitespace-pre-line">
                  {formData.comment}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <span className="text-xs text-text-secondary uppercase tracking-wide">
                    Budget
                  </span>
                  <p className="text-sm font-medium text-text-primary mt-1">
                    {formData.budget_min || formData.budget_max
                      ? `$${formData.budget_min || '0'} - $${formData.budget_max || 'Any'}/hr`
                      : 'Not specified'}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <span className="text-xs text-text-secondary uppercase tracking-wide">
                    Urgency
                  </span>
                  <p className="text-sm font-medium text-text-primary mt-1 capitalize">
                    {formData.urgency}
                  </p>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Navigation buttons */}
        <div className="flex items-center justify-between mt-8 pt-5 border-t border-border">
          {step > 0 ? (
            <button
              type="button"
              onClick={handleBack}
              className="text-sm text-text-secondary hover:text-primary transition-colors"
            >
              &larr; Back
            </button>
          ) : (
            <div />
          )}

          {step < 3 ? (
            <button
              type="button"
              onClick={handleNext}
              className="bg-primary text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors"
            >
              Next &rarr;
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={mutation.isPending}
              className="bg-primary text-white px-8 py-2.5 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {mutation.isPending ? 'Creating...' : 'Submit Task'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
