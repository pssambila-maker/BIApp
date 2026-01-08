import { useState } from 'react';
import { Row, Col, Spin, Alert, Statistic, Modal, Tabs } from 'antd';
import { DatabaseOutlined, TagOutlined, BarChartOutlined } from '@ant-design/icons';
import { useSemanticCatalog } from './hooks/useSemanticCatalog';
import EntityCard from '@/components/semantic/EntityCard';
import DimensionList from '@/components/semantic/DimensionList';
import MeasureList from '@/components/semantic/MeasureList';
import { SemanticEntity } from '@/types/semantic';

export default function SemanticCatalog() {
  const { data, isLoading, error } = useSemanticCatalog();
  const [selectedEntity, setSelectedEntity] = useState<SemanticEntity | null>(null);

  if (isLoading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (error) return <Alert type="error" message="Failed to load semantic catalog" />;
  if (!data) return null;

  return (
    <div>
      <h1>Semantic Catalog</h1>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Statistic
            title="Total Entities"
            value={data.total_entities}
            prefix={<DatabaseOutlined />}
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="Total Dimensions"
            value={data.total_dimensions}
            prefix={<TagOutlined />}
          />
        </Col>
        <Col span={8}>
          <Statistic
            title="Total Measures"
            value={data.total_measures}
            prefix={<BarChartOutlined />}
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {data.entities.map((entity) => (
          <Col key={entity.id} xs={24} sm={12} lg={8}>
            <EntityCard entity={entity} onClick={() => setSelectedEntity(entity)} />
          </Col>
        ))}
      </Row>

      <Modal
        title={selectedEntity?.name}
        open={!!selectedEntity}
        onCancel={() => setSelectedEntity(null)}
        footer={null}
        width={1000}
      >
        {selectedEntity && (
          <Tabs
            items={[
              {
                key: 'dimensions',
                label: `Dimensions (${selectedEntity.dimensions.length})`,
                children: <DimensionList dimensions={selectedEntity.dimensions} />,
              },
              {
                key: 'measures',
                label: `Measures (${selectedEntity.measures.length})`,
                children: <MeasureList measures={selectedEntity.measures} />,
              },
            ]}
          />
        )}
      </Modal>
    </div>
  );
}
