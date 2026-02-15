
'use client';

import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Machine } from '@/lib/types';
import L from 'leaflet';
import MapController from './MapController';

const createIcon = (color: string) => L.divIcon({
    className: 'custom-icon',
    html: `<div style="background-color: ${color}; width: 15px; height: 15px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.5);"></div>`,
    iconSize: [15, 15],
    iconAnchor: [7, 7],
    popupAnchor: [0, -10]
});

const GreenIcon = createIcon('#22c55e');
const OrangeIcon = createIcon('#f97316');
const RedIcon = createIcon('#ef4444');


interface MapProps {
    machines: Machine[];
    center?: [number, number];
    zoom?: number;
}

const LeafletMap = ({ machines, center = [14.4974, -14.4524], zoom = 7 }: MapProps) => {
    return (
        <MapContainer center={center} zoom={zoom} scrollWheelZoom={true} className="h-full w-full rounded-lg shadow-lg z-0">
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapController center={center} zoom={zoom} />
            {machines.map((machine) => (
                <Marker
                    key={machine.id}
                    position={[machine.location.lat, machine.location.lng]}
                    icon={
                        machine.status === 'operational' ? GreenIcon :
                            machine.status === 'critical' ? RedIcon :
                                OrangeIcon
                    }
                >
                    <Popup>
                        <div className="p-2 min-w-[200px]">
                            <h3 className="font-bold text-lg text-cat-black">{machine.serialNumber}</h3>
                            <p className="text-sm font-semibold text-gray-600">{machine.model}</p>
                            <p className="text-sm text-gray-500 mb-2">{machine.client}</p>

                            <div className="border-t pt-2 mt-1">
                                <span className={`text-xs px-2 py-1 rounded-full font-bold ${machine.status === 'operational' ? 'bg-green-100 text-green-800' :
                                    machine.status === 'critical' ? 'bg-red-100 text-red-800' :
                                        'bg-orange-100 text-orange-800'
                                    }`}>
                                    {machine.status === 'critical' ? 'PRIORITAIRE' : machine.status === 'operational' ? 'OPERATIONNEL' : 'MAINTENANCE PREVUE'}
                                </span>
                            </div>

                            {machine.pendingInterventions.length > 0 && (
                                <div className="mt-3">
                                    <h4 className="text-xs font-bold uppercase text-gray-400 mb-1">Interventions</h4>
                                    <ul className="space-y-1">
                                        {machine.pendingInterventions.map(i => (
                                            <li key={i.id} className="text-xs bg-yellow-50 p-1 rounded border border-yellow-200 text-cat-black">
                                                <span className="font-bold">{i.type}</span>: {i.description}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
};

export default LeafletMap;
