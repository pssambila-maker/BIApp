import { Select, Space, Typography, Input, Row, Col } from 'antd';
import { BgColorsOutlined } from '@ant-design/icons';
import { ChartConfiguration, ColorMode, ChartType } from '@/types/visualization';

const { Text } = Typography;

interface Props {
  config: ChartConfiguration;
  chartType: ChartType;
  onChange: (config: ChartConfiguration) => void;
}

export default function ColorConfigPanel({ config, chartType, onChange }: Props) {
  const colorModeOptions = [
    { value: 'conditional', label: 'Conditional (by value)' },
    { value: 'single', label: 'Single color' },
  ];

  // Conditional coloring only works for bar charts with single series
  const showConditionalColors = config.color_mode === 'conditional' &&
                                  chartType === 'bar' &&
                                  config.y_axis_columns.length === 1;

  const conditionalColors = config.conditional_colors || [
    { condition: 'positive', color: '#5470c6' },
    { condition: 'negative', color: '#ee6666' },
    { condition: 'zero', color: '#91cc75' },
  ];

  const updateConditionalColor = (condition: 'positive' | 'negative' | 'zero', color: string) => {
    const newColors = conditionalColors.map(rule =>
      rule.condition === condition ? { ...rule, color } : rule
    );
    onChange({ ...config, conditional_colors: newColors });
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      <div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
          <BgColorsOutlined style={{ marginRight: 8, fontSize: 16 }} />
          <Text strong>Color Mode:</Text>
        </div>
        <Select
          style={{ width: '100%' }}
          value={config.color_mode || 'conditional'}
          onChange={(value: ColorMode) =>
            onChange({ ...config, color_mode: value })
          }
          options={colorModeOptions}
        />
      </div>

      {showConditionalColors && (
        <div>
          <Text strong style={{ display: 'block', marginBottom: 8 }}>
            Conditional Colors:
          </Text>
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            <Row gutter={8} align="middle">
              <Col span={12}>
                <Text>Positive values:</Text>
              </Col>
              <Col span={12}>
                <Input
                  type="color"
                  value={conditionalColors.find(r => r.condition === 'positive')?.color || '#5470c6'}
                  onChange={(e) => updateConditionalColor('positive', e.target.value)}
                  style={{ width: '100%', height: 32 }}
                />
              </Col>
            </Row>
            <Row gutter={8} align="middle">
              <Col span={12}>
                <Text>Negative values:</Text>
              </Col>
              <Col span={12}>
                <Input
                  type="color"
                  value={conditionalColors.find(r => r.condition === 'negative')?.color || '#ee6666'}
                  onChange={(e) => updateConditionalColor('negative', e.target.value)}
                  style={{ width: '100%', height: 32 }}
                />
              </Col>
            </Row>
            <Row gutter={8} align="middle">
              <Col span={12}>
                <Text>Zero values:</Text>
              </Col>
              <Col span={12}>
                <Input
                  type="color"
                  value={conditionalColors.find(r => r.condition === 'zero')?.color || '#91cc75'}
                  onChange={(e) => updateConditionalColor('zero', e.target.value)}
                  style={{ width: '100%', height: 32 }}
                />
              </Col>
            </Row>
          </Space>
        </div>
      )}

      {config.color_mode === 'conditional' && chartType === 'bar' && config.y_axis_columns.length > 1 && (
        <Text type="secondary" style={{ fontSize: 12 }}>
          Note: Conditional colors are only applied when there's a single measure selected.
        </Text>
      )}

      {config.color_mode === 'conditional' && chartType !== 'bar' && (
        <Text type="secondary" style={{ fontSize: 12 }}>
          Note: Conditional colors are only available for bar charts.
        </Text>
      )}
    </Space>
  );
}
