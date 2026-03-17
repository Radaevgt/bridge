const DOMAINS = ['AI/ML', 'Law', 'Finance', 'Medicine', 'Engineering', 'Design', 'Marketing', 'Education', 'Science', 'Business', 'Other'];
const LANGUAGES = ['English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese', 'Russian', 'Arabic', 'Portuguese', 'Hindi'];
const SORT_OPTIONS = [
  { value: 'rating', label: 'Top Rated' },
  { value: 'relevance', label: 'Best Match' },
  { value: 'price_asc', label: 'Price: Low to High' },
  { value: 'price_desc', label: 'Price: High to Low' },
];

export default function FilterPanel({ filters, onFilterChange }) {
  const handleChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value });
  };

  return (
    <div className="bg-white border border-border rounded-xl p-5 space-y-5">
      <h3 className="text-lg font-semibold text-primary-dark">Filters</h3>

      {/* Sort */}
      <div>
        <label className="block text-sm font-medium text-text-primary mb-1">Sort by</label>
        <select
          value={filters.sort || 'rating'}
          onChange={(e) => handleChange('sort', e.target.value)}
          className="w-full border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      {/* Domain */}
      <div>
        <label className="block text-sm font-medium text-text-primary mb-1">Domain</label>
        <select
          value={filters.domain || ''}
          onChange={(e) => handleChange('domain', e.target.value)}
          className="w-full border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">All Domains</option>
          {DOMAINS.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      {/* Language */}
      <div>
        <label className="block text-sm font-medium text-text-primary mb-1">Language</label>
        <select
          value={filters.language || ''}
          onChange={(e) => handleChange('language', e.target.value)}
          className="w-full border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">All Languages</option>
          {LANGUAGES.map((l) => (
            <option key={l} value={l}>{l}</option>
          ))}
        </select>
      </div>

      {/* Price Range */}
      <div>
        <label className="block text-sm font-medium text-text-primary mb-1">Price Range ($/hr)</label>
        <div className="flex items-center gap-2">
          <input
            type="number"
            placeholder="Min"
            value={filters.min_price || ''}
            onChange={(e) => handleChange('min_price', e.target.value)}
            className="w-full border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <span className="text-text-secondary">-</span>
          <input
            type="number"
            placeholder="Max"
            value={filters.max_price || ''}
            onChange={(e) => handleChange('max_price', e.target.value)}
            className="w-full border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>

      {/* Min Rating */}
      <div>
        <label className="block text-sm font-medium text-text-primary mb-1">Minimum Rating</label>
        <select
          value={filters.min_rating || ''}
          onChange={(e) => handleChange('min_rating', e.target.value)}
          className="w-full border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">Any Rating</option>
          <option value="4.5">4.5+</option>
          <option value="4">4.0+</option>
          <option value="3.5">3.5+</option>
          <option value="3">3.0+</option>
        </select>
      </div>

      {/* Available Only */}
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={filters.availability_only || false}
          onChange={(e) => handleChange('availability_only', e.target.checked)}
          className="w-4 h-4 rounded border-border text-primary focus:ring-primary"
        />
        <span className="text-sm text-text-primary">Available only</span>
      </label>

      {/* Reset */}
      <button
        onClick={() => onFilterChange({ sort: 'rating' })}
        className="w-full text-sm text-text-secondary hover:text-primary py-2 transition-colors"
      >
        Reset Filters
      </button>
    </div>
  );
}
