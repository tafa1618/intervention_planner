'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { FilterProvider } from '@/contexts/FilterContext';
import { useFilteredMachines } from '@/lib/useFilteredMachines';
import { Machine } from '@/lib/types';
import { fetchMachines } from '@/lib/api';
import Map from '@/components/ui/Map';
import GlobalSearch from '@/components/GlobalSearch';
import FilterDrawer from '@/components/FilterDrawer';
import { MessageSquare, Trash2, Send, MapPin, Filter, Search, Settings, LogOut } from 'lucide-react';

function DashboardContent() {
    const router = useRouter();
    const [machines, setMachines] = useState<Machine[]>([]);
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [messages, setMessages] = useState<
        { role: 'user' | 'assistant'; text: string }[]
    >([
        {
            role: 'assistant',
            text: `Bonjour ! Je suis votre assistant de tournée. Où devez-vous intervenir aujourd'hui ? (ex: "Client GCO" ou "Dakar")`,
        },
    ]);

    const [input, setInput] = useState('');
    const [user, setUser] = useState<{ name: string, email: string, role?: string } | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Use filtered machines hook
    const filteredMachines = useFilteredMachines(machines);

    // Map State
    const [mapCenter, setMapCenter] = useState<[number, number] | undefined>(undefined);
    const [mapZoom, setMapZoom] = useState<number | undefined>(undefined);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    };

    useEffect(() => {
        const timeoutId = setTimeout(() => scrollToBottom(), 100);
        return () => clearTimeout(timeoutId);
    }, [messages]);

    const handleLocate = (lat: number, lng: number) => {
        setMapCenter([lat, lng]);
        setMapZoom(12);
    };

    const handleSearchClick = () => {
        if (inputRef.current) {
            inputRef.current.focus();
            setMessages(prev => [...prev, { role: 'assistant', text: "Je vous écoute. Tapez un nom de client ou un numéro de série." }]);
        }
    };

    useEffect(() => {
        try {
            const storedUser = localStorage.getItem('user');
            if (!storedUser) {
                router.push('/login');
            } else {
                setUser(JSON.parse(storedUser));
            }
        } catch (e) {
            console.error("Auth Error:", e);
            router.push('/login');
        }
    }, []);

    useEffect(() => {
        async function loadData() {
            try {
                const data = await fetchMachines();
                setMachines(data);
            } catch (error) {
                console.error("Failed to load machines", error);
            }
        }
        if (user) {
            loadData();
        }
    }, [user]);

    if (!user) {
        return (
            <div className="flex h-screen items-center justify-center bg-gray-100">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cat-yellow mx-auto mb-4"></div>
                    <p className="text-gray-600">Chargement de la session...</p>
                </div>
            </div>
        );
    }

    const handleClearChat = async () => {
        setMessages([{ role: 'assistant', text: 'Historique effacé. Carte réinitialisée.' }]);
        try {
            const data = await fetchMachines();
            setMachines(data);
        } catch (error) {
            console.error("Failed to reset map", error);
        }
    };

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userText = input;
        setMessages(prev => [...prev, { role: 'user', text: userText }]);
        setInput('');

        try {
            const results = await fetchMachines(userText);
            setMachines(results);

            const count = results.length;
            const criticalMachines = results.filter(m => m.status === 'critical');
            const maintenanceCount = results.filter(m => m.status === 'maintenance').length;
            const operationalCount = results.filter(m => m.status === 'operational').length;

            let responseText = `Résultat pour "${userText}" : ${count} machine(s) trouvée(s).`;

            if (count > 0) {
                if (criticalMachines.length > 0) {
                    responseText += `\\n\\n🔴 ${criticalMachines.length} ACTION(S) REQUISE(S) :`;
                    criticalMachines.slice(0, 5).forEach(m => {
                        const interventions = m.pendingInterventions
                            .filter(i => i.priority === 'HIGH' || i.status === 'PENDING')
                            .map(i => {
                                const desc = i.description || 'Intervention critique';
                                return desc.length > 50 ? desc.substring(0, 50) + '...' : desc;
                            })
                            .join(', ');
                        responseText += `\\n- ${m.serialNumber} : ${interventions}`;
                    });
                    if (criticalMachines.length > 5) responseText += `\\n...et ${criticalMachines.length - 5} autres.`;
                }

                if (maintenanceCount > 0) responseText += `\\n\\n🟠 ${maintenanceCount} Maintenance(s) Prévue(s)`;
                if (operationalCount > 0) responseText += `\\n🟢 ${operationalCount} Opérationnelle(s)`;

                const noLocation = results.filter(m => m.location.lat === 0 && m.location.lng === 0).length;
                if (noLocation > 0) {
                    responseText += `\\n⚠️ ${noLocation} machine(s) sans position GPS.`;
                }
            } else {
                responseText += " Aucune correspondance.";
            }

            setMessages(prev => [...prev, { role: 'assistant', text: responseText }]);

        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', text: "Erreur lors de la recherche." }]);
        }
    };

    const handleReset = async () => {
        try {
            const data = await fetchMachines();
            setMachines(data);
            setMessages(prev => [...prev, { role: 'assistant', text: "Affichage de la vue globale (toutes les machines)." }]);
        } catch (error) {
            console.error("Failed to reset map", error);
        }
    };

    return (
        <div className="flex h-screen bg-gray-100 overflow-hidden font-sans">
            {/* Filter Drawer */}
            <FilterDrawer machines={machines} isOpen={isFilterOpen} onClose={() => setIsFilterOpen(false)} />

            {/* Sidebar Navigation */}
            <aside className="w-64 bg-cat-black text-white flex flex-col shadow-2xl z-20">
                <div className="p-6 border-b border-gray-800">
                    <h1 className="text-2xl font-bold text-cat-yellow tracking-tighter">NEEMBA</h1>
                    <p className="text-xs text-gray-400 uppercase tracking-widest mt-1">Intervention Planner</p>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <NavItem icon={<MapPin size={20} />} label="Carte Globale" active onClick={handleReset} />
                    <NavItem icon={<Filter size={20} />} label="Filtres Avancés" onClick={() => setIsFilterOpen(!isFilterOpen)} />
                    <NavItem icon={<Search size={20} />} label="Recherche Avancée" onClick={handleSearchClick} />
                    {user?.role === 'admin' && (
                        <NavItem
                            icon={<Settings size={20} />}
                            label="Admin / Paramètres"
                            onClick={() => router.push('/admin')}
                        />
                    )}
                </nav>

                <div className="p-4 border-t border-gray-800">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-8 h-8 rounded-full bg-cat-yellow text-cat-black flex items-center justify-center font-bold">
                            {user.name ? user.name[0] : 'U'}
                        </div>
                        <div>
                            <p className="text-sm font-bold">{user.name || 'Utilisateur'}</p>
                            <p className="text-xs text-gray-400">{user.email}</p>
                        </div>
                    </div>
                    <button
                        onClick={() => { localStorage.removeItem('user'); router.push('/login'); }}
                        className="flex items-center gap-2 text-sm text-red-400 hover:text-red-300 transition"
                    >
                        <LogOut size={16} /> Déconnexion
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col relative min-h-0 overflow-hidden">
                {/* Header */}
                <header className="h-14 bg-white border-b border-gray-200 flex items-center px-6 shadow-sm z-10 justify-between shrink-0">
                    <h2 className="font-bold text-gray-800">Tableau de Bord - Optimisation</h2>
                    <div className="flex gap-2">
                        <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-bold">Système: Opérationnel</span>
                    </div>
                </header>

                <div className="flex-1 flex relative min-h-0 overflow-hidden">
                    {/* Map Area */}
                    <div className="flex-1 relative bg-gray-200 min-h-0 min-w-0">
                        <Map machines={filteredMachines} center={mapCenter} zoom={mapZoom} />

                        {/* Global Search Overlay */}
                        <div className="absolute top-4 left-16 z-[1000]">
                            <GlobalSearch onLocate={handleLocate} />
                        </div>

                        {/* Floating Legend / Info */}
                        <div className="absolute top-4 right-4 bg-white/90 backdrop-blur p-4 rounded-lg shadow-lg z-[400] max-w-xs">
                            <h3 className="font-bold text-sm mb-2 text-gray-900">Légende</h3>
                            <div className="space-y-2 text-xs text-gray-800">
                                <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-green-500 border border-white shadow-sm"></span> Opérationnel</div>
                                <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-orange-500 border border-white shadow-sm"></span> Maintenance Prévue</div>
                                <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500 border border-white shadow-sm"></span> Action Requise (Urgent)</div>
                            </div>
                        </div>
                    </div>

                    {/* Right Panel: Assistant / Chat */}
                    <div className="w-96 bg-white border-l border-gray-200 flex flex-col shadow-xl z-10 h-full max-h-full">
                        <div className="shrink-0 p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50">
                            <div className="flex items-center gap-2">
                                <MessageSquare size={18} className="text-cat-yellow fill-cat-black" />
                                <h3 className="font-bold text-gray-800">Assistant de Tournée</h3>
                            </div>
                            <button onClick={handleClearChat} className="text-gray-400 hover:text-red-500 transition" title="Effacer l'historique">
                                <Trash2 size={16} />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto min-h-0 p-4 space-y-4 bg-gray-50/50">
                            {messages.map((msg, idx) => (
                                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[85%] p-3 rounded-lg text-sm shadow-sm ${msg.role === 'user'
                                        ? 'bg-cat-black text-white rounded-br-none'
                                        : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none'
                                        }`}>
                                        {msg.text}
                                    </div>
                                </div>
                            ))}
                            <div ref={messagesEndRef} />
                        </div>

                        <div className="shrink-0 p-4 bg-white border-t border-gray-200">
                            <form onSubmit={handleSendMessage} className="relative">
                                <input
                                    ref={inputRef}
                                    type="text"
                                    className="w-full pl-4 pr-10 py-3 bg-gray-100 border-none rounded-full text-sm focus:ring-2 focus:ring-cat-yellow outline-none transition text-gray-900"
                                    placeholder="Rechercher (Client, Série) ou discuter..."
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                />
                                <button
                                    type="submit"
                                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-cat-yellow text-cat-black rounded-full hover:bg-yellow-400 transition shadow-sm"
                                >
                                    <Send size={16} />
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

function NavItem({ icon, label, active = false, onClick }: { icon: React.ReactNode, label: string, active?: boolean, onClick?: () => void }) {
    return (
        <button onClick={onClick} className={`w-full flex items-center gap-3 px-4 py-3 rounded-md transition ${active
            ? 'bg-cat-yellow text-cat-black font-bold'
            : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            }`}>
            {icon}
            <span className="text-sm">{label}</span>
        </button>
    )
}

// Main export with FilterProvider wrapper
export default function Dashboard() {
    return (
        <FilterProvider>
            <DashboardContent />
        </FilterProvider>
    );
}
