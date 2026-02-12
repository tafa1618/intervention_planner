
'use client'

import dynamic from 'next/dynamic'
import { Machine } from '@/lib/types'

const LeafletMap = dynamic(
    () => import('./LeafletMap'),
    {
        ssr: false,
        loading: () => <div className="h-full w-full bg-gray-100 animate-pulse rounded-lg flex items-center justify-center text-gray-500 font-medium">Chargement de la Carte...</div>
    }
)

interface MapProps {
    machines: Machine[];
    center?: [number, number];
    zoom?: number;
}

export default function Map({ machines, center, zoom }: MapProps) {
    return <LeafletMap machines={machines} center={center} zoom={zoom} />
}
