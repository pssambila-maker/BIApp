import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Button,
  Card,
  Empty,
  Space,
  Table,
  Tag,
  Popconfirm,
  message,
  Typography,
  Input,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  StarOutlined,
  StarFilled,
  DashboardOutlined,
} from '@ant-design/icons';
import { dashboardAPI } from '@/api/dashboards';
import type { Dashboard } from '@/types/dashboard';

const { Title, Text } = Typography;
const { Search } = Input;

export default function DashboardList() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchText, setSearchText] = useState('');

  // Fetch dashboards
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboards'],
    queryFn: () => dashboardAPI.listDashboards(),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => dashboardAPI.deleteDashboard(id),
    onSuccess: () => {
      message.success('Dashboard deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to delete dashboard');
    },
  });

  // Toggle favorite mutation
  const toggleFavoriteMutation = useMutation({
    mutationFn: ({ id, isFavorite }: { id: string; isFavorite: boolean }) =>
      dashboardAPI.updateDashboard(id, { is_favorite: !isFavorite }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboards'] });
    },
  });

  const dashboards = dashboardData?.dashboards || [];
  const filteredDashboards = dashboards.filter((dashboard) =>
    dashboard.name.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Dashboard) => (
        <Space>
          <Button
            type="link"
            icon={record.is_favorite ? <StarFilled style={{ color: '#faad14' }} /> : <StarOutlined />}
            onClick={() => toggleFavoriteMutation.mutate({ id: record.id, isFavorite: record.is_favorite })}
          />
          <a onClick={() => navigate(`/dashboards/${record.id}`)}>{name}</a>
        </Space>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => <Text type="secondary">{text || '-'}</Text>,
    },
    {
      title: 'Widgets',
      dataIndex: 'widgets',
      key: 'widgets',
      render: (widgets: any[]) => <Tag>{widgets?.length || 0} widgets</Tag>,
    },
    {
      title: 'Tags',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags: string[]) => (
        <>
          {tags?.map((tag) => (
            <Tag key={tag}>{tag}</Tag>
          ))}
        </>
      ),
    },
    {
      title: 'Updated',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Dashboard) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`/dashboards/${record.id}/edit`)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete dashboard"
            description="Are you sure you want to delete this dashboard?"
            onConfirm={() => deleteMutation.mutate(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={2}>
              <DashboardOutlined /> Dashboards
            </Title>
            <Text type="secondary">
              Create and manage your interactive dashboards
            </Text>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            size="large"
            onClick={() => navigate('/dashboards/new')}
          >
            Create Dashboard
          </Button>
        </div>

        <Card>
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <Search
              placeholder="Search dashboards..."
              allowClear
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 300 }}
            />

            {filteredDashboards.length === 0 && !isLoading ? (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="No dashboards yet. Create your first dashboard to get started!"
              >
                <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/dashboards/new')}>
                  Create Dashboard
                </Button>
              </Empty>
            ) : (
              <Table
                columns={columns}
                dataSource={filteredDashboards}
                rowKey="id"
                loading={isLoading}
                pagination={{ pageSize: 10 }}
              />
            )}
          </Space>
        </Card>
      </Space>
    </div>
  );
}
