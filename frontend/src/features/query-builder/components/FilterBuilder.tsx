import { Button, Select, Space } from 'antd';
import { PlusOutlined, CloseOutlined } from '@ant-design/icons';
import { SemanticDimension } from '@/types/semantic';
import { FilterCondition } from '@/types/queryBuilder';
import ValueInput from './ValueInput';

export interface FilterRow {
  id: string;
  dimension_id: string;
  operator: FilterCondition['operator'];
  value: any;
}

interface Props {
  dimensions: SemanticDimension[];
  filters: FilterRow[];
  onChange: (filters: FilterRow[]) => void;
}

// Operators by data type
const OPERATORS_BY_TYPE: Record<string, FilterCondition['operator'][]> = {
  string: ['=', '!=', 'LIKE', 'IN', 'NOT IN', 'IS NULL', 'IS NOT NULL'],
  integer: ['=', '!=', '>', '<', '>=', '<=', 'IN', 'NOT IN', 'IS NULL', 'IS NOT NULL'],
  decimal: ['=', '!=', '>', '<', '>=', '<=', 'IN', 'NOT IN', 'IS NULL', 'IS NOT NULL'],
  date: ['=', '!=', '>', '<', '>=', '<=', 'IS NULL', 'IS NOT NULL'],
  boolean: ['=', '!=', 'IS NULL', 'IS NOT NULL'],
};

// Operator labels for display
const OPERATOR_LABELS: Record<FilterCondition['operator'], string> = {
  '=': 'equals',
  '!=': 'not equals',
  '>': 'greater than',
  '<': 'less than',
  '>=': 'greater than or equal',
  '<=': 'less than or equal',
  'IN': 'is one of',
  'NOT IN': 'is not one of',
  'LIKE': 'contains',
  'IS NULL': 'is empty',
  'IS NOT NULL': 'is not empty',
};

export default function FilterBuilder({ dimensions, filters, onChange }: Props) {
  const addFilter = () => {
    const newFilter: FilterRow = {
      id: `filter_${Date.now()}`,
      dimension_id: '',
      operator: '=',
      value: null,
    };
    onChange([...filters, newFilter]);
  };

  const removeFilter = (id: string) => {
    onChange(filters.filter(f => f.id !== id));
  };

  const updateFilter = (id: string, updates: Partial<FilterRow>) => {
    onChange(
      filters.map(f => f.id === id ? { ...f, ...updates } : f)
    );
  };

  return (
    <div>
      <label style={{ fontWeight: 'bold', marginBottom: 8, display: 'block' }}>
        Filters (Optional):
      </label>

      <Space direction="vertical" style={{ width: '100%' }} size="small">
        {filters.map(filter => {
          const dimension = dimensions.find(d => d.id === filter.dimension_id);
          const operators = dimension ? OPERATORS_BY_TYPE[dimension.data_type] : [];

          return (
            <Space key={filter.id} style={{ width: '100%' }}>
              {/* Dimension Selector */}
              <Select
                style={{ width: 200 }}
                placeholder="Select dimension"
                value={filter.dimension_id || undefined}
                onChange={(dimensionId) => {
                  const dim = dimensions.find(d => d.id === dimensionId);
                  updateFilter(filter.id, {
                    dimension_id: dimensionId,
                    operator: dim ? OPERATORS_BY_TYPE[dim.data_type][0] : '=',
                    value: null,
                  });
                }}
                options={dimensions.map(d => ({
                  value: d.id,
                  label: d.name,
                }))}
              />

              {/* Operator Selector */}
              {filter.dimension_id && (
                <Select
                  style={{ width: 150 }}
                  value={filter.operator}
                  onChange={(operator) => updateFilter(filter.id, { operator, value: null })}
                  options={operators.map(op => ({
                    value: op,
                    label: OPERATOR_LABELS[op],
                  }))}
                />
              )}

              {/* Value Input */}
              {filter.dimension_id && dimension && (
                <ValueInput
                  dataType={dimension.data_type}
                  operator={filter.operator}
                  value={filter.value}
                  onChange={(value) => updateFilter(filter.id, { value })}
                />
              )}

              {/* Remove Button */}
              <Button
                type="text"
                danger
                icon={<CloseOutlined />}
                onClick={() => removeFilter(filter.id)}
              />
            </Space>
          );
        })}

        {/* Add Filter Button */}
        <Button
          type="dashed"
          icon={<PlusOutlined />}
          onClick={addFilter}
          disabled={dimensions.length === 0}
        >
          Add Filter
        </Button>
      </Space>
    </div>
  );
}
