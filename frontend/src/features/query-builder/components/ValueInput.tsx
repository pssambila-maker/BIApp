import { Input, InputNumber, Select, DatePicker } from 'antd';
import { SemanticDimension } from '@/types/semantic';
import { FilterCondition } from '@/types/queryBuilder';
import dayjs from 'dayjs';

interface ValueInputProps {
  dataType: SemanticDimension['data_type'];
  operator: FilterCondition['operator'];
  value: any;
  onChange: (value: any) => void;
}

export default function ValueInput({ dataType, operator, value, onChange }: ValueInputProps) {
  // No input for NULL operators
  if (operator === 'IS NULL' || operator === 'IS NOT NULL') {
    return null;
  }

  // Multi-value input for IN/NOT IN
  if (operator === 'IN' || operator === 'NOT IN') {
    return (
      <Select
        mode="tags"
        style={{ width: 250 }}
        placeholder="Enter values and press enter"
        value={value || []}
        onChange={onChange}
      />
    );
  }

  // Type-specific inputs
  switch (dataType) {
    case 'string':
      return (
        <Input
          style={{ width: 250 }}
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder={operator === 'LIKE' ? 'e.g., %search%' : 'Enter value'}
        />
      );

    case 'integer':
      return (
        <InputNumber
          style={{ width: 250 }}
          value={value}
          onChange={onChange}
          precision={0}
          placeholder="Enter number"
        />
      );

    case 'decimal':
      return (
        <InputNumber
          style={{ width: 250 }}
          value={value}
          onChange={onChange}
          placeholder="Enter number"
        />
      );

    case 'date':
      return (
        <DatePicker
          value={value ? dayjs(value) : null}
          onChange={(date) => onChange(date ? date.format('YYYY-MM-DD') : null)}
          style={{ width: 250 }}
        />
      );

    case 'boolean':
      return (
        <Select
          style={{ width: 250 }}
          value={value}
          onChange={onChange}
          placeholder="Select value"
        >
          <Select.Option value={true}>True</Select.Option>
          <Select.Option value={false}>False</Select.Option>
        </Select>
      );

    default:
      return (
        <Input
          style={{ width: 250 }}
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Enter value"
        />
      );
  }
}
