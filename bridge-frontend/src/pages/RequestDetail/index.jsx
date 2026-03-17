import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getTaskRequestDetail,
  createProposal,
  updateRequestStatus,
  getMatchingSpecialists,
} from '../../api/requests';
import { createChat } from '../../api/chats';
import useAuthStore from '../../store/authStore';
import SpecialistCard from '../../components/SpecialistCard';

const urgencyConfig = {
  low: { label: 'Low', className: 'bg-gray-100 text-text-secondary' },
  medium: { label: 'Medium', className: 'bg-blue-50 text-primary' },
  high: { label: 'High', className: 'bg-yellow-50 text-yellow-600' },
  urgent: { label: 'Urgent', className: 'bg-red-50 text-error' },
};

const statusConfig = {
  open: { label: 'Open', className: 'bg-green-50 text-success' },
  in_progress: { label: 'In Progress', className: 'bg-blue-50 text-primary' },
  closed: { label: 'Closed', className: 'bg-gray-100 text-text-secondary' },
};

export default function RequestDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const isClient = user?.role === 'client';

  const [proposalForm, setProposalForm] = useState({
    message: '',
    price_offer: '',
  });
  const [proposalMsg, setProposalMsg] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['taskRequest', id],
    queryFn: () => getTaskRequestDetail(id),
  });

  const request = data?.data;
  const urgency = urgencyConfig[request?.urgency] || urgencyConfig.medium;
  const reqStatus = statusConfig[request?.status] || statusConfig.open;

  // Fetch matching specialists (client only, open requests)
  const { data: specialistsData, isLoading: specialistsLoading } = useQuery({
    queryKey: ['matchingSpecialists', id],
    queryFn: () => getMatchingSpecialists(id),
    enabled: isClient && !!request && request.status === 'open',
  });
  const matchingSpecialists = specialistsData?.data || [];

  const proposalMutation = useMutation({
    mutationFn: (formData) => createProposal(id, formData),
    onSuccess: () => {
      setProposalMsg('Proposal submitted successfully!');
      setProposalForm({ message: '', price_offer: '' });
      queryClient.invalidateQueries({ queryKey: ['taskRequest', id] });
      setTimeout(() => setProposalMsg(''), 3000);
    },
    onError: (err) => {
      setProposalMsg(
        err.response?.data?.detail || 'Failed to submit proposal'
      );
    },
  });

  const statusMutation = useMutation({
    mutationFn: (newStatus) => updateRequestStatus(id, { status: newStatus }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['taskRequest', id] });
    },
  });

  const chatMutation = useMutation({
    mutationFn: (specialistId) => createChat(specialistId),
    onSuccess: (res) => {
      navigate(`/chats/${res.data.id}`);
    },
  });

  const handleProposalSubmit = (e) => {
    e.preventDefault();
    if (!proposalForm.message.trim()) return;
    proposalMutation.mutate({
      message: proposalForm.message.trim(),
      price_offer: proposalForm.price_offer
        ? parseFloat(proposalForm.price_offer)
        : null,
    });
  };

  const alreadyProposed = request?.proposals?.some(
    (p) => p.specialist_id === user?.id
  );

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-8 space-y-4">
        <div className="h-6 w-32 bg-gray-100 rounded animate-pulse" />
        <div className="h-48 bg-white border border-border rounded-xl animate-pulse" />
        <div className="h-32 bg-white border border-border rounded-xl animate-pulse" />
      </div>
    );
  }

  if (!request) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-16 text-center">
        <p className="text-text-secondary mb-3">Request not found.</p>
        <Link
          to="/requests"
          className="text-primary text-sm font-medium hover:underline"
        >
          Back to Requests
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <Link
        to="/requests"
        className="text-sm text-text-secondary hover:text-primary mb-6 inline-block"
      >
        &larr; Back to Requests
      </Link>

      {/* Request details card */}
      <div className="bg-white border border-border rounded-xl p-6 mb-6">
        <div className="flex items-center gap-2 flex-wrap mb-4">
          <span className="bg-primary-light text-primary text-sm font-medium px-3 py-1 rounded">
            {request.domain}
          </span>
          <span
            className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${urgency.className}`}
          >
            {urgency.label} priority
          </span>
          <span
            className={`text-xs font-medium px-2.5 py-0.5 rounded-full ${reqStatus.className}`}
          >
            {reqStatus.label}
          </span>
        </div>

        {/* Budget display */}
        {(request.budget_min != null || request.budget_max != null) && (
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm text-text-secondary">Budget:</span>
            <span className="text-sm font-medium text-text-primary">
              ${request.budget_min || 0} - ${request.budget_max || 'Any'}/hr
            </span>
          </div>
        )}

        {request.comment ? (
          <p className="text-text-primary text-sm leading-relaxed whitespace-pre-line">
            {request.comment}
          </p>
        ) : (
          <p className="text-text-secondary text-sm italic">
            No description provided.
          </p>
        )}

        <div className="flex items-center gap-3 mt-5 pt-4 border-t border-border">
          <div className="w-8 h-8 rounded-full bg-primary-light text-primary flex items-center justify-center text-xs font-bold">
            {request.client?.full_name?.charAt(0) || '?'}
          </div>
          <div>
            <p className="text-sm font-medium text-text-primary">
              {request.client?.full_name}
            </p>
            <p className="text-xs text-text-secondary">
              Posted {new Date(request.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Status controls for client */}
        {isClient &&
          request.client_id === user?.id &&
          request.status !== 'closed' && (
            <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border">
              <span className="text-sm text-text-secondary mr-2">
                Update status:
              </span>
              {request.status === 'open' && (
                <button
                  onClick={() => statusMutation.mutate('in_progress')}
                  disabled={statusMutation.isPending}
                  className="text-xs bg-primary-light text-primary px-3 py-1.5 rounded-lg font-medium hover:bg-primary hover:text-white transition-colors disabled:opacity-50"
                >
                  Mark In Progress
                </button>
              )}
              <button
                onClick={() => statusMutation.mutate('closed')}
                disabled={statusMutation.isPending}
                className="text-xs bg-gray-100 text-text-secondary px-3 py-1.5 rounded-lg font-medium hover:bg-gray-200 transition-colors disabled:opacity-50"
              >
                Close Request
              </button>
            </div>
          )}
      </div>

      {/* Matching specialists section — visible to owning client when request is open */}
      {isClient &&
        request.client_id === user?.id &&
        request.status === 'open' && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-primary-dark mb-4">
              Matching Specialists ({matchingSpecialists.length})
            </h2>

            {specialistsLoading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className="h-32 bg-white border border-border rounded-xl animate-pulse"
                  />
                ))}
              </div>
            ) : matchingSpecialists.length === 0 ? (
              <div className="bg-white border border-border rounded-xl p-8 text-center">
                <p className="text-text-secondary text-sm">
                  No specialists currently match this task. Try broadening your
                  budget range or check back later as new specialists join.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {matchingSpecialists.map((s) => (
                  <div key={s.id} className="relative">
                    <SpecialistCard specialist={s} />
                    <div className="absolute top-4 right-4">
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          chatMutation.mutate(s.user_id);
                        }}
                        disabled={chatMutation.isPending}
                        className="bg-primary text-white text-xs px-3 py-1.5 rounded-lg font-medium hover:bg-primary-dark transition-colors disabled:opacity-50"
                      >
                        Message
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      {/* Proposals section */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-primary-dark mb-4">
          Proposals ({request.proposals?.length || 0})
        </h2>

        {request.proposals?.length === 0 ? (
          <div className="bg-white border border-border rounded-xl p-8 text-center">
            <p className="text-text-secondary text-sm">
              No proposals yet. Specialists matching this domain will be able to
              see your request and submit proposals.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {request.proposals.map((proposal) => (
              <div
                key={proposal.id}
                className="bg-white border border-border rounded-xl p-5"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-primary-light text-primary flex items-center justify-center text-sm font-bold">
                      {proposal.specialist?.full_name?.charAt(0) || '?'}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-text-primary">
                        {proposal.specialist?.full_name}
                      </p>
                      <p className="text-xs text-text-secondary">
                        {new Date(proposal.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  {proposal.price_offer != null && (
                    <span className="text-sm font-semibold text-primary whitespace-nowrap">
                      ${proposal.price_offer}/hr
                    </span>
                  )}
                </div>
                <p className="text-sm text-text-primary mt-3 leading-relaxed">
                  {proposal.message}
                </p>
                {/* Client can start a chat with the proposing specialist */}
                {isClient && (
                  <div className="mt-3 pt-3 border-t border-border">
                    <button
                      onClick={() =>
                        chatMutation.mutate(proposal.specialist_id)
                      }
                      disabled={chatMutation.isPending}
                      className="text-sm text-primary font-medium hover:underline disabled:opacity-50"
                    >
                      Start Chat
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Proposal form (specialist only, if request is open and hasn't proposed yet) */}
      {!isClient && request.status === 'open' && !alreadyProposed && (
        <div className="bg-white border border-border rounded-xl p-6">
          <h2 className="text-lg font-semibold text-primary-dark mb-4">
            Submit a Proposal
          </h2>

          {proposalMsg && (
            <p
              className={`text-sm mb-3 ${proposalMsg.includes('success') ? 'text-success' : 'text-error'}`}
            >
              {proposalMsg}
            </p>
          )}

          <form onSubmit={handleProposalSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Your Proposal <span className="text-error">*</span>
              </label>
              <textarea
                rows={4}
                value={proposalForm.message}
                onChange={(e) =>
                  setProposalForm((f) => ({ ...f, message: e.target.value }))
                }
                placeholder="Describe how you can help with this request, your relevant experience, and approach..."
                className="w-full border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Proposed Rate{' '}
                <span className="text-text-secondary font-normal">
                  ($/hr, optional)
                </span>
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={proposalForm.price_offer}
                onChange={(e) =>
                  setProposalForm((f) => ({
                    ...f,
                    price_offer: e.target.value,
                  }))
                }
                placeholder="e.g. 100"
                className="w-full border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <button
              type="submit"
              disabled={
                !proposalForm.message.trim() || proposalMutation.isPending
              }
              className="bg-primary text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {proposalMutation.isPending ? 'Submitting...' : 'Submit Proposal'}
            </button>
          </form>
        </div>
      )}

      {/* Already proposed indicator */}
      {!isClient && alreadyProposed && (
        <div className="bg-primary-light border border-primary/20 rounded-xl p-4 text-center">
          <p className="text-sm text-primary font-medium">
            You have already submitted a proposal for this request.
          </p>
        </div>
      )}
    </div>
  );
}
