
export interface Intervention {
    id: number;
    type: string;
    priority: string;
    status: string;
    description?: string;
    date_created: string;
}

export interface Location {
    lat: number;
    lng: number;
    address?: string;
}

export interface Machine {
    id: number;
    serialNumber: string;
    model?: string;
    client: string;
    location: Location;
    status: string;
    pendingInterventions: Intervention[];
}

export interface ProgramStatus {
    visionLink: boolean;
    cvaf?: string;
    inspection?: string;
    remoteService?: string;
    suiviPs?: number;
}

export interface MachineContext {
    id: number;
    serialNumber: string;
    model?: string;
    client: string;
    location?: Location;
    status: string;
    programs: ProgramStatus;
}
