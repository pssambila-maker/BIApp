import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Button, Space, Typography, Empty, Spin, Card } from 'antd';
import { ArrowLeftOutlined, EditOutlined } from '@ant-design/icons';
import { Responsive as ResponsiveGridLayout } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { dashboardAPI } from '@/api/dashboards';
import WidgetCard from './components/WidgetCard';

const { Title, Text } = Typography;

export default function DashboardView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Fetch dashboard
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['dashboard', id],
    queryFn: () => dashboardAPI.getDashboard(id!),
    enabled: !!id,
  });

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

          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => navigate(`/dashboards/${dashboard.id}/edit`)}
          >
            Edit Dashboard
          </Button>
        </div>

        {/* Dashboard Content */}
        <Card style={{ minHeight: 600 }}>
          {dashboard.widgets.length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="This dashboard has no widgets yet"
            >
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => navigate(`/dashboards/${dashboard.id}/edit`)}
              >
                Add Widgets
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
            >
              {dashboard.widgets.map((widget) => (
                <div key={widget.id}>
                  <WidgetCard
                    widget={widget}
                    dashboardId={id!}
                    readOnly={true}
                  />
                </div>
              ))}
            </ResponsiveGridLayout>
          )}
        </Card>
      </Space>
    </div>
  );
}
