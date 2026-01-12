import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Form, Input, Button, Card, Space, Typography, message, Select } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { dashboardAPI } from '@/api/dashboards';
import type { DashboardCreate } from '@/types/dashboard';

const { Title, Text } = Typography;
const { TextArea } = Input;

export default function CreateDashboard() {
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const createMutation = useMutation({
    mutationFn: (data: DashboardCreate) => dashboardAPI.createDashboard(data),
    onSuccess: (dashboard) => {
      message.success('Dashboard created successfully');
      navigate(`/dashboards/${dashboard.id}/edit`);
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to create dashboard');
    },
  });

  const onFinish = (values: any) => {
    const dashboardData: DashboardCreate = {
      name: values.name,
      description: values.description,
      tags: values.tags || [],
      is_public: false,
      is_favorite: false,
      layout_config: {
        cols: 12,
        rowHeight: 100,
      },
      global_filters: [],
      widgets: [],
    };

    createMutation.mutate(dashboardData);
  };

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div>
          <Button
            type="link"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/dashboards')}
            style={{ paddingLeft: 0 }}
          >
            Back to Dashboards
          </Button>
          <Title level={2}>Create New Dashboard</Title>
          <Text type="secondary">
            Create a new dashboard to organize and visualize your data
          </Text>
        </div>

        <Card>
          <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            autoComplete="off"
          >
            <Form.Item
              label="Dashboard Name"
              name="name"
              rules={[
                { required: true, message: 'Please enter a dashboard name' },
                { max: 255, message: 'Name must be less than 255 characters' },
              ]}
            >
              <Input placeholder="e.g., Sales Performance Dashboard" />
            </Form.Item>

            <Form.Item
              label="Description"
              name="description"
            >
              <TextArea
                rows={4}
                placeholder="Describe what this dashboard shows and who it's for..."
              />
            </Form.Item>

            <Form.Item
              label="Tags"
              name="tags"
              help="Add tags to categorize this dashboard"
            >
              <Select
                mode="tags"
                placeholder="Add tags (press Enter to add)"
                style={{ width: '100%' }}
              />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  loading={createMutation.isPending}
                >
                  Create Dashboard
                </Button>
                <Button size="large" onClick={() => navigate('/dashboards')}>
                  Cancel
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      </Space>
    </div>
  );
}
