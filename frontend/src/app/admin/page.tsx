'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Users, Database, Upload, LogOut, ArrowLeft, Plus, Trash2, Pencil } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

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
    const [user, setUser] = useState<{ name: string; email: string; role: string } | null>(null);
    const [activeTab, setActiveTab] = useState<'users' | 'data'>('users');
    const [users, setUsers] = useState<User[]>([]);
    const [stats, setStats] = useState<Stats | null>(null);
    const [newUser, setNewUser] = useState({ email: '', full_name: '', password: '' });
    const [editingUser, setEditingUser] = useState<User | null>(null);
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
        const res = await fetch(`${API_URL}/admin/users`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) setUsers(await res.json());
    };

    const fetchStats = async () => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_URL}/admin/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) setStats(await res.json());
    };

    const handleCreateOrUpdateUser = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        try {
            const token = localStorage.getItem('token');
            const url = editingUser
                ? `${API_URL}/admin/users/${editingUser.id}`
                : `${API_URL}/admin/users`;

            const method = editingUser ? 'PUT' : 'POST';

            // For update, exclude empty password if not changing it
            const body: Partial<typeof newUser> & { role: string } = { ...newUser, role: 'user' };
            if (editingUser && !newUser.password) {
                delete body.password;
            }

            const res = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(body)
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || 'Erreur lors de l\'opération');
            }

            setMessage(editingUser ? 'Utilisateur modifié !' : 'Utilisateur créé avec succès !');
            setNewUser({ email: '', full_name: '', password: '' });
            setEditingUser(null);
            fetchUsers();
        } catch (err: unknown) {
            setMessage(`Erreur: ${err instanceof Error ? err.message : 'Erreur inconnue'}`);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteUser = async (userId: number) => {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) return;

        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/admin/users/${userId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                fetchUsers();
            } else {
                alert("Erreur lors de la suppression");
            }
        } catch (error) {
            console.error(error);
        }
    };

    const startEdit = (user: User) => {
        setEditingUser(user);
        setNewUser({
            email: user.email,
            full_name: user.full_name,
            password: '' // Don't fill password
        });
        setMessage('');
    };

    const cancelEdit = () => {
        setEditingUser(null);
        setNewUser({ email: '', full_name: '', password: '' });
        setMessage('');
    };

    const handleUpload = async (file: File) => {
        setLoading(true);
        setMessage('');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_URL}/admin/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || "Erreur lors de l'upload");
            }

            setMessage('Fichier uploadé et traité avec succès !');
            fetchStats(); // Refresh stats
        } catch (error: unknown) {
            setMessage(`Erreur: ${error instanceof Error ? error.message : 'Erreur inconnue'}`);
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
                                            <th className="px-4 py-3 text-right">Actions</th>
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
                                                <td className="px-4 py-3 flex gap-2 justify-end">
                                                    <button onClick={() => startEdit(u)} className="p-1 text-blue-600 hover:bg-blue-50 rounded">
                                                        <Pencil size={16} />
                                                    </button>
                                                    {u.role !== 'admin' && (
                                                        <button onClick={() => handleDeleteUser(u.id)} className="p-1 text-red-600 hover:bg-red-50 rounded">
                                                            <Trash2 size={16} />
                                                        </button>
                                                    )}
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
                                <Plus className="w-5 h-5" /> {editingUser ? 'Modifier Utilisateur' : 'Nouvel Utilisateur'}
                            </h3>
                            <form onSubmit={handleCreateOrUpdateUser} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Nom Complet</label>
                                    <input
                                        type="text" required
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cat-yellow outline-none text-gray-900 bg-gray-50 placeholder-gray-400"
                                        value={newUser.full_name}
                                        onChange={e => setNewUser({ ...newUser, full_name: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Email (@neemba.com)</label>
                                    <input
                                        type="email" required
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cat-yellow outline-none text-gray-900 bg-gray-50 placeholder-gray-400"
                                        value={newUser.email}
                                        onChange={e => setNewUser({ ...newUser, email: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        {editingUser ? 'Nouveau mot de passe (laisser vide pour ne pas changer)' : 'Mot de passe temporaire'}
                                    </label>
                                    <input
                                        type="text"
                                        required={!editingUser}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cat-yellow outline-none font-mono text-gray-900 bg-gray-50 placeholder-gray-400"
                                        value={newUser.password}
                                        onChange={e => setNewUser({ ...newUser, password: e.target.value })}
                                        placeholder={editingUser ? "Optionnel" : "ex: Neemba2024!"}
                                    />
                                </div>
                                <div className="flex gap-2">
                                    {editingUser && (
                                        <button
                                            type="button"
                                            onClick={cancelEdit}
                                            className="flex-1 bg-gray-200 text-gray-800 font-bold py-2 rounded-lg hover:bg-gray-300 transition"
                                        >
                                            Annuler
                                        </button>
                                    )}
                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="flex-1 bg-cat-black text-white font-bold py-2 rounded-lg hover:bg-gray-800 transition disabled:opacity-50"
                                    >
                                        {loading ? 'En cours...' : (editingUser ? 'Mettre à jour' : 'Créer le compte')}
                                    </button>
                                </div>
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
                                Sélectionnez le fichier <strong>Programmes.xlsx</strong> pour mettre à jour la base de données.
                                <br />Le traitement peut prendre quelques minutes.
                            </p>

                            <div className="max-w-md mx-auto">
                                <label className="block mb-4 cursor-pointer">
                                    <span className="sr-only">Choisir un fichier</span>
                                    <input
                                        type="file"
                                        accept=".xlsx"
                                        onChange={(e) => {
                                            const file = e.target.files?.[0];
                                            if (file) handleUpload(file);
                                        }}
                                        disabled={loading}
                                        className="block w-full text-sm text-gray-500
                                            file:mr-4 file:py-2 file:px-4
                                            file:rounded-full file:border-0
                                            file:text-sm file:font-semibold
                                            file:bg-cat-yellow file:text-cat-black
                                            hover:file:bg-yellow-400
                                        "
                                    />
                                </label>

                                {loading && (
                                    <div className="text-blue-600 font-bold animate-pulse">
                                        Upload et ingestion en cours...
                                    </div>
                                )}

                                {message && (
                                    <div className={`mt-4 p-3 rounded-lg text-sm font-medium ${message.includes('succès') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                        {message}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
