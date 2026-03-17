import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { generateLessonPlan, getRoomLessonPlans } from '../../api/lessonPlans';

const TABS = [
  { key: 'lesson', label: '📖 Lesson', icon: '📖' },
  { key: 'practice', label: '✏️ Practice', icon: '✏️' },
  { key: 'homework', label: '📝 Homework', icon: '📝' },
];

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="text-xs text-text-secondary hover:text-primary transition-colors px-2 py-1 rounded border border-border hover:border-primary/30"
    >
      {copied ? '✓ Copied' : '📋 Copy'}
    </button>
  );
}

function TypingIndicator() {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4">
      <div className="flex items-center gap-1.5">
        <div className="w-2.5 h-2.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2.5 h-2.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2.5 h-2.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <p className="text-sm text-text-secondary">AI is generating your lesson plan...</p>
      <p className="text-xs text-text-secondary">This may take 15-30 seconds</p>
    </div>
  );
}

function MarkdownContent({ content }) {
  if (!content) return <p className="text-text-secondary text-sm">No content generated.</p>;

  // Simple markdown rendering: headers, bold, lists, code blocks
  const lines = content.split('\n');
  const elements = [];
  let inCodeBlock = false;
  let codeLines = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code blocks
    if (line.startsWith('```')) {
      if (inCodeBlock) {
        elements.push(
          <pre key={`code-${i}`} className="bg-gray-50 border border-border rounded-lg p-3 text-sm font-mono overflow-x-auto my-2">
            {codeLines.join('\n')}
          </pre>
        );
        codeLines = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    // Headers
    if (line.startsWith('### ')) {
      elements.push(<h4 key={i} className="text-sm font-bold text-primary-dark mt-4 mb-1">{line.slice(4)}</h4>);
    } else if (line.startsWith('## ')) {
      elements.push(<h3 key={i} className="text-base font-bold text-primary-dark mt-4 mb-2">{line.slice(3)}</h3>);
    } else if (line.startsWith('# ')) {
      elements.push(<h2 key={i} className="text-lg font-bold text-primary-dark mt-4 mb-2">{line.slice(2)}</h2>);
    }
    // List items
    else if (line.match(/^[-*•]\s/)) {
      elements.push(
        <li key={i} className="text-sm text-text-primary ml-4 list-disc">
          {renderInline(line.slice(2))}
        </li>
      );
    }
    // Numbered list
    else if (line.match(/^\d+\.\s/)) {
      const text = line.replace(/^\d+\.\s/, '');
      elements.push(
        <li key={i} className="text-sm text-text-primary ml-4 list-decimal">
          {renderInline(text)}
        </li>
      );
    }
    // Empty line
    else if (line.trim() === '') {
      elements.push(<div key={i} className="h-2" />);
    }
    // Regular paragraph
    else {
      elements.push(<p key={i} className="text-sm text-text-primary leading-relaxed">{renderInline(line)}</p>);
    }
  }

  return <div className="space-y-0.5">{elements}</div>;
}

function renderInline(text) {
  // Bold: **text**
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-semibold">{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

export default function LessonPlanPanel({ roomId, requestId, onClose }) {
  const [activeTab, setActiveTab] = useState('lesson');
  const [additionalContext, setAdditionalContext] = useState('');
  const [showContextInput, setShowContextInput] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['lessonPlans', roomId],
    queryFn: () => getRoomLessonPlans(roomId),
  });

  const plans = data?.data || [];
  const latestPlan = plans[0] || null;

  const generateMutation = useMutation({
    mutationFn: generateLessonPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lessonPlans', roomId] });
      setShowContextInput(false);
      setAdditionalContext('');
    },
  });

  const handleGenerate = () => {
    generateMutation.mutate({
      room_id: roomId,
      request_id: requestId || null,
      additional_context: additionalContext || null,
    });
  };

  const getTabContent = () => {
    if (!latestPlan) return '';
    switch (activeTab) {
      case 'lesson': return latestPlan.lesson_content;
      case 'practice': return latestPlan.practice_exercises;
      case 'homework': return latestPlan.homework;
      default: return '';
    }
  };

  return (
    <div className="bg-white border border-border rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-gray-50">
        <h3 className="text-sm font-semibold text-primary-dark flex items-center gap-2">
          ✨ AI Lesson Planner
        </h3>
        <button
          onClick={onClose}
          className="text-text-secondary hover:text-text-primary text-lg leading-none"
        >
          ×
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* No plan yet — show generate CTA */}
        {!latestPlan && !generateMutation.isPending && (
          <div className="text-center py-6">
            <div className="text-3xl mb-3">🎓</div>
            <h4 className="text-sm font-semibold text-primary-dark mb-1">
              Generate Lesson Materials
            </h4>
            <p className="text-xs text-text-secondary mb-4 max-w-sm mx-auto">
              AI will analyze your conversation and create a structured lesson plan with practice exercises and homework.
            </p>

            {showContextInput && (
              <div className="mb-4 max-w-sm mx-auto">
                <textarea
                  value={additionalContext}
                  onChange={(e) => setAdditionalContext(e.target.value)}
                  placeholder="Optional: add specific focus areas or instructions for the AI..."
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  rows={3}
                />
              </div>
            )}

            <div className="flex items-center justify-center gap-2">
              <button
                onClick={handleGenerate}
                className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors"
              >
                ✨ Generate Lesson Plan
              </button>
              {!showContextInput && (
                <button
                  onClick={() => setShowContextInput(true)}
                  className="text-text-secondary hover:text-primary text-sm px-3 py-2 rounded-lg border border-border hover:border-primary/30 transition-colors"
                >
                  + Add context
                </button>
              )}
            </div>
          </div>
        )}

        {/* Generating... */}
        {generateMutation.isPending && <TypingIndicator />}

        {/* Generation error */}
        {generateMutation.isError && (
          <div className="text-center py-6">
            <div className="text-3xl mb-3">⚠️</div>
            <p className="text-sm text-error mb-3">
              {generateMutation.error?.response?.data?.detail || 'Failed to generate lesson plan. Please try again.'}
            </p>
            <button
              onClick={handleGenerate}
              className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Plan exists — show tabs */}
        {latestPlan && latestPlan.status === 'completed' && !generateMutation.isPending && (
          <>
            {/* Tabs */}
            <div className="flex items-center gap-1 mb-4">
              {TABS.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    activeTab === tab.key
                      ? 'bg-primary text-white'
                      : 'bg-gray-50 text-text-secondary hover:bg-primary-light hover:text-primary'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
              <div className="flex-1" />
              <CopyButton text={getTabContent()} />
            </div>

            {/* Tab content */}
            <div className="max-h-96 overflow-y-auto pr-1">
              <MarkdownContent content={getTabContent()} />
            </div>

            {/* Footer actions */}
            <div className="flex items-center justify-between mt-4 pt-3 border-t border-border">
              <span className="text-xs text-text-secondary">
                Language: {latestPlan.language?.toUpperCase()} · Generated {new Date(latestPlan.created_at).toLocaleString()}
              </span>
              <button
                onClick={handleGenerate}
                disabled={generateMutation.isPending}
                className="text-xs text-primary hover:text-primary-dark font-medium transition-colors disabled:opacity-50"
              >
                🔄 Regenerate
              </button>
            </div>
          </>
        )}

        {/* Plan failed */}
        {latestPlan && latestPlan.status === 'failed' && !generateMutation.isPending && (
          <div className="text-center py-6">
            <div className="text-3xl mb-3">⚠️</div>
            <p className="text-sm text-error mb-2">Generation failed</p>
            <p className="text-xs text-text-secondary mb-3">{latestPlan.error_message}</p>
            <button
              onClick={handleGenerate}
              className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
