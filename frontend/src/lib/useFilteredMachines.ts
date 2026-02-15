import { useMemo } from 'react';
import { Machine } from './types';
import { useFilters } from '@/contexts/FilterContext';

export function useFilteredMachines(machines: Machine[]): Machine[] {
    const { filters } = useFilters();

    return useMemo(() => {
        return machines.filter(machine => {
            // Filter by status
            if (filters.status.length > 0) {
                const status = machine.status as 'operational' | 'maintenance' | 'critical';
                if (!filters.status.includes(status)) {
                    return false;
                }
            }

            // Filter by client
            if (filters.clients.length > 0 && !filters.clients.includes(machine.client)) {
                return false;
            }

            // Filter by region (extracted from client name for now)
            // TODO: Implement proper region extraction when column added to DB
            if (filters.regions.length > 0) {
                // Simple heuristic: check if client name contains region
                const hasRegion = filters.regions.some(region =>
                    machine.client.toLowerCase().includes(region.toLowerCase())
                );
                if (!hasRegion) return false;
            }

            return true;
        });
    }, [machines, filters]);
}
