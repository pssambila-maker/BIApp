import { Drawer, List, Typography, Empty, Tag, Tooltip, Space } from 'antd';
import { ClockCircleOutlined, ThunderboltOutlined, DatabaseOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { queryHistoryAPI } from '@/api/semantic';
import { QueryHistory, FilterCondition } from '@/types/queryBuilder';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Text, Paragraph } = Typography;

interface Props {
  visible: boolean;
  onClose: () => void;
  onLoadQuery: (history: QueryHistory) => void;
  currentEntityId: string | null;
}

export default function QueryHistoryDrawer({ visible, onClose, onLoadQuery, currentEntityId }: Props) {
  const { data, isLoading } = useQuery({
    queryKey: ['query-history'],
    queryFn: () => queryHistoryAPI.list(50),
    enabled: visible,
  });

  const handleLoadQuery = (history: QueryHistory) => {
    onLoadQuery(history);
    onClose();
  };

  return (
    <Drawer
      title="Query History"
      placement="right"
      width={600}
      open={visible}
      onClose={onClose}
    >
      {data && data.history.length === 0 ? (
        <Empty
          description="No query history yet"
          style={{ marginTop: 60 }}
        />
      ) : (
        <List
          loading={isLoading}
          dataSource={data?.history || []}
          renderItem={(history) => (
            <List.Item
              style={{ cursor: 'pointer', padding: '16px 0' }}
              onClick={() => handleLoadQuery(history)}
            >
              <List.Item.Meta
                title={
                  <Space>
                    <Text strong>Query</Text>
                    {currentEntityId && history.entity_id !== currentEntityId && (
                      <Tag color="orange">Different entity</Tag>
                    )}
                  </Space>
                }
                description={
                  <Space direction="vertical" size={8} style={{ width: '100%' }}>
                    {/* Stats Row */}
                    <Space size={16} wrap>
                      <Tooltip title="Execution time">
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          <ThunderboltOutlined /> {history.execution_time_ms}ms
                        </Text>
                      </Tooltip>
                      <Tooltip title="Row count">
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          <DatabaseOutlined /> {history.row_count.toLocaleString()} rows
                        </Text>
                      </Tooltip>
                      <Tooltip title="Executed at">
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          <ClockCircleOutlined /> {dayjs(history.executed_at).fromNow()}
                        </Text>
                      </Tooltip>
                    </Space>

                    {/* Configuration Summary */}
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {history.query_config.dimension_ids.length} dimensions,{' '}
                      {history.query_config.measure_ids.length} measures
                      {history.query_config.filters.length > 0 &&
                        `, ${history.query_config.filters.length} filters`}
                    </Text>

                    {/* SQL Preview */}
                    <Paragraph
                      ellipsis={{ rows: 2, expandable: true, symbol: 'Show SQL' }}
                      style={{
                        marginBottom: 0,
                        fontSize: 11,
                        fontFamily: 'monospace',
                        background: '#f5f5f5',
                        padding: '4px 8px',
                        borderRadius: 4,
                      }}
                    >
                      {history.generated_sql}
                    </Paragraph>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      )}
    </Drawer>
  );
}
