
import { Machine, MachineContext } from './types';

export interface ClientStats {
    name: string;
    count: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export async function fetchMachines(search?: string): Promise<Machine[]> {
    try {
        const url = search
            ? `${API_URL}/machines/?search=${encodeURIComponent(search)}`
            : `${API_URL}/machines/`;

        const res = await fetch(url);
        if (!res.ok) {
            throw new Error('Failed to fetch machines');
        }
        return res.json();
    } catch (error) {
        console.error('Error fetching machines:', error);
        return [];
    }
}

export async function searchGlobalContext(query: string): Promise<MachineContext[]> {
    try {
        const res = await fetch(`${API_URL}/machines/global-search?q=${encodeURIComponent(query)}`);
        if (!res.ok) {
            throw new Error('Failed to fetch global context');
        }
        return res.json();
    } catch (error) {
        console.error('Error fetching global context:', error);
        return [];
    }
}

export async function fetchClients(): Promise<ClientStats[]> {
    try {
        const res = await fetch(`${API_URL}/machines/clients`);
        if (!res.ok) {
            throw new Error('Failed to fetch clients');
        }
        return res.json();
    } catch (error) {
        console.error('Error fetching clients:', error);
        return [];
    }
}
