import { useState, useEffect } from 'react';
import { Modal, Form, Input, Select, InputNumber, message, Tabs, Space, Button, Divider } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { semanticAPI } from '@/api/semantic';
import { DashboardWidgetCreate, GridPosition } from '@/types/dashboard';
import { ChartType } from '@/types/visualization';

interface AddWidgetModalProps {
  open: boolean;
  onCancel: () => void;
  onOk: (widget: DashboardWidgetCreate) => void;
  existingWidgets: any[];
}

const chartTypeOptions = [
  { value: 'bar', label: 'Bar Chart' },
  { value: 'line', label: 'Line Chart' },
  { value: 'pie', label: 'Pie Chart' },
  { value: 'area', label: 'Area Chart' },
  { value: 'scatter', label: 'Scatter Plot' },
  { value: 'table', label: 'Table' },
];

export default function AddWidgetModal({ open, onCancel, onOk }: AddWidgetModalProps) {
  const [form] = Form.useForm();
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>([]);
  const [selectedMeasures, setSelectedMeasures] = useState<string[]>([]);

  // Fetch entities
  const { data: entities } = useQuery({
    queryKey: ['semantic-entities'],
    queryFn: () => semanticAPI.listEntities(),
  });

  // Fetch entity details when selected
  const { data: entityDetails } = useQuery({
    queryKey: ['semantic-entity', selectedEntityId],
    queryFn: () => semanticAPI.getEntity(selectedEntityId!),
    enabled: !!selectedEntityId,
  });

  useEffect(() => {
    if (!open) {
      form.resetFields();
      setSelectedEntityId(null);
      setSelectedDimensions([]);
      setSelectedMeasures([]);
    }
  }, [open, form]);

  const handleOk = async () => {
    try {
      const values = await form.validateFields();

      if (!selectedEntityId) {
        message.error('Please select a semantic entity');
        return;
      }

      if (selectedDimensions.length === 0 && selectedMeasures.length === 0) {
        message.error('Please select at least one dimension or measure');
        return;
      }

      // Build query configuration
      const queryConfig = {
        entity_id: selectedEntityId,
        dimensions: selectedDimensions,
        measures: selectedMeasures,
        filters: [],
        limit: values.limit || 1000,
      };

      // Build chart configuration
      const chartConfig = {
        chart_type: values.chart_type,
        x_axis: selectedDimensions[0] || null,
        y_axis: selectedMeasures[0] || null,
        show_legend: values.show_legend ?? true,
        show_data_labels: values.show_data_labels ?? false,
      };

      // Calculate grid position (simple auto-placement)
      const gridPosition: GridPosition = {
        x: values.position_x ?? 0,
        y: values.position_y ?? 0,
        w: values.width ?? 6,
        h: values.height ?? 4,
      };

      const widgetData: DashboardWidgetCreate = {
        title: values.title,
        description: values.description,
        query_config: queryConfig,
        chart_config: chartConfig,
        grid_position: gridPosition,
        position_order: 0,
        refresh_interval: values.refresh_interval,
      };

      onOk(widgetData);
      form.resetFields();
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  const dimensionOptions = entityDetails?.dimensions.map((dim) => ({
    value: dim.id,
    label: dim.display_name,
  })) || [];

  const measureOptions = entityDetails?.measures.map((measure) => ({
    value: measure.id,
    label: measure.display_name,
  })) || [];

  return (
    <Modal
      title="Add Widget to Dashboard"
      open={open}
      onCancel={onCancel}
      onOk={handleOk}
      width={700}
      okText="Add Widget"
    >
      <Form form={form} layout="vertical">
        <Tabs
          items={[
            {
              key: 'data',
              label: 'Data Configuration',
              children: (
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                  <Form.Item
                    name="entity_id"
                    label="Semantic Entity"
                    rules={[{ required: true, message: 'Please select a semantic entity' }]}
                  >
                    <Select
                      placeholder="Select an entity"
                      onChange={(value) => {
                        setSelectedEntityId(value);
                        setSelectedDimensions([]);
                        setSelectedMeasures([]);
                      }}
                      options={entities?.entities.map((entity) => ({
                        value: entity.id,
                        label: entity.display_name,
                      }))}
                    />
                  </Form.Item>

                  <Form.Item label="Dimensions">
                    <Select
                      mode="multiple"
                      placeholder="Select dimensions"
                      value={selectedDimensions}
                      onChange={setSelectedDimensions}
                      options={dimensionOptions}
                      disabled={!selectedEntityId}
                    />
                  </Form.Item>

                  <Form.Item label="Measures">
                    <Select
                      mode="multiple"
                      placeholder="Select measures"
                      value={selectedMeasures}
                      onChange={setSelectedMeasures}
                      options={measureOptions}
                      disabled={!selectedEntityId}
                    />
                  </Form.Item>

                  <Form.Item name="limit" label="Row Limit" initialValue={1000}>
                    <InputNumber min={1} max={10000} style={{ width: '100%' }} />
                  </Form.Item>
                </Space>
              ),
            },
            {
              key: 'visualization',
              label: 'Visualization',
              children: (
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                  <Form.Item
                    name="title"
                    label="Widget Title"
                    rules={[{ required: true, message: 'Please enter a title' }]}
                  >
                    <Input placeholder="Enter widget title" />
                  </Form.Item>

                  <Form.Item name="description" label="Description">
                    <Input.TextArea rows={2} placeholder="Optional description" />
                  </Form.Item>

                  <Form.Item
                    name="chart_type"
                    label="Chart Type"
                    initialValue="bar"
                    rules={[{ required: true }]}
                  >
                    <Select options={chartTypeOptions} />
                  </Form.Item>

                  <Form.Item name="show_legend" label="Show Legend" initialValue={true}>
                    <Select options={[
                      { value: true, label: 'Yes' },
                      { value: false, label: 'No' },
                    ]} />
                  </Form.Item>

                  <Form.Item name="show_data_labels" label="Show Data Labels" initialValue={false}>
                    <Select options={[
                      { value: true, label: 'Yes' },
                      { value: false, label: 'No' },
                    ]} />
                  </Form.Item>

                  <Form.Item name="refresh_interval" label="Auto-refresh Interval (seconds)">
                    <InputNumber min={5} max={3600} placeholder="Optional (e.g., 30)" style={{ width: '100%' }} />
                  </Form.Item>
                </Space>
              ),
            },
            {
              key: 'position',
              label: 'Position & Size',
              children: (
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                  <div>
                    <strong>Grid Position</strong>
                    <Divider style={{ margin: '8px 0' }} />
                  </div>

                  <Space>
                    <Form.Item name="position_x" label="X Position" initialValue={0}>
                      <InputNumber min={0} max={11} />
                    </Form.Item>

                    <Form.Item name="position_y" label="Y Position" initialValue={0}>
                      <InputNumber min={0} />
                    </Form.Item>
                  </Space>

                  <div>
                    <strong>Widget Size</strong>
                    <Divider style={{ margin: '8px 0' }} />
                  </div>

                  <Space>
                    <Form.Item name="width" label="Width (1-12 columns)" initialValue={6}>
                      <InputNumber min={1} max={12} />
                    </Form.Item>

                    <Form.Item name="height" label="Height (grid units)" initialValue={4}>
                      <InputNumber min={1} max={20} />
                    </Form.Item>
                  </Space>

                  <div style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
                    The dashboard uses a 12-column grid system. Position and size can be adjusted later by dragging.
                  </div>
                </Space>
              ),
            },
          ]}
        />
      </Form>
    </Modal>
  );
}
