import { Form, Select, Space, Alert } from 'antd';
import { ChartConfiguration } from '@/types/visualization';

interface Props {
  columns: string[];
  config: ChartConfiguration;
  onChange: (config: ChartConfiguration) => void;
}

export default function AxisConfigPanel({ columns, config, onChange }: Props) {
  if (config.chart_type === 'pie') {
    return (
      <Space direction="vertical" style={{ width: '100%' }}>
        <Alert
          message="Pie charts require exactly one category column and one value column"
          type="info"
          showIcon
          style={{ marginBottom: 8 }}
        />
        <Form layout="inline">
          <Form.Item label="Category Column">
            <Select
              style={{ width: 220 }}
              value={config.category_column}
              onChange={(value) => onChange({ ...config, category_column: value })}
              options={columns.map(col => ({ label: col, value: col }))}
              placeholder="Select category"
            />
          </Form.Item>
          <Form.Item label="Value Column">
            <Select
              style={{ width: 220 }}
              value={config.value_column}
              onChange={(value) => onChange({ ...config, value_column: value })}
              options={columns.map(col => ({ label: col, value: col }))}
              placeholder="Select value"
            />
          </Form.Item>
        </Form>
      </Space>
    );
  }

  // Bar, Line, Area charts
  return (
    <Form layout="inline">
      <Form.Item label="X-Axis (Category)">
        <Select
          style={{ width: 220 }}
          value={config.x_axis_column}
          onChange={(value) => onChange({ ...config, x_axis_column: value })}
          options={columns.map(col => ({ label: col, value: col }))}
          placeholder="Select X-axis"
        />
      </Form.Item>
      <Form.Item label="Y-Axis (Values)">
        <Select
          mode="multiple"
          style={{ width: 320 }}
          value={config.y_axis_columns}
          onChange={(values) => onChange({ ...config, y_axis_columns: values })}
          options={columns.map(col => ({ label: col, value: col }))}
          placeholder="Select one or more measures"
          maxTagCount="responsive"
        />
      </Form.Item>
    </Form>
  );
}
