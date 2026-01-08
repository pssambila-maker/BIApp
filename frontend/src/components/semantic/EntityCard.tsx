import { Card, Tag, Descriptions, Badge } from 'antd';
import { DatabaseOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { SemanticEntity } from '@/types/semantic';

interface Props {
  entity: SemanticEntity;
  onClick: () => void;
}

export default function EntityCard({ entity, onClick }: Props) {
  return (
    <Card
      hoverable
      onClick={onClick}
      title={
        <span>
          <DatabaseOutlined style={{ marginRight: 8 }} />
          {entity.name}
          {entity.is_certified && (
            <CheckCircleOutlined style={{ color: '#52c41a', marginLeft: 8 }} />
          )}
        </span>
      }
      extra={entity.plural_name}
    >
      <Descriptions column={1} size="small">
        <Descriptions.Item label="Primary Table">{entity.primary_table}</Descriptions.Item>
        <Descriptions.Item label="Dimensions">
          <Badge count={entity.dimensions.length} style={{ backgroundColor: '#1890ff' }} />
        </Descriptions.Item>
        <Descriptions.Item label="Measures">
          <Badge count={entity.measures.length} style={{ backgroundColor: '#52c41a' }} />
        </Descriptions.Item>
      </Descriptions>
      <div style={{ marginTop: 12 }}>
        {entity.tags.map((tag) => (
          <Tag key={tag} color="blue">{tag}</Tag>
        ))}
      </div>
      {entity.description && (
        <p style={{ marginTop: 12, color: '#666' }}>{entity.description}</p>
      )}
    </Card>
  );
}
