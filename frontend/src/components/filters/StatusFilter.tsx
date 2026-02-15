'use client';

import { useFilters } from '@/contexts/FilterContext';

export default function StatusFilter() {
    const { filters, setFilters } = useFilters();

    const statusOptions = [
        { value: 'critical', label: 'Action Requise (Urgent)', color: 'bg-red-500', icon: '🔴' },
        { value: 'maintenance', label: 'Maintenance Prévue', color: 'bg-orange-500', icon: '🟠' },
        { value: 'operational', label: 'Opérationnel', color: 'bg-green-500', icon: '🟢' },
    ] as const;

    const toggleStatus = (status: 'operational' | 'maintenance' | 'critical') => {
        const newStatus = filters.status.includes(status)
            ? filters.status.filter(s => s !== status)
            : [...filters.status, status];
        setFilters({ status: newStatus });
    };

    return (
        <div>
            <h4 className="text-sm font-bold text-gray-700 mb-3">Statut</h4>
            <div className="space-y-2">
                {statusOptions.map(option => (
                    <label
                        key={option.value}
                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition"
                    >
                        <input
                            type="checkbox"
                            checked={filters.status.includes(option.value)}
                            onChange={() => toggleStatus(option.value)}
                            className="w-4 h-4 text-cat-yellow focus:ring-cat-yellow rounded"
                        />
                        <span className={`w-3 h-3 rounded-full ${option.color}`}></span>
                        <span className="text-sm text-gray-800 flex-1">{option.label}</span>
                    </label>
                ))}
            </div>
        </div>
    );
}
