import { useState } from 'react';
import { Button, Select, Space, Alert, Collapse, Typography, Table, Empty, message } from 'antd';
import { PlayCircleOutlined, ClearOutlined } from '@ant-design/icons';
import { useSemanticCatalog } from '@/features/semantic-catalog/hooks/useSemanticCatalog';
import { useExecuteQuery } from './hooks/useQueryBuilder';
import { QueryRequest } from '@/types/queryBuilder';

export default function QueryBuilder() {
  // State
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [selectedDimensionIds, setSelectedDimensionIds] = useState<string[]>([]);
  const [selectedMeasureIds, setSelectedMeasureIds] = useState<string[]>([]);

  // Data fetching
  const { data: catalog, isLoading: catalogLoading } = useSemanticCatalog();
  const { mutate: executeQuery, data: results, isLoading: queryLoading, error } = useExecuteQuery();

  // Get selected entity
  const selectedEntity = catalog?.entities.find(e => e.id === selectedEntityId);

  // Handlers
  const handleExecute = () => {
    if (!selectedEntityId || selectedMeasureIds.length === 0) {
      message.warning('Please select an entity and at least one measure');
      return;
    }

    const request: QueryRequest = {
      entity_id: selectedEntityId,
      dimension_ids: selectedDimensionIds,
      measure_ids: selectedMeasureIds,
      filters: [],
      limit: 1000,
    };

    executeQuery(request);
  };

  const handleClear = () => {
    setSelectedEntityId(null);
    setSelectedDimensionIds([]);
    setSelectedMeasureIds([]);
  };

  // Render
  return (
    <div>
      <h1>Query Builder</h1>

      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* Entity Selector */}
        <div>
          <label style={{ fontWeight: 'bold', marginBottom: 8, display: 'block' }}>
            Select Entity:
          </label>
          <Select
            style={{ width: '100%' }}
            placeholder="Choose a semantic entity"
            value={selectedEntityId}
            onChange={setSelectedEntityId}
            loading={catalogLoading}
            options={catalog?.entities.map(e => ({
              value: e.id,
              label: e.name,
              description: e.description,
            }))}
          />
        </div>

        {/* Dimension Selector */}
        {selectedEntity && (
          <div>
            <label style={{ fontWeight: 'bold', marginBottom: 8, display: 'block' }}>
              Dimensions (GROUP BY):
            </label>
            <Select
              mode="multiple"
              style={{ width: '100%' }}
              placeholder="Select dimensions for grouping"
              value={selectedDimensionIds}
              onChange={setSelectedDimensionIds}
              options={selectedEntity.dimensions.map(d => ({
                value: d.id,
                label: d.name,
                description: d.description || d.sql_column,
              }))}
            />
          </div>
        )}

        {/* Measure Selector */}
        {selectedEntity && (
          <div>
            <label style={{ fontWeight: 'bold', marginBottom: 8, display: 'block' }}>
              Measures (Aggregations):
            </label>
            <Select
              mode="multiple"
              style={{ width: '100%' }}
              placeholder="Select measures to calculate"
              value={selectedMeasureIds}
              onChange={setSelectedMeasureIds}
              options={selectedEntity.measures.map(m => ({
                value: m.id,
                label: `${m.name} (${m.aggregation_function})`,
                description: m.description,
              }))}
            />
          </div>
        )}

        {/* Action Buttons */}
        <Space>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleExecute}
            loading={queryLoading}
            disabled={!selectedEntityId || selectedMeasureIds.length === 0}
          >
            Execute Query
          </Button>
          <Button icon={<ClearOutlined />} onClick={handleClear}>
            Clear
          </Button>
        </Space>

        {/* Error Display */}
        {error && (
          <Alert
            type="error"
            message="Query Failed"
            description={(error as any).response?.data?.detail || 'An error occurred'}
            closable
          />
        )}

        {/* Results */}
        {results && (
          <>
            <div>
              <h2>Results ({results.row_count} rows)</h2>

              {/* SQL Preview */}
              <Collapse
                items={[
                  {
                    key: 'sql',
                    label: 'View Generated SQL',
                    children: (
                      <Typography.Paragraph>
                        <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
                          {results.generated_sql}
                        </pre>
                      </Typography.Paragraph>
                    ),
                  },
                ]}
              />
            </div>

            {/* Results Table */}
            {results.row_count > 0 ? (
              <Table
                dataSource={results.data}
                columns={results.columns.map(col => ({
                  title: col,
                  dataIndex: col,
                  key: col,
                }))}
                pagination={{ pageSize: 20 }}
                scroll={{ x: true }}
                rowKey={(record, index) => index?.toString() || '0'}
              />
            ) : (
              <Empty description="No results found" />
            )}
          </>
        )}
      </Space>
    </div>
  );
}
