'use client';

import { useState, useEffect } from 'react';
import { Search, MapPin, AlertCircle, CheckCircle, XCircle, Clock } from 'lucide-react';
import { searchGlobalContext } from '@/lib/api';
import { MachineContext } from '@/lib/types';

interface GlobalSearchProps {
    onLocate: (lat: number, lng: number) => void;
}

export default function GlobalSearch({ onLocate }: GlobalSearchProps) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<MachineContext[]>([]);
    const [loading, setLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(false);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(async () => {
            if (query.length >= 2) {
                setLoading(true);
                const data = await searchGlobalContext(query);
                setResults(data);
                setLoading(false);
                setIsOpen(true);
            } else {
                setResults([]);
                setIsOpen(false);
            }
        }, 500);

        return () => clearTimeout(timer);
    }, [query]);

    const StatusBadge = ({ label, status, color }: { label: string, status: any, color: string }) => {
        if (!status) return <span className="text-xs text-gray-300 ml-1 opacity-50">{label}</span>;

        let displayColor = 'text-gray-500';
        if (color === 'green') displayColor = 'text-green-600';
        if (color === 'red') displayColor = 'text-red-500';
        if (color === 'orange') displayColor = 'text-orange-500';
        if (color === 'blue') displayColor = 'text-blue-500';

        return (
            <span className={`text-xs font-medium px-1.5 py-0.5 rounded border border-current ${displayColor} bg-opacity-10 ml-1 flex items-center gap-0.5`}>
                {label}
            </span>
        );
    };

    return (
        <div className="absolute top-4 left-16 z-[1000] w-96 font-sans">
            <div className="relative">
                <input
                    type="text"
                    placeholder="Global Search (Client, Serial, Model)..."
                    className="w-full pl-10 pr-4 py-3 rounded-lg shadow-xl border-0 focus:ring-2 focus:ring-cat-yellow bg-white/95 backdrop-blur-sm text-gray-800"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={() => query.length >= 2 && setIsOpen(true)}
                />
                <Search className="absolute left-3 top-3.5 text-gray-400 w-5 h-5" />
                {loading && (
                    <div className="absolute right-3 top-3.5 animate-spin rounded-full h-5 w-5 border-b-2 border-cat-yellow"></div>
                )}
            </div>

            {isOpen && results.length > 0 && (
                <div className="mt-2 bg-white rounded-lg shadow-2xl max-h-[70vh] overflow-y-auto border border-gray-100">
                    <div className="p-2 text-xs font-bold text-gray-400 uppercase tracking-wider sticky top-0 bg-gray-50 border-b">
                        Found {results.length} machines
                    </div>
                    {results.map((machine) => (
                        <div key={machine.id} className="p-3 hover:bg-gray-50 border-b last:border-0 transition-colors">
                            <div className="flex justify-between items-start mb-1">
                                <div>
                                    <div className="font-bold text-gray-800 flex items-center gap-2">
                                        {machine.serialNumber}
                                        <span className="text-xs font-normal text-gray-500 bg-gray-100 px-1 rounded">{machine.model}</span>
                                    </div>
                                    <div className="text-sm text-cat-black font-semibold">{machine.client}</div>
                                </div>
                                {machine.location && (
                                    <button
                                        onClick={() => {
                                            if (machine.location) {
                                                onLocate(machine.location.lat, machine.location.lng);
                                                setIsOpen(false);
                                            }
                                        }}
                                        className="text-cat-yellow hover:text-yellow-600 p-1 rounded-full hover:bg-yellow-50 transition-colors"
                                        title="Locate on map"
                                    >
                                        <MapPin className="w-5 h-5" />
                                    </button>
                                )}
                            </div>

                            {/* Program Status Grid */}
                            <div className="flex flex-wrap gap-1 mt-2">
                                {/* VisionLink */}
                                {machine.programs.visionLink ? (
                                    <StatusBadge label="VL" status={true} color="green" />
                                ) : (
                                    <StatusBadge label="VL" status={true} color="gray" /> // Show distinct inactive?
                                )}

                                {/* CVAF */}
                                <StatusBadge
                                    label="CVA"
                                    status={machine.programs.cvaf}
                                    color={machine.programs.cvaf ? 'blue' : 'gray'}
                                />

                                {/* Inspection */}
                                <StatusBadge
                                    label="ISP"
                                    status={machine.programs.inspection}
                                    color={machine.programs.inspection ? 'orange' : 'gray'}
                                />

                                {/* Remote Service */}
                                <StatusBadge
                                    label="RMT"
                                    status={machine.programs.remoteService}
                                    color={machine.programs.remoteService === '1/1' ? 'green' : machine.programs.remoteService ? 'red' : 'gray'}
                                />
                                {/* Suivi PS */}
                                {machine.programs.suiviPs && machine.programs.suiviPs > 0 ? (
                                    <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-red-100 text-red-600 border border-red-200 ml-1">
                                        PS: {machine.programs.suiviPs}
                                    </span>
                                ) : null}

                            </div>

                            {!machine.location && (
                                <div className="mt-2 text-xs text-red-400 italic flex items-center gap-1">
                                    <AlertCircle className="w-3 h-3" /> No GPS Location
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
            {isOpen && results.length === 0 && !loading && (
                <div className="mt-2 bg-white rounded-lg shadow-xl p-4 text-center text-gray-500">
                    No results found.
                </div>
            )}
        </div>
    );
}
