import { createContext, useContext, useState, ReactNode, useMemo } from 'react';

export interface FilterState {
    status: ('operational' | 'maintenance' | 'critical')[];
    regions: string[];
    clients: string[];
}

interface FilterContextType {
    filters: FilterState;
    setFilters: (filters: Partial<FilterState>) => void;
    activeCount: number;
    resetFilters: () => void;
}

const defaultFilters: FilterState = {
    status: [],
    regions: [],
    clients: [],
};

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export function FilterProvider({ children }: { children: ReactNode }) {
    const [filters, setFiltersState] = useState<FilterState>(defaultFilters);

    const setFilters = (newFilters: Partial<FilterState>) => {
        setFiltersState(prev => ({ ...prev, ...newFilters }));
    };

    const resetFilters = () => {
        setFiltersState(defaultFilters);
    };

    const activeCount = useMemo(() => {
        return filters.status.length + filters.regions.length + filters.clients.length;
    }, [filters]);

    return (
        <FilterContext.Provider value={{ filters, setFilters, activeCount, resetFilters }}>
            {children}
        </FilterContext.Provider>
    );
}

export function useFilters() {
    const context = useContext(FilterContext);
    if (!context) {
        throw new Error('useFilters must be used within FilterProvider');
    }
    return context;
}
