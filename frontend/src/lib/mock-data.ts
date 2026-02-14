
export interface Machine {
  id: string;
  serialNumber: string;
  model: string;
  client: string;
  location: {
    lat: number;
    lng: number;
    address: string;
  };
  status: 'operational' | 'breakdown' | 'maintenance';
  pendingInterventions: Intervention[];
}

export interface Intervention {
  id: string;
  type: 'SOS' | 'PSSR' | 'PI' | 'Repair' | 'Remote Service';
  programName?: string; // e.g. "CVA Level 2"
  dueDate: string;
  priority: 'high' | 'medium' | 'low';
  description: string;
}

// Coordinates around Dakar and Senegal regions
const DAKAR_CENTER = { lat: 14.7167, lng: -17.4677 };

export const MOCK_MACHINES: Machine[] = [
  // DAKAR REGION - CLUSTER 1 (Port Autonome)
  {
    id: 'm1',
    serialNumber: 'CAT-320-001',
    model: '320 GC',
    client: 'GCO (Grande Côte Opérations)',
    location: { lat: 14.6928, lng: -17.4467, address: 'Port Autonome, Dakar' },
    status: 'operational',
    pendingInterventions: [
      { id: 'i1', type: 'SOS', dueDate: '2023-11-15', priority: 'high', description: 'Surveillance huile moteur - Taux de fer élevé' },
      { id: 'i2', type: 'PSSR', dueDate: '2023-12-01', priority: 'medium', description: 'Inspection complète train de roulement' }
    ]
  },
  {
    id: 'm2',
    serialNumber: 'CAT-D8T-002',
    model: 'D8T',
    client: 'GCO (Grande Côte Opérations)', // Same client, same location -> INTRA-CLIENT optimization example
    location: { lat: 14.6930, lng: -17.4470, address: 'Port Autonome, Dakar' }, // Very close to m1
    status: 'maintenance',
    pendingInterventions: [
      { id: 'i3', type: 'PI', programName: 'Upgrade Hydraulic Valve', dueDate: '2023-10-20', priority: 'low', description: 'Mise à niveau obligatoire valve hydraulique (PI-12345)' }
    ]
  },
  
  // DAKAR REGION - CLUSTER 2 (Diamniadio / Industrial Zone)
  {
    id: 'm3',
    serialNumber: 'CAT-966L-003',
    model: '966L',
    client: 'Ciments du Sahel',
    location: { lat: 14.7400, lng: -17.1800, address: 'Rufisque / Diamniadio' },
    status: 'operational',
    pendingInterventions: [
      { id: 'i4', type: 'Remote Service', dueDate: '2023-11-10', priority: 'medium', description: 'Mise à jour firmware ECM à distance' }
    ]
  },
  {
    id: 'm4',
    serialNumber: 'CAT-140K-004',
    model: '140K',
    client: 'Eiffage Sénégal', // Different client nearby -> INTER-CLIENT optimization example
    location: { lat: 14.7450, lng: -17.1900, address: 'Chantier Autoroute A1' },
    status: 'breakdown',
    pendingInterventions: [
      { id: 'i5', type: 'Repair', dueDate: '2023-11-05', priority: 'high', description: 'Panne démarrage - Technicien requis urgence' }
    ]
  },

  // REMOTE REGION (Kédougou / Sabodala - Gold Mines)
  {
    id: 'm5',
    serialNumber: 'CAT-777E-005',
    model: '777E',
    client: 'Sabodala Gold Ops',
    location: { lat: 13.1700, lng: -12.1000, address: 'Mine de Sabodala' },
    status: 'operational',
    pendingInterventions: [
      { id: 'i6', type: 'PSSR', dueDate: '2023-11-20', priority: 'high', description: 'Inspection semestrielle' },
      { id: 'i7', type: 'SOS', dueDate: '2023-11-20', priority: 'medium', description: 'Prélèvement fluides transmission' }
    ]
  },
   {
    id: 'm6',
    serialNumber: 'CAT-777E-006',
    model: '777E',
    client: 'Sabodala Gold Ops',
    location: { lat: 13.1720, lng: -12.1020, address: 'Mine de Sabodala (Zone Nord)' },
    status: 'operational',
    pendingInterventions: []
  },
  
  // REGION THIES
    {
    id: 'm7',
    serialNumber: 'CAT-D6R-007',
    model: 'D6R',
    client: 'Dangote Cement',
    location: { lat: 14.8000, lng: -17.0000, address: 'Carrière Pout' },
    status: 'operational',
    pendingInterventions: [
        { id: 'i8', type: 'PI', dueDate: '2023-12-15', priority: 'low', description: 'Replacement joint étanchéité cabine' }
    ]
  }

];

export const MOCK_USERS = [
  { email: 'admin@neemba.com', password: 'password', name: 'Moussa Diop', role: 'Planner' },
  { email: 'tech@neemba.com', password: 'password', name: 'Fatou Ndiaye', role: 'Technician' }
];
