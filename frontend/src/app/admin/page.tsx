'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Users, Database, Upload, LogOut, ArrowLeft, Plus } from 'lucide-react';

interface User {
    id: number;
    email: string;
    full_name: string;
    role: string;
    is_active: number;
}

interface Stats {
    total_machines: number;
    connected_machines: number;
    machines_with_remote: number;
    clients_count: number;
}

export default function AdminPage() {
    const [user, setUser] = useState<any>(null);
    const [activeTab, setActiveTab] = useState<'users' | 'data'>('users');
    const [users, setUsers] = useState<User[]>([]);
    const [stats, setStats] = useState<Stats | null>(null);
    const [newUser, setNewUser] = useState({ email: '', full_name: '', password: '' });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const router = useRouter();

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        const token = localStorage.getItem('token');

        if (!storedUser || !token) {
            router.push('/login');
            return;
        }

        const parsedUser = JSON.parse(storedUser);
        if (parsedUser.role !== 'admin') {
            router.push('/dashboard');
            return;
        }

        setUser(parsedUser);
        fetchUsers();
        fetchStats();
    }, [router]);

    const fetchUsers = async () => {
        const token = localStorage.getItem('token');
        const res = await fetch('http://localhost:8001/admin/users', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) setUsers(await res.json());
    };

    const fetchStats = async () => {
        const token = localStorage.getItem('token');
        const res = await fetch('http://localhost:8001/admin/stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) setStats(await res.json());
    };

    const handleCreateUser = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        try {
            const token = localStorage.getItem('token');
            const res = await fetch('http://localhost:8001/admin/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ ...newUser, role: 'user' }) // Force role 'user'
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || 'Erreur lors de la création');
            }

            setMessage('Utilisateur créé avec succès !');
            setNewUser({ email: '', full_name: '', password: '' });
            fetchUsers();
        } catch (err: any) {
            setMessage(`Erreur: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        router.push('/login');
    };

    if (!user) return <div className="p-10 text-center">Chargement...</div>;

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <aside className="w-64 bg-cat-black text-white flex flex-col">
                <div className="p-6">
                    <h1 className="text-2xl font-bold text-cat-yellow">NEEMBA</h1>
                    <p className="text-xs uppercase tracking-widest text-gray-400">Admin Panel</p>
                </div>

                <nav className="flex-1 px-4 space-y-2">
                    <button
                        onClick={() => setActiveTab('users')}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${activeTab === 'users' ? 'bg-cat-yellow text-cat-black font-bold' : 'text-gray-300 hover:bg-gray-800'}`}
                    >
                        <Users className="w-5 h-5" /> Utilisateurs
                    </button>
                    <button
                        onClick={() => setActiveTab('data')}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${activeTab === 'data' ? 'bg-cat-yellow text-cat-black font-bold' : 'text-gray-300 hover:bg-gray-800'}`}
                    >
                        <Database className="w-5 h-5" /> Données
                    </button>
                </nav>

                <div className="p-4 border-t border-gray-800 space-y-2">
                    <button
                        onClick={() => router.push('/dashboard')}
                        className="w-full flex items-center gap-2 text-gray-400 hover:text-white px-4 py-2"
                    >
                        <ArrowLeft className="w-4 h-4" /> Retour Dashboard
                    </button>
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 text-red-400 hover:text-red-300 px-4 py-2"
                    >
                        <LogOut className="w-4 h-4" /> Déconnexion
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8 overflow-y-auto">
                <header className="mb-8">
                    <h2 className="text-3xl font-bold text-gray-800">
                        {activeTab === 'users' ? 'Gestion des Utilisateurs' : 'Gestion des Données'}
                    </h2>
                </header>

                {activeTab === 'users' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Users List */}
                        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
                            <h3 className="text-lg font-bold text-gray-700 mb-4 flex items-center gap-2">
                                <Users className="w-5 h-5" /> Liste des comptes
                            </h3>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                        <tr>
                                            <th className="px-4 py-3">Nom</th>
                                            <th className="px-4 py-3">Email</th>
                                            <th className="px-4 py-3">Rôle</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100">
                                        {users.map(u => (
                                            <tr key={u.id}>
                                                <td className="px-4 py-3 font-medium text-gray-900">{u.full_name}</td>
                                                <td className="px-4 py-3 text-gray-500">{u.email}</td>
                                                <td className="px-4 py-3">
                                                    <span className={`px-2 py-1 rounded text-xs font-bold ${u.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'}`}>
                                                        {u.role}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* Create User Form */}
                        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 h-fit">
                            <h3 className="text-lg font-bold text-gray-700 mb-4 flex items-center gap-2">
                                <Plus className="w-5 h-5" /> Nouvel Utilisateur
                            </h3>
                            <form onSubmit={handleCreateUser} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Nom Complet</label>
                                    <input
                                        type="text" required
                                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-cat-yellow outline-none"
                                        value={newUser.full_name}
                                        onChange={e => setNewUser({ ...newUser, full_name: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Email (@neemba.com)</label>
                                    <input
                                        type="email" required
                                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-cat-yellow outline-none"
                                        value={newUser.email}
                                        onChange={e => setNewUser({ ...newUser, email: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Mot de passe temporaire</label>
                                    <input
                                        type="text" required
                                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-cat-yellow outline-none font-mono bg-gray-50"
                                        value={newUser.password}
                                        onChange={e => setNewUser({ ...newUser, password: e.target.value })}
                                        placeholder="ex: Neemba2024!"
                                    />
                                </div>
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full bg-cat-black text-white font-bold py-2 rounded-lg hover:bg-gray-800 transition disabled:opacity-50"
                                >
                                    {loading ? 'Création...' : 'Créer le compte'}
                                </button>
                                {message && (
                                    <div className={`text-sm p-2 rounded ${message.includes('Erreur') ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                                        {message}
                                    </div>
                                )}
                            </form>
                        </div>
                    </div>
                )}

                {activeTab === 'data' && (
                    <div className="space-y-8">
                        {/* Stats Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                <p className="text-sm text-gray-500 font-bold uppercase">Total Machines</p>
                                <p className="text-3xl font-extrabold text-cat-black mt-2">{stats?.total_machines || 0}</p>
                            </div>
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                <p className="text-sm text-gray-500 font-bold uppercase">Clients</p>
                                <p className="text-3xl font-extrabold text-blue-600 mt-2">{stats?.clients_count || 0}</p>
                            </div>
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                <p className="text-sm text-gray-500 font-bold uppercase">Connectées (GPS)</p>
                                <p className="text-3xl font-extrabold text-green-600 mt-2">{stats?.connected_machines || 0}</p>
                            </div>
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                <p className="text-sm text-gray-500 font-bold uppercase">Remote Service</p>
                                <p className="text-3xl font-extrabold text-orange-600 mt-2">{stats?.machines_with_remote || 0}</p>
                            </div>
                        </div>

                        {/* Upload Section (Placeholder for now, redirect logic or use existing component?) */}
                        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
                            <Upload className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                            <h3 className="text-xl font-bold text-gray-800 mb-2">Mise à jour des données</h3>
                            <p className="text-gray-500 mb-6">
                                Pour mettre à jour la base de données, utilisez le script d'ingestion ou l'interface d'upload.
                                <br />(Bientôt disponible ici directement).
                            </p>
                            <button className="bg-cat-yellow text-cat-black font-bold py-2 px-6 rounded-lg hover:bg-yellow-500 transition">
                                Uploader un fichier
                            </button>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
