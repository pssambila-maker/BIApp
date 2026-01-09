import { Drawer, List, Button, Space, Typography, Empty, Tag, Popconfirm, message, Checkbox } from 'antd';
import { StarOutlined, StarFilled, DeleteOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { savedQueryAPI } from '@/api/semantic';
import { SavedQuery } from '@/types/queryBuilder';
import { useState } from 'react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Text } = Typography;

interface Props {
  visible: boolean;
  onClose: () => void;
  onLoadQuery: (query: SavedQuery) => void;
  currentEntityId: string | null;
}

export default function SavedQueriesDrawer({ visible, onClose, onLoadQuery, currentEntityId }: Props) {
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['saved-queries', favoritesOnly],
    queryFn: () => savedQueryAPI.list(favoritesOnly),
    enabled: visible,
  });

  const { mutate: toggleFavorite } = useMutation({
    mutationFn: ({ id, is_favorite }: { id: string; is_favorite: boolean }) =>
      savedQueryAPI.update(id, { is_favorite: !is_favorite }),
    onSuccess: () => {
      queryClient.invalidateQueries(['saved-queries']);
    },
  });

  const { mutate: deleteQuery } = useMutation({
    mutationFn: (id: string) => savedQueryAPI.delete(id),
    onSuccess: () => {
      message.success('Query deleted successfully');
      queryClient.invalidateQueries(['saved-queries']);
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to delete query');
    },
  });

  const handleLoadQuery = (query: SavedQuery) => {
    onLoadQuery(query);
    onClose();
  };

  return (
    <Drawer
      title="Saved Queries"
      placement="right"
      width={500}
      open={visible}
      onClose={onClose}
      extra={
        <Checkbox
          checked={favoritesOnly}
          onChange={(e) => setFavoritesOnly(e.target.checked)}
        >
          Favorites only
        </Checkbox>
      }
    >
      {data && data.queries.length === 0 ? (
        <Empty
          description={favoritesOnly ? 'No favorite queries' : 'No saved queries'}
          style={{ marginTop: 60 }}
        />
      ) : (
        <List
          loading={isLoading}
          dataSource={data?.queries || []}
          renderItem={(query) => (
            <List.Item
              key={query.id}
              actions={[
                <Button
                  type="text"
                  icon={query.is_favorite ? <StarFilled style={{ color: '#fadb14' }} /> : <StarOutlined />}
                  onClick={() => toggleFavorite({ id: query.id, is_favorite: query.is_favorite })}
                />,
                <Popconfirm
                  title="Delete query?"
                  description="This action cannot be undone."
                  onConfirm={() => deleteQuery(query.id)}
                  okText="Delete"
                  okType="danger"
                  cancelText="Cancel"
                >
                  <Button type="text" danger icon={<DeleteOutlined />} />
                </Popconfirm>,
              ]}
            >
              <List.Item.Meta
                title={
                  <Space>
                    <a onClick={() => handleLoadQuery(query)}>{query.name}</a>
                    {currentEntityId && query.entity_id !== currentEntityId && (
                      <Tag color="orange">Different entity</Tag>
                    )}
                  </Space>
                }
                description={
                  <Space direction="vertical" size={4} style={{ width: '100%' }}>
                    {query.description && <Text type="secondary">{query.description}</Text>}
                    <Space size={16}>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        <ClockCircleOutlined /> {dayjs(query.updated_at).fromNow()}
                      </Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {query.query_config.dimension_ids.length} dimensions,{' '}
                        {query.query_config.measure_ids.length} measures
                        {query.query_config.filters.length > 0 && `, ${query.query_config.filters.length} filters`}
                      </Text>
                    </Space>
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
