/**
 * Dashboard API client
 */

import apiClient from './client';
import {
  Dashboard,
  DashboardCreate,
  DashboardUpdate,
  DashboardListResponse,
  DashboardWidget,
  DashboardWidgetCreate,
  DashboardWidgetUpdate,
  WidgetDataResponse,
} from '@/types/dashboard';

export const dashboardAPI = {
  // Dashboard CRUD
  async listDashboards(skip = 0, limit = 50, favoriteOnly = false): Promise<DashboardListResponse> {
    const response = await apiClient.get('/dashboards', {
      params: { skip, limit, favorite_only: favoriteOnly },
    });
    return response.data;
  },

  async getDashboard(id: string): Promise<Dashboard> {
    const response = await apiClient.get(`/dashboards/${id}`);
    return response.data;
  },

  async createDashboard(data: DashboardCreate): Promise<Dashboard> {
    const response = await apiClient.post('/dashboards', data);
    return response.data;
  },

  async updateDashboard(id: string, data: DashboardUpdate): Promise<Dashboard> {
    const response = await apiClient.put(`/dashboards/${id}`, data);
    return response.data;
  },

  async deleteDashboard(id: string): Promise<void> {
    await apiClient.delete(`/dashboards/${id}`);
  },

  // Widget CRUD
  async addWidget(dashboardId: string, widget: DashboardWidgetCreate): Promise<DashboardWidget> {
    const response = await apiClient.post(`/dashboards/${dashboardId}/widgets`, widget);
    return response.data;
  },

  async updateWidget(
    dashboardId: string,
    widgetId: string,
    data: DashboardWidgetUpdate
  ): Promise<DashboardWidget> {
    const response = await apiClient.put(`/dashboards/${dashboardId}/widgets/${widgetId}`, data);
    return response.data;
  },

  async deleteWidget(dashboardId: string, widgetId: string): Promise<void> {
    await apiClient.delete(`/dashboards/${dashboardId}/widgets/${widgetId}`);
  },

  // Widget Data
  async getWidgetData(dashboardId: string, widgetId: string): Promise<WidgetDataResponse> {
    const response = await apiClient.post(`/dashboards/${dashboardId}/widgets/${widgetId}/data`);
    return response.data;
  },
};
