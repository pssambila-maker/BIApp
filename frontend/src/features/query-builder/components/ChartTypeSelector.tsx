import { Radio, Space } from 'antd';
import { BarChartOutlined, LineChartOutlined, AreaChartOutlined, PieChartOutlined } from '@ant-design/icons';
import { ChartType } from '@/types/visualization';

interface Props {
  value: ChartType;
  onChange: (type: ChartType) => void;
}

export default function ChartTypeSelector({ value, onChange }: Props) {
  return (
    <Radio.Group value={value} onChange={(e) => onChange(e.target.value)} size="large">
      <Space>
        <Radio.Button value="bar">
          <BarChartOutlined /> Bar
        </Radio.Button>
        <Radio.Button value="line">
          <LineChartOutlined /> Line
        </Radio.Button>
        <Radio.Button value="area">
          <AreaChartOutlined /> Area
        </Radio.Button>
        <Radio.Button value="pie">
          <PieChartOutlined /> Pie
        </Radio.Button>
      </Space>
    </Radio.Group>
  );
}
