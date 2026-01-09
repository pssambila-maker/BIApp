import { Modal, Form, Input, Checkbox, message } from 'antd';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { savedQueryAPI } from '@/api/semantic';
import { SavedQueryCreate } from '@/types/queryBuilder';

interface Props {
  visible: boolean;
  onClose: () => void;
  queryConfig: {
    entity_id: string;
    dimension_ids: string[];
    measure_ids: string[];
    filters: any[];
    limit: number;
  };
}

export default function SaveQueryModal({ visible, onClose, queryConfig }: Props) {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  const { mutate: saveQuery, isLoading } = useMutation({
    mutationFn: (data: SavedQueryCreate) => savedQueryAPI.create(data),
    onSuccess: () => {
      message.success('Query saved successfully');
      queryClient.invalidateQueries(['saved-queries']);
      form.resetFields();
      onClose();
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to save query');
    },
  });

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      saveQuery({
        name: values.name,
        description: values.description,
        entity_id: queryConfig.entity_id,
        query_config: {
          dimension_ids: queryConfig.dimension_ids,
          measure_ids: queryConfig.measure_ids,
          filters: queryConfig.filters,
          limit: queryConfig.limit,
        },
        is_favorite: values.is_favorite || false,
      });
    } catch (error) {
      // Validation failed
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title="Save Query"
      open={visible}
      onOk={handleSave}
      onCancel={handleCancel}
      confirmLoading={isLoading}
      okText="Save"
      cancelText="Cancel"
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{ is_favorite: false }}
      >
        <Form.Item
          name="name"
          label="Query Name"
          rules={[
            { required: true, message: 'Please enter a name' },
            { max: 255, message: 'Name must be less than 255 characters' },
          ]}
        >
          <Input placeholder="e.g., Monthly Sales by Region" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description (Optional)"
        >
          <Input.TextArea
            rows={3}
            placeholder="Describe what this query does..."
          />
        </Form.Item>

        <Form.Item
          name="is_favorite"
          valuePropName="checked"
        >
          <Checkbox>Mark as favorite</Checkbox>
        </Form.Item>
      </Form>
    </Modal>
  );
}
