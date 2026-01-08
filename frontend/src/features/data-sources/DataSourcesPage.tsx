import { useState } from 'react';
import { Button, Table, Tag, Space, Tooltip, Modal, message } from 'antd';
import {
  PlusOutlined,
  DatabaseOutlined,
  FileOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  SyncOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { ColumnsType } from 'antd/es/table';
import { dataSourceAPI } from '@/api/dataSources';
import { DataSource, DataSourceType } from '@/types/dataSource';
import AddDataSourceModal from './components/AddDataSourceModal';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { confirm } = Modal;

export default function DataSourcesPage() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: dataSources, isLoading } = useQuery({
    queryKey: ['data-sources'],
    queryFn: () => dataSourceAPI.getAll(),
  });

  const deleteMutation = useMutation({
    mutationFn: dataSourceAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['data-sources'] });
      message.success('Data source deleted successfully');
    },
    onError: () => {
      message.error('Failed to delete data source');
    },
  });

  const syncMutation = useMutation({
    mutationFn: dataSourceAPI.sync,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['data-sources'] });
      message.success(`Synced successfully! Found ${data.tables_found} tables`);
    },
    onError: () => {
      message.error('Failed to sync data source');
    },
  });

  const testMutation = useMutation({
    mutationFn: dataSourceAPI.testConnection,
    onSuccess: (data) => {
      if (data.status === 'success') {
        message.success(data.message);
      } else {
        message.error(data.message);
      }
    },
    onError: () => {
      message.error('Failed to test connection');
    },
  });

  const handleDelete = (id: string, name: string) => {
    confirm({
      title: 'Delete Data Source',
      icon: <ExclamationCircleOutlined />,
      content: `Are you sure you want to delete "${name}"? This action cannot be undone.`,
      okText: 'Delete',
      okType: 'danger',
      onOk: () => deleteMutation.mutate(id),
    });
  };

  const getSourceTypeIcon = (type: DataSourceType) => {
    const fileTypes: DataSourceType[] = ['csv', 'excel'];
    return fileTypes.includes(type) ? <FileOutlined /> : <DatabaseOutlined />;
  };

  const getSourceTypeColor = (type: DataSourceType) => {
    const colors: Record<DataSourceType, string> = {
      postgresql: 'blue',
      mysql: 'orange',
      csv: 'green',
      excel: 'cyan',
    };
    return colors[type] || 'default';
  };

  const columns: ColumnsType<DataSource> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          {getSourceTypeIcon(record.type)}
          <strong>{text}</strong>
          {record.is_certified && <CheckCircleOutlined style={{ color: '#52c41a' }} />}
        </Space>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: DataSourceType) => (
        <Tag color={getSourceTypeColor(type)}>{type.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => dayjs(date).format('MMM D, YYYY'),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="Test Connection">
            <Button
              size="small"
              icon={<CheckCircleOutlined />}
              onClick={() => testMutation.mutate(record.id)}
              loading={testMutation.isPending}
            />
          </Tooltip>
          <Tooltip title="Sync Tables">
            <Button
              size="small"
              icon={<SyncOutlined />}
              onClick={() => syncMutation.mutate(record.id)}
              loading={syncMutation.isPending}
            />
          </Tooltip>
          <Tooltip title="Delete">
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(record.id, record.name)}
              loading={deleteMutation.isPending}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>Data Sources</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setIsAddModalOpen(true)}
        >
          Add Data Source
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={dataSources}
        rowKey="id"
        loading={isLoading}
        pagination={{ pageSize: 10 }}
      />

      <AddDataSourceModal
        open={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
      />
    </div>
  );
}
