import { Select, Space, Typography } from 'antd';
import { SortAscendingOutlined } from '@ant-design/icons';
import { ChartConfiguration, SortOrder, SortBy } from '@/types/visualization';

const { Text } = Typography;

interface Props {
  config: ChartConfiguration;
  onChange: (config: ChartConfiguration) => void;
}

export default function SortConfigPanel({ config, onChange }: Props) {
  const sortOrderOptions = [
    { value: 'none', label: 'No Sorting' },
    { value: 'ascending', label: 'Ascending (A → Z, 1 → 9)' },
    { value: 'descending', label: 'Descending (Z → A, 9 → 1)' },
  ];

  const sortByOptions = [
    { value: 'category', label: 'Sort by Category (X-axis)' },
    { value: 'value', label: 'Sort by Value (Y-axis)' },
  ];

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="middle">
      <div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
          <SortAscendingOutlined style={{ marginRight: 8, fontSize: 16 }} />
          <Text strong>Sort Order:</Text>
        </div>
        <Select
          style={{ width: '100%' }}
          value={config.sort_order || 'none'}
          onChange={(value: SortOrder) =>
            onChange({ ...config, sort_order: value })
          }
          options={sortOrderOptions}
        />
      </div>

      {config.sort_order && config.sort_order !== 'none' && (
        <div>
          <Text strong>Sort By:</Text>
          <Select
            style={{ width: '100%', marginTop: 8 }}
            value={config.sort_by || 'category'}
            onChange={(value: SortBy) =>
              onChange({ ...config, sort_by: value })
            }
            options={sortByOptions}
          />
        </div>
      )}
    </Space>
  );
}
