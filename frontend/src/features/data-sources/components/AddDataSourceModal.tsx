import { useState } from 'react';
import { Modal, Form, Input, Select, message, Steps } from 'antd';
import { DatabaseOutlined, FileOutlined, SettingOutlined } from '@ant-design/icons';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { dataSourceAPI } from '@/api/dataSources';
import { DataSourceType, DataSourceCreate } from '@/types/dataSource';
import DatabaseForm from './DatabaseForm';
import FileForm from './FileForm';

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function AddDataSourceModal({ open, onClose }: Props) {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [sourceType, setSourceType] = useState<DataSourceType>('postgresql');
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: dataSourceAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['data-sources'] });
      message.success('Data source created successfully!');
      handleClose();
    },
    onError: (error: any) => {
      console.error('Create data source error:', error.response?.data);
      const detail = error.response?.data?.detail;
      if (Array.isArray(detail)) {
        // Pydantic validation errors
        const errors = detail.map((e: any) => `${e.loc.join('.')}: ${e.msg}`).join(', ');
        message.error(`Validation error: ${errors}`);
      } else {
        message.error(detail || 'Failed to create data source');
      }
    },
  });

  const handleClose = () => {
    form.resetFields();
    setCurrentStep(0);
    setSourceType('postgresql');
    onClose();
  };

  const handleNext = async () => {
    try {
      if (currentStep === 0) {
        await form.validateFields(['name', 'type']);
        setCurrentStep(1);
      } else {
        // Get all form values including step 0 fields
        const allValues = form.getFieldsValue(true);
        console.log('All form values:', allValues);

        // Validate only step 2 fields
        await form.validateFields();

        // Rename config to connection_config for backend
        const payload = {
          name: allValues.name,
          description: allValues.description || undefined,
          type: allValues.type,
          connection_config: allValues.config,
        };
        console.log('Payload to send:', payload);
        createMutation.mutate(payload as DataSourceCreate);
      }
    } catch (error) {
      console.error('Validation error:', error);
    }
  };

  const handleBack = () => {
    setCurrentStep(0);
  };

  const isDatabaseType = ['postgresql', 'mysql'].includes(sourceType);

  return (
    <Modal
      title="Add Data Source"
      open={open}
      onOk={handleNext}
      onCancel={currentStep === 0 ? handleClose : handleBack}
      okText={currentStep === 0 ? 'Next' : 'Create'}
      cancelText={currentStep === 0 ? 'Cancel' : 'Back'}
      confirmLoading={createMutation.isPending}
      width={600}
    >
      <Steps
        current={currentStep}
        style={{ marginBottom: 24 }}
        items={[
          { title: 'Basic Info', icon: <SettingOutlined /> },
          { title: 'Connection', icon: isDatabaseType ? <DatabaseOutlined /> : <FileOutlined /> },
        ]}
      />

      <Form
        form={form}
        layout="vertical"
        initialValues={{
          type: 'postgresql',
          config: {
            delimiter: ',',
            encoding: 'utf-8',
          },
        }}
      >
        {currentStep === 0 && (
          <>
            <Form.Item
              name="name"
              label="Name"
              rules={[{ required: true, message: 'Please enter a name!' }]}
            >
              <Input placeholder="My Database" />
            </Form.Item>

            <Form.Item
              name="description"
              label="Description"
            >
              <Input.TextArea rows={3} placeholder="Optional description" />
            </Form.Item>

            <Form.Item
              name="type"
              label="Type"
              rules={[{ required: true, message: 'Please select a type!' }]}
            >
              <Select
                onChange={(value) => setSourceType(value as DataSourceType)}
                options={[
                  { value: 'postgresql', label: 'PostgreSQL', icon: <DatabaseOutlined /> },
                  { value: 'mysql', label: 'MySQL', icon: <DatabaseOutlined /> },
                  { value: 'csv', label: 'CSV File', icon: <FileOutlined /> },
                  { value: 'excel', label: 'Excel File', icon: <FileOutlined /> },
                ]}
              />
            </Form.Item>
          </>
        )}

        {currentStep === 1 && (
          isDatabaseType ? (
            <DatabaseForm sourceType={sourceType} />
          ) : (
            <FileForm sourceType={sourceType} />
          )
        )}
      </Form>
    </Modal>
  );
}
