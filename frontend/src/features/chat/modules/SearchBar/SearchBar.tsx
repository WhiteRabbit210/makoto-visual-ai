import React, { useState } from 'react';
import { Search } from 'lucide-react';

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({ 
  placeholder = "チャットを検索...",
  onSearch 
}) => {
  const [query, setQuery] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;
    setQuery(newQuery);
    onSearch?.(newQuery);
  };

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
      <input
        type="text"
        value={query}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full pl-9 pr-3 py-2 bg-bg-secondary rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-blue/20 transition-all"
      />
    </div>
  );
};