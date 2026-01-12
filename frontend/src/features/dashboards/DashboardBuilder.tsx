import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, Space, Typography, message, Card, Empty, Spin, Modal } from 'antd';
import {
  ArrowLeftOutlined,
  PlusOutlined,
  SaveOutlined,
  EyeOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { Responsive as ResponsiveGridLayout } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { dashboardAPI } from '@/api/dashboards';
import type { DashboardWidget, DashboardWidgetCreate } from '@/types/dashboard';
import WidgetCard from './components/WidgetCard';
import AddWidgetModal from './components/AddWidgetModal';

const { Title, Text } = Typography;

export default function DashboardBuilder() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [hasChanges, setHasChanges] = useState(false);
  const [isAddWidgetModalOpen, setIsAddWidgetModalOpen] = useState(false);

  // Fetch dashboard
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['dashboard', id],
    queryFn: () => dashboardAPI.getDashboard(id!),
    enabled: !!id,
  });

  // Update dashboard mutation
  const updateMutation = useMutation({
    mutationFn: ({ dashboardId, data }: { dashboardId: string; data: any }) =>
      dashboardAPI.updateDashboard(dashboardId, data),
    onSuccess: () => {
      message.success('Dashboard saved');
      setHasChanges(false);
      queryClient.invalidateQueries({ queryKey: ['dashboard', id] });
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to save dashboard');
    },
  });

  // Add widget mutation
  const addWidgetMutation = useMutation({
    mutationFn: (widget: DashboardWidgetCreate) =>
      dashboardAPI.addWidget(id!, widget),
    onSuccess: () => {
      message.success('Widget added successfully');
      queryClient.invalidateQueries({ queryKey: ['dashboard', id] });
      setIsAddWidgetModalOpen(false);
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to add widget');
    },
  });

  // Delete widget mutation
  const deleteWidgetMutation = useMutation({
    mutationFn: (widgetId: string) =>
      dashboardAPI.deleteWidget(id!, widgetId),
    onSuccess: () => {
      message.success('Widget deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['dashboard', id] });
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to delete widget');
    },
  });

  const handleLayoutChange = () => {
    setHasChanges(true);
  };

  const handleSave = () => {
    if (!dashboard) return;

    updateMutation.mutate({
      dashboardId: dashboard.id,
      data: {
        layout_config: dashboard.layout_config,
      },
    });
  };

  const handleAddWidget = () => {
    setIsAddWidgetModalOpen(true);
  };

  const handleAddWidgetSubmit = (widget: DashboardWidgetCreate) => {
    addWidgetMutation.mutate(widget);
  };

  const handleEditWidget = (_widget: DashboardWidget) => {
    // For now, just show a message - full edit functionality can be added later
    message.info('Widget editing coming soon!');
  };

  const handleDeleteWidget = (widgetId: string) => {
    Modal.confirm({
      title: 'Delete Widget',
      icon: <ExclamationCircleOutlined />,
      content: 'Are you sure you want to delete this widget?',
      okText: 'Delete',
      okType: 'danger',
      onOk: () => deleteWidgetMutation.mutate(widgetId),
    });
  };

  if (isLoading) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div style={{ padding: 24 }}>
        <Empty description="Dashboard not found" />
      </div>
    );
  }

  // Prepare layout items for react-grid-layout
  const layouts = {
    lg: dashboard.widgets.map((widget) => ({
      i: widget.id,
      x: widget.grid_position.x,
      y: widget.grid_position.y,
      w: widget.grid_position.w,
      h: widget.grid_position.h,
    })),
  };

  return (
    <div style={{ padding: 24 }}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Button
              type="link"
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/dashboards')}
              style={{ paddingLeft: 0 }}
            >
              Back to Dashboards
            </Button>
            <Title level={2}>{dashboard.name}</Title>
            {dashboard.description && <Text type="secondary">{dashboard.description}</Text>}
          </div>

          <Space>
            <Button
              type="default"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/dashboards/${dashboard.id}`)}
            >
              View Mode
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAddWidget}
            >
              Add Widget
            </Button>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={updateMutation.isPending}
              disabled={!hasChanges}
            >
              Save Changes
            </Button>
          </Space>
        </div>

        {/* Dashboard Grid */}
        <Card style={{ minHeight: 600 }}>
          {dashboard.widgets.length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="No widgets yet. Add your first widget to get started!"
            >
              <Button type="primary" icon={<PlusOutlined />} onClick={handleAddWidget}>
                Add Widget
              </Button>
            </Empty>
          ) : (
            <ResponsiveGridLayout
              className="layout"
              layouts={layouts}
              breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
              cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
              rowHeight={dashboard.layout_config?.rowHeight || 100}
              width={1200}
              onLayoutChange={handleLayoutChange}
            >
              {dashboard.widgets.map((widget) => (
                <div key={widget.id}>
                  <WidgetCard
                    widget={widget}
                    dashboardId={id!}
                    onEdit={handleEditWidget}
                    onDelete={handleDeleteWidget}
                  />
                </div>
              ))}
            </ResponsiveGridLayout>
          )}
        </Card>
      </Space>

      {/* Add Widget Modal */}
      <AddWidgetModal
        open={isAddWidgetModalOpen}
        onCancel={() => setIsAddWidgetModalOpen(false)}
        onOk={handleAddWidgetSubmit}
        existingWidgets={dashboard.widgets}
      />
    </div>
  );
}
