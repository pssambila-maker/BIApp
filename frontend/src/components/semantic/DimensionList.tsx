import { Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { SemanticDimension } from '@/types/semantic';

interface Props {
  dimensions: SemanticDimension[];
}

export default function DimensionList({ dimensions }: Props) {
  const columns: ColumnsType<SemanticDimension> = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Description', dataIndex: 'description', key: 'description' },
    { title: 'SQL Column', dataIndex: 'sql_column', key: 'sql_column', render: (text) => <code>{text}</code> },
    { title: 'Data Type', dataIndex: 'data_type', key: 'data_type' },
    { title: 'Format', dataIndex: 'display_format', key: 'display_format' },
  ];

  return (
    <Table
      columns={columns}
      dataSource={dimensions}
      rowKey="id"
      pagination={false}
      size="small"
    />
  );
}
