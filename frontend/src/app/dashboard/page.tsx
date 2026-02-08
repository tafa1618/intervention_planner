
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Map from '@/components/ui/Map';
import { MOCK_MACHINES, Machine } from '@/lib/mock-data';
import { Search, MessageSquare, MapPin, Settings, LogOut, Send } from 'lucide-react';

export default function Dashboard() {
    const router = useRouter();
    const [machines, setMachines] = useState<Machine[]>(MOCK_MACHINES);
    const [messages, setMessages] = useState<{ role: 'user' | 'assistant', text: string }[]>([
        { role: 'assistant', text: 'Bonjour ! Je suis votre assistant de tournée. Où devez-vous intervenir aujourd\'hui ? (ex: "Client GCO" ou "Dakar")' }
    ]);
    const [input, setInput] = useState('');
    const [user, setUser] = useState<{ name: string, email: string } | null>(null);

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (!storedUser) {
            router.push('/login');
        } else {
            setUser(JSON.parse(storedUser));
        }
    }, [router]);

    const handleSendMessage = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        // Add user message
        const newMessages = [...messages, { role: 'user', text: input } as const];
        setMessages(newMessages);
        const query = input.toLowerCase();
        setInput('');

        // Mock AI Logic
        setTimeout(() => {
            let responseText = '';
            let filteredMachines = MOCK_MACHINES;

            if (query.includes('gco') || query.includes('grande côte')) {
                filteredMachines = MOCK_MACHINES.filter(m => m.client.includes('GCO'));
                responseText = `J'ai trouvé ${filteredMachines.length} machines pour le client GCO. Je les ai mises en évidence sur la carte. Voulez-vous optimiser la tournée pour inclure les inspections proches ?`;
            } else if (query.includes('sabodala') || query.includes('kedougou')) {
                filteredMachines = MOCK_MACHINES.filter(m => m.client.includes('Sabodala'));
                responseText = `Zone Sabodala isolée. 2 machines détectées dont 1 en panne. C'est un déplacement long, je suggère de grouper avec les inspections PSSR du mois prochain.`;
            } else {
                responseText = "Je ne suis pas sûr de comprendre. Essayez de taper un nom de client comme 'GCO' ou 'Sabodala'.";
            }

            setMessages(prev => [...prev, { role: 'assistant', text: responseText }]);
            // In a real app, we would zoom to these machines. For now, we update the map data if needed or just keep all.
            // Let's filter the map for visual feedback
            if (filteredMachines.length > 0 && filteredMachines.length < MOCK_MACHINES.length) {
                setMachines(filteredMachines);
            } else {
                setMachines(MOCK_MACHINES); // Reset if clear or confusing
            }

        }, 1000);
    };

    if (!user) return null;

    return (
        <div className="flex h-screen bg-gray-100 overflow-hidden font-sans">
            {/* Sidebar Navigation */}
            <aside className="w-64 bg-cat-black text-white flex flex-col shadow-2xl z-20">
                <div className="p-6 border-b border-gray-800">
                    <h1 className="text-2xl font-bold text-cat-yellow tracking-tighter">NEEMBA</h1>
                    <p className="text-xs text-gray-400 uppercase tracking-widest mt-1">Intervention Planner</p>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <NavItem icon={<MapPin size={20} />} label="Carte Globale" active />
                    <NavItem icon={<Search size={20} />} label="Recherche Avancée" />
                    <NavItem icon={<Settings size={20} />} label="Paramètres" />
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
            <main className="flex-1 flex flex-col relative">
                {/* Header - could be breadcrumbs or global actions */}
                <header className="h-14 bg-white border-b border-gray-200 flex items-center px-6 shadow-sm z-10 justify-between">
                    <h2 className="font-bold text-gray-800">Tableau de Bord - Optimisation</h2>
                    <div className="flex gap-2">
                        <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-bold">Système: Opérationnel</span>
                    </div>
                </header>

                <div className="flex-1 flex relative">
                    {/* Map Area */}
                    <div className="flex-1 relative bg-gray-200">
                        <Map machines={machines} />

                        {/* Floating Legend / Info */}
                        <div className="absolute top-4 right-4 bg-white/90 backdrop-blur p-4 rounded-lg shadow-lg z-[400] max-w-xs">
                            <h3 className="font-bold text-sm mb-2 text-gray-800">Légende</h3>
                            <div className="space-y-2 text-xs">
                                <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-green-500"></span> Opérationnel</div>
                                <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-orange-500"></span> Maintenance Prévue</div>
                                <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500"></span> En Panne (Urgent)</div>
                            </div>
                        </div>
                    </div>

                    {/* Right Panel: Assistant / Chat */}
                    <div className="w-96 bg-white border-l border-gray-200 flex flex-col shadow-xl z-10">
                        <div className="p-4 border-b border-gray-100 flex items-center gap-2 bg-gray-50">
                            <MessageSquare size={18} className="text-cat-yellow fill-cat-black" />
                            <h3 className="font-bold text-gray-800">Assistant de Tournée</h3>
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
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
                        </div>

                        <div className="p-4 bg-white border-t border-gray-200">
                            <form onSubmit={handleSendMessage} className="relative">
                                <input
                                    type="text"
                                    className="w-full pl-4 pr-10 py-3 bg-gray-100 border-none rounded-full text-sm focus:ring-2 focus:ring-cat-yellow outline-none transition text-gray-900"
                                    placeholder="Écrivez votre demande..."
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

function NavItem({ icon, label, active = false }: { icon: React.ReactNode, label: string, active?: boolean }) {
    return (
        <button className={`w-full flex items-center gap-3 px-4 py-3 rounded-md transition ${active
            ? 'bg-cat-yellow text-cat-black font-bold'
            : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            }`}>
            {icon}
            <span className="text-sm">{label}</span>
        </button>
    )
}
