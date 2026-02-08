
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const router = useRouter();

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        if (!email.endsWith('@neemba.com')) {
            setError('Accès restreint aux employés Neemba uniquement (@neemba.com)');
            return;
        }
        if (password.length < 4) {
            setError('Mot de passe trop court');
            return;
        }

        // Mock successful login
        localStorage.setItem('user', JSON.stringify({ email, role: 'Planner' }));
        router.push('/dashboard');
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md border-t-8 border-cat-yellow">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-cat-black mb-2">NEEMBA</h1>
                    <p className="text-sm text-gray-500 font-bold uppercase tracking-widest">Intervention Planner</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email Professionnel</label>
                        <input
                            type="email"
                            required
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-cat-yellow focus:border-cat-yellow outline-none transition text-gray-900"
                            placeholder="votre.nom@neemba.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
                        <input
                            type="password"
                            required
                            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-cat-yellow focus:border-cat-yellow outline-none transition text-gray-900"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>

                    {error && (
                        <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md border border-red-200">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="w-full bg-cat-black text-white font-bold py-3 px-4 rounded hover:bg-gray-800 transition duration-200 flex items-center justify-center gap-2"
                    >
                        SE CONNECTER
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14" /><path d="m12 5 7 7-7 7" /></svg>
                    </button>
                </form>

                <div className="mt-6 text-center text-xs text-gray-400">
                    &copy; {new Date().getFullYear()} Neemba - Caterpillar Dealer
                </div>
            </div>
        </div>
    );
}
