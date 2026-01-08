import { Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { SemanticMeasure } from '@/types/semantic';

interface Props {
  measures: SemanticMeasure[];
}

const AGGREGATION_COLORS: Record<string, string> = {
  SUM: 'blue',
  COUNT: 'green',
  AVG: 'orange',
  MIN: 'purple',
  MAX: 'red',
  MEDIAN: 'cyan',
  STDDEV: 'magenta',
};

export default function MeasureList({ measures }: Props) {
  const columns: ColumnsType<SemanticMeasure> = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Description', dataIndex: 'description', key: 'description' },
    {
      title: 'Aggregation',
      dataIndex: 'aggregation_function',
      key: 'aggregation_function',
      render: (agg: string) => (
        <Tag color={AGGREGATION_COLORS[agg] || 'default'}>{agg}</Tag>
      ),
    },
    { title: 'Base Column', dataIndex: 'base_column', key: 'base_column', render: (text) => <code>{text}</code> },
    { title: 'Format', dataIndex: 'format', key: 'format' },
  ];

  return (
    <Table
      columns={columns}
      dataSource={measures}
      rowKey="id"
      pagination={false}
      size="small"
    />
  );
}
