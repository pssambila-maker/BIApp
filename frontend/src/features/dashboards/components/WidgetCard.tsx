import { useState } from 'react';
import { Card, Button, Space, Dropdown, Spin, Alert } from 'antd';
import { EditOutlined, DeleteOutlined, MoreOutlined, DragOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { DashboardWidget } from '@/types/dashboard';
import { dashboardAPI } from '@/api/dashboards';
import ChartVisualization from '@/features/query-builder/components/ChartVisualization';

interface WidgetCardProps {
  widget: DashboardWidget;
  dashboardId: string;
  onEdit?: (widget: DashboardWidget) => void;
  onDelete?: (widgetId: string) => void;
  readOnly?: boolean;
}

export default function WidgetCard({
  widget,
  dashboardId,
  onEdit,
  onDelete,
  readOnly = false,
}: WidgetCardProps) {
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch widget data
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['widget-data', dashboardId, widget.id],
    queryFn: () => dashboardAPI.getWidgetData(dashboardId, widget.id),
    enabled: !!dashboardId && !!widget.id,
    refetchInterval: autoRefresh && widget.refresh_interval ? widget.refresh_interval * 1000 : false,
  });

  const menuItems = [
    {
      key: 'edit',
      icon: <EditOutlined />,
      label: 'Edit Widget',
      onClick: () => onEdit?.(widget),
    },
    {
      key: 'refresh',
      label: autoRefresh ? 'Disable Auto-refresh' : 'Enable Auto-refresh',
      onClick: () => setAutoRefresh(!autoRefresh),
      disabled: !widget.refresh_interval,
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: 'Delete Widget',
      danger: true,
      onClick: () => onDelete?.(widget.id),
    },
  ];

  return (
    <Card
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
      bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '12px' }}
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {!readOnly && (
              <DragOutlined className="drag-handle" style={{ cursor: 'move', fontSize: 16 }} />
            )}
            <span>{widget.title}</span>
          </div>
          {!readOnly && (
            <Dropdown menu={{ items: menuItems }} trigger={['click']}>
              <Button type="text" icon={<MoreOutlined />} size="small" />
            </Dropdown>
          )}
        </div>
      }
      extra={
        !readOnly && widget.refresh_interval && (
          <span style={{ fontSize: 12, color: '#888' }}>
            Refreshes every {widget.refresh_interval}s
          </span>
        )
      }
    >
      {widget.description && (
        <div style={{ marginBottom: 8, fontSize: 12, color: '#666' }}>
          {widget.description}
        </div>
      )}

      <div style={{ flex: 1, overflow: 'auto' }}>
        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Spin size="large" />
          </div>
        )}

        {error && (
          <Alert
            message="Error loading widget data"
            description={(error as Error).message}
            type="error"
            showIcon
          />
        )}

        {data && !isLoading && (
          <ChartVisualization
            data={data.data}
            chartType={widget.chart_config.chart_type}
            config={widget.chart_config}
          />
        )}
      </div>
    </Card>
  );
}
