import { useState, useEffect } from 'react';
import { Button, Select, Space, Alert, Collapse, Typography, Table, Empty, message, Dropdown, Segmented } from 'antd';
import { PlayCircleOutlined, ClearOutlined, SaveOutlined, FolderOpenOutlined, DownloadOutlined, HistoryOutlined, TableOutlined, BarChartOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useSemanticCatalog } from '@/features/semantic-catalog/hooks/useSemanticCatalog';
import { useExecuteQuery } from './hooks/useQueryBuilder';
import { QueryRequest, SavedQuery, FilterCondition, QueryHistory } from '@/types/queryBuilder';
import { ChartConfiguration } from '@/types/visualization';
import FilterBuilder, { FilterRow } from './components/FilterBuilder';
import SaveQueryModal from './components/SaveQueryModal';
import SavedQueriesDrawer from './components/SavedQueriesDrawer';
import QueryHistoryDrawer from './components/QueryHistoryDrawer';
import ChartVisualization from './components/ChartVisualization';
import { semanticAPI } from '@/api/semantic';
import { inferChartConfig } from './utils/chartUtils';

export default function QueryBuilder() {
  // State
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [selectedDimensionIds, setSelectedDimensionIds] = useState<string[]>([]);
  const [selectedMeasureIds, setSelectedMeasureIds] = useState<string[]>([]);
  const [filters, setFilters] = useState<FilterRow[]>([]);
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [savedQueriesVisible, setSavedQueriesVisible] = useState(false);
  const [historyVisible, setHistoryVisible] = useState(false);
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('table');
  const [chartConfig, setChartConfig] = useState<ChartConfiguration | null>(null);

  // Data fetching
  const { data: catalog, isLoading: catalogLoading } = useSemanticCatalog();
  const { mutate: executeQuery, data: results, isLoading: queryLoading, error } = useExecuteQuery();

  // Get selected entity
  const selectedEntity = catalog?.entities.find(e => e.id === selectedEntityId);

  // Auto-initialize chart config when results arrive
  useEffect(() => {
    if (results) {
      // Always reinitialize chart config when new results arrive
      // This ensures column names match the current query results
      setChartConfig(inferChartConfig(results));
    }
  }, [results]);

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
      filters: filters.map(f => ({
        dimension_id: f.dimension_id,
        operator: f.operator,
        value: f.value,
      })),
      limit: 1000,
    };

    executeQuery(request);
  };

  const handleClear = () => {
    setSelectedEntityId(null);
    setSelectedDimensionIds([]);
    setSelectedMeasureIds([]);
    setFilters([]);
    setChartConfig(null);
    setViewMode('table');
  };

  const handleSaveQuery = () => {
    if (!selectedEntityId || selectedMeasureIds.length === 0) {
      message.warning('Please configure a query before saving');
      return;
    }
    setSaveModalVisible(true);
  };

  const handleLoadQuery = (savedQuery: SavedQuery) => {
    setSelectedEntityId(savedQuery.entity_id);
    setSelectedDimensionIds(savedQuery.query_config.dimension_ids);
    setSelectedMeasureIds(savedQuery.query_config.measure_ids);

    // Convert filters to FilterRow format
    const loadedFilters: FilterRow[] = savedQuery.query_config.filters.map((f: FilterCondition, index: number) => ({
      id: `filter_${Date.now()}_${index}`,
      dimension_id: f.dimension_id,
      operator: f.operator,
      value: f.value,
    }));
    setFilters(loadedFilters);

    message.success(`Loaded query: ${savedQuery.name}`);
  };

  const handleLoadHistory = (history: QueryHistory) => {
    setSelectedEntityId(history.entity_id);
    setSelectedDimensionIds(history.query_config.dimension_ids);
    setSelectedMeasureIds(history.query_config.measure_ids);

    // Convert filters to FilterRow format
    const loadedFilters: FilterRow[] = history.query_config.filters.map((f: FilterCondition, index: number) => ({
      id: `filter_${Date.now()}_${index}`,
      dimension_id: f.dimension_id,
      operator: f.operator,
      value: f.value,
    }));
    setFilters(loadedFilters);

    message.success('Loaded query from history');
  };

  const handleExport = async (format: 'csv' | 'xlsx' | 'json') => {
    if (!selectedEntityId || selectedMeasureIds.length === 0) {
      message.warning('Please configure a query before exporting');
      return;
    }

    try {
      const request: QueryRequest = {
        entity_id: selectedEntityId,
        dimension_ids: selectedDimensionIds,
        measure_ids: selectedMeasureIds,
        filters: filters.map(f => ({
          dimension_id: f.dimension_id,
          operator: f.operator,
          value: f.value,
        })),
        limit: 1000,
      };

      await semanticAPI.exportQuery(request, format);
      message.success(`Exported as ${format.toUpperCase()}`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Export failed');
    }
  };

  const exportMenuItems: MenuProps['items'] = [
    {
      key: 'csv',
      label: 'Download as CSV',
      onClick: () => handleExport('csv'),
    },
    {
      key: 'xlsx',
      label: 'Download as Excel',
      onClick: () => handleExport('xlsx'),
    },
    {
      key: 'json',
      label: 'Download as JSON',
      onClick: () => handleExport('json'),
    },
  ];

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

        {/* Filter Builder */}
        {selectedEntity && (
          <FilterBuilder
            dimensions={selectedEntity.dimensions}
            filters={filters}
            onChange={setFilters}
          />
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
          <Button
            icon={<SaveOutlined />}
            onClick={handleSaveQuery}
            disabled={!selectedEntityId || selectedMeasureIds.length === 0}
          >
            Save Query
          </Button>
          <Button icon={<FolderOpenOutlined />} onClick={() => setSavedQueriesVisible(true)}>
            Load Query
          </Button>
          <Button icon={<HistoryOutlined />} onClick={() => setHistoryVisible(true)}>
            History
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
              <Space style={{ width: '100%', justifyContent: 'space-between', marginBottom: 16 }}>
                <h2 style={{ margin: 0 }}>Results ({results.row_count} rows)</h2>
                <Space>
                  <Segmented
                    options={[
                      { label: 'Table', value: 'table', icon: <TableOutlined /> },
                      { label: 'Chart', value: 'chart', icon: <BarChartOutlined /> },
                    ]}
                    value={viewMode}
                    onChange={(value) => setViewMode(value as 'table' | 'chart')}
                  />
                  <Dropdown menu={{ items: exportMenuItems }} placement="bottomRight">
                    <Button icon={<DownloadOutlined />}>Export</Button>
                  </Dropdown>
                </Space>
              </Space>

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

            {/* Conditional Rendering: Table or Chart */}
            {viewMode === 'table' ? (
              results.row_count > 0 ? (
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
              )
            ) : (
              chartConfig && (
                <ChartVisualization
                  data={results}
                  config={chartConfig}
                  onConfigChange={setChartConfig}
                />
              )
            )}
          </>
        )}
      </Space>

      {/* Save Query Modal */}
      <SaveQueryModal
        visible={saveModalVisible}
        onClose={() => setSaveModalVisible(false)}
        queryConfig={{
          entity_id: selectedEntityId || '',
          dimension_ids: selectedDimensionIds,
          measure_ids: selectedMeasureIds,
          filters: filters.map(f => ({
            dimension_id: f.dimension_id,
            operator: f.operator,
            value: f.value,
          })),
          limit: 1000,
        }}
      />

      {/* Saved Queries Drawer */}
      <SavedQueriesDrawer
        visible={savedQueriesVisible}
        onClose={() => setSavedQueriesVisible(false)}
        onLoadQuery={handleLoadQuery}
        currentEntityId={selectedEntityId}
      />

      {/* Query History Drawer */}
      <QueryHistoryDrawer
        visible={historyVisible}
        onClose={() => setHistoryVisible(false)}
        onLoadQuery={handleLoadHistory}
        currentEntityId={selectedEntityId}
      />
    </div>
  );
}
