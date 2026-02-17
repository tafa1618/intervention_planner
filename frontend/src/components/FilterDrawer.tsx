'use client';

import { useState } from 'react';
import { X, Filter } from 'lucide-react';
import { useFilters } from '@/contexts/FilterContext';
import { Machine } from '@/lib/types';
import { fetchClients, ClientStats } from '@/lib/api';
import { useEffect } from 'react';

interface FilterDrawerProps {
    machines: Machine[]; // All machines for extracting unique clients/regions
    isOpen: boolean;
    onClose: () => void;
}

export default function FilterDrawer({ machines, isOpen, onClose }: FilterDrawerProps) {
    const { activeCount, resetFilters } = useFilters();
    const [allClients, setAllClients] = useState<ClientStats[]>([]);

    useEffect(() => {
        async function loadClients() {
            const data = await fetchClients();
            setAllClients(data);
        }
        if (isOpen) {
            loadClients();
        }
    }, [isOpen]);

    return (
        <>
            {/* Backdrop */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/20 z-30 transition-opacity"
                    onClick={onClose}
                />
            )}

            {/* Drawer */}
            <div
                className={`fixed left-0 top-0 h-full w-80 bg-white shadow-2xl z-40 transform transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-64' : '-translate-x-full'
                    }`}
            >
                {/* Header */}
                <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
                    <div className="flex items-center gap-2">
                        <Filter size={18} className="text-cat-yellow" />
                        <h3 className="font-bold text-gray-800">Filtres Avancés</h3>
                        {activeCount > 0 && (
                            <span className="bg-cat-yellow text-cat-black text-xs px-2 py-0.5 rounded-full font-bold">
                                {activeCount}
                            </span>
                        )}
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition"
                    >
                        <X size={20} />
                    </button>
                </div>

                <div className="p-4 space-y-6 overflow-y-auto h-[calc(100%-140px)]">
                    <StatusFilter />
                    <ClientFilter clients={allClients} />
                </div>

                {/* Footer */}
                <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white">
                    <button
                        onClick={resetFilters}
                        className="w-full py-2 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition font-medium text-sm"
                    >
                        Réinitialiser les filtres
                    </button>
                </div>
            </div>
        </>
    );
}
