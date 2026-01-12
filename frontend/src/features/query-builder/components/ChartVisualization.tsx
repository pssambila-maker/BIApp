import { useMemo, useState, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, Space, Alert, Empty, Divider } from 'antd';
import { QueryResponse } from '@/types/queryBuilder';
import { ChartConfiguration, ChartType } from '@/types/visualization';
import { transformDataForECharts, validateChartConfig } from '../utils/chartUtils';
import ChartTypeSelector from './ChartTypeSelector';
import AxisConfigPanel from './AxisConfigPanel';
import SortConfigPanel from './SortConfigPanel';
import ColorConfigPanel from './ColorConfigPanel';

interface Props {
  data: QueryResponse;
  config: ChartConfiguration;
  onConfigChange: (config: ChartConfiguration) => void;
}

export default function ChartVisualization({ data, config, onConfigChange }: Props) {
  const [chartType, setChartType] = useState<ChartType>(config.chart_type);

  // Update chart type in config when changed
  useEffect(() => {
    if (chartType !== config.chart_type) {
      // When switching to/from pie chart, reset axis configurations
      if (chartType === 'pie') {
        onConfigChange({
          ...config,
          chart_type: chartType,
          category_column: config.x_axis_column,
          value_column: config.y_axis_columns[0] || null,
        });
      } else if (config.chart_type === 'pie') {
        onConfigChange({
          ...config,
          chart_type: chartType,
          x_axis_column: config.category_column,
          y_axis_columns: config.value_column ? [config.value_column] : [],
        });
      } else {
        onConfigChange({ ...config, chart_type: chartType });
      }
    }
  }, [chartType]);

  // Validate configuration
  const validationError = useMemo(() => {
    return validateChartConfig(config, data.columns);
  }, [config, data.columns]);

  // Generate ECharts option
  const chartOption = useMemo(() => {
    if (validationError) return null;
    return transformDataForECharts(data, config, chartType);
  }, [data, config, chartType, validationError]);

  if (data.row_count === 0) {
    return <Empty description="No data to visualize" style={{ marginTop: 60 }} />;
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* Chart Type Selector */}
      <Card size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <div style={{ fontWeight: 'bold', marginBottom: 8 }}>Chart Type:</div>
          <ChartTypeSelector value={chartType} onChange={setChartType} />
        </Space>
      </Card>

      {/* Axis Configuration */}
      <Card size="small">
        <div style={{ fontWeight: 'bold', marginBottom: 12 }}>Chart Configuration:</div>
        <AxisConfigPanel
          columns={data.columns}
          config={config}
          onChange={onConfigChange}
        />

        {chartType !== 'pie' && (
          <>
            <Divider style={{ margin: '16px 0' }} />
            <div style={{ fontWeight: 'bold', marginBottom: 12 }}>Sorting:</div>
            <SortConfigPanel config={config} onChange={onConfigChange} />

            <Divider style={{ margin: '16px 0' }} />
            <div style={{ fontWeight: 'bold', marginBottom: 12 }}>Colors:</div>
            <ColorConfigPanel
              config={config}
              chartType={chartType}
              onChange={onConfigChange}
            />
          </>
        )}
      </Card>

      {/* Chart Display */}
      {validationError ? (
        <Alert
          message="Invalid Chart Configuration"
          description={validationError}
          type="error"
          showIcon
        />
      ) : (
        <Card>
          <ReactECharts
            option={chartOption!}
            style={{ height: '500px', width: '100%' }}
            opts={{ renderer: 'canvas' }}
            notMerge={true}
            lazyUpdate={true}
          />
        </Card>
      )}
    </Space>
  );
}
