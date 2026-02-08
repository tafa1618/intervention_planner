
'use client';

import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Machine } from '@/lib/mock-data';
import L from 'leaflet';

// Fix for default marker icon in Next.js/Webpack
const iconUrl = 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png';
const iconRetinaUrl = 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png';
const shadowUrl = 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
    iconUrl,
    iconRetinaUrl,
    shadowUrl,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

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
            {machines.map((machine) => (
                <Marker key={machine.id} position={[machine.location.lat, machine.location.lng]}>
                    <Popup>
                        <div className="p-2 min-w-[200px]">
                            <h3 className="font-bold text-lg text-cat-black">{machine.serialNumber}</h3>
                            <p className="text-sm font-semibold text-gray-600">{machine.model}</p>
                            <p className="text-sm text-gray-500 mb-2">{machine.client}</p>

                            <div className="border-t pt-2 mt-1">
                                <span className={`text-xs px-2 py-1 rounded-full font-bold ${machine.status === 'operational' ? 'bg-green-100 text-green-800' :
                                    machine.status === 'breakdown' ? 'bg-red-100 text-red-800' :
                                        'bg-orange-100 text-orange-800'
                                    }`}>
                                    {machine.status.toUpperCase()}
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
