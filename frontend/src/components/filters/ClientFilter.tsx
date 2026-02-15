'use client';

import { useMemo, useState } from 'react';
import { useFilters } from '@/contexts/FilterContext';
import { Machine } from '@/lib/types';
import { Search } from 'lucide-react';

interface ClientFilterProps {
    machines: Machine[];
}

export default function ClientFilter({ machines }: ClientFilterProps) {
    const { filters, setFilters } = useFilters();
    const [searchTerm, setSearchTerm] = useState('');

    // Extract unique clients with counts
    const clientList = useMemo(() => {
        const clientCounts = machines.reduce((acc, machine) => {
            const client = machine.client;
            acc[client] = (acc[client] || 0) + 1;
            return acc;
        }, {} as Record<string, number>);

        return Object.entries(clientCounts)
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => a.name.localeCompare(b.name));
    }, [machines]);

    // Filter clients based on search
    const filteredClientList = useMemo(() => {
        if (!searchTerm) return clientList;
        return clientList.filter(client =>
            client.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [clientList, searchTerm]);

    const toggleClient = (clientName: string) => {
        const newClients = filters.clients.includes(clientName)
            ? filters.clients.filter(c => c !== clientName)
            : [...filters.clients, clientName];
        setFilters({ clients: newClients });
    };

    return (
        <div>
            <h4 className="text-sm font-bold text-gray-700 mb-3">Client</h4>

            {/* Search input */}
            <div className="relative mb-3">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                    type="text"
                    placeholder="Rechercher un client..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cat-yellow"
                />
            </div>

            {/* Client list */}
            <div className="space-y-1 max-h-60 overflow-y-auto">
                {filteredClientList.map(client => (
                    <label
                        key={client.name}
                        className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition"
                    >
                        <input
                            type="checkbox"
                            checked={filters.clients.includes(client.name)}
                            onChange={() => toggleClient(client.name)}
                            className="w-4 h-4 text-cat-yellow focus:ring-cat-yellow rounded"
                        />
                        <span className="text-sm text-gray-800 flex-1">{client.name}</span>
                        <span className="text-xs text-gray-500">({client.count})</span>
                    </label>
                ))}
                {filteredClientList.length === 0 && (
                    <p className="text-sm text-gray-400 text-center py-4">Aucun client trouvé</p>
                )}
            </div>
        </div>
    );
}
