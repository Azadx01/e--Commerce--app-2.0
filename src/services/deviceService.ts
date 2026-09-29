import api from './apiClient';

// ─── Types ────────────────────────────────────────────────────────────────────
export interface DeviceRead {
    id: number;
    user_id: number;
    category: 'smartphone' | 'laptop';
    brand: string;
    model: string;
    condition: string | null;
    status: string | null;
    purchase_date: string | null;
    created_at: string;
    updated_at: string | null;
}

export interface DeviceCreate {
    category: 'smartphone' | 'laptop';
    brand: string;
    model: string;
    condition?: string;
    serial_number?: string;
    purchase_date?: string;
    status?: string;
}

export interface DeviceUpdate {
    condition?: string;
    status?: string;
}

// ─── Service ──────────────────────────────────────────────────────────────────
export const deviceService = {
    /**
     * GET /devices
     * Returns all devices belonging to the authenticated user.
     */
    list: async (): Promise<DeviceRead[]> => {
        const response = await api.get<DeviceRead[]>('/devices');
        return response.data;
    },

    /**
     * GET /devices/:id
     * Returns a single device by ID.
     */
    get: async (id: number): Promise<DeviceRead> => {
        const response = await api.get<DeviceRead>(`/devices/${id}`);
        return response.data;
    },

    /**
     * POST /devices
     * Creates a new device record.
     */
    create: async (payload: DeviceCreate): Promise<DeviceRead> => {
        const response = await api.post<DeviceRead>('/devices', payload);
        return response.data;
    },

    /**
     * PATCH /devices/:id
     * Updates mutable fields of an existing device.
     */
    update: async (id: number, payload: DeviceUpdate): Promise<DeviceRead> => {
        const response = await api.patch<DeviceRead>(`/devices/${id}`, payload);
        return response.data;
    },

    /**
     * DELETE /devices/:id
     * Permanently removes a device.
     */
    remove: async (id: number): Promise<DeviceRead> => {
        const response = await api.delete<DeviceRead>(`/devices/${id}`);
        return response.data;
    },
};
