import { Form, Input, InputNumber, Switch, Select } from 'antd';
import { DatabaseConfig, DataSourceType } from '@/types/dataSource';

interface Props {
  sourceType: DataSourceType;
}

export default function DatabaseForm({ sourceType }: Props) {
  const defaultPorts: Record<string, number> = {
    postgresql: 5432,
    mysql: 3306,
  };

  return (
    <>
      <Form.Item
        name={['config', 'host']}
        label="Host"
        rules={[{ required: true, message: 'Please enter the host!' }]}
        initialValue="localhost"
      >
        <Input placeholder="localhost or IP address" />
      </Form.Item>

      <Form.Item
        name={['config', 'port']}
        label="Port"
        rules={[{ required: true, message: 'Please enter the port!' }]}
        initialValue={defaultPorts[sourceType]}
      >
        <InputNumber min={1} max={65535} style={{ width: '100%' }} />
      </Form.Item>

      <Form.Item
        name={['config', 'database']}
        label="Database"
        rules={[{ required: true, message: 'Please enter the database name!' }]}
      >
        <Input placeholder="Database name" />
      </Form.Item>

      <Form.Item
        name={['config', 'username']}
        label="Username"
        rules={[{ required: true, message: 'Please enter the username!' }]}
      >
        <Input placeholder="Database user" />
      </Form.Item>

      <Form.Item
        name={['config', 'password']}
        label="Password"
        rules={[{ required: true, message: 'Please enter the password!' }]}
      >
        <Input.Password placeholder="Database password" />
      </Form.Item>

      {sourceType === 'postgres' && (
        <Form.Item
          name={['config', 'schema']}
          label="Schema"
          initialValue="public"
        >
          <Input placeholder="public" />
        </Form.Item>
      )}

      <Form.Item
        name={['config', 'ssl_enabled']}
        label="SSL Enabled"
        valuePropName="checked"
        initialValue={false}
      >
        <Switch />
      </Form.Item>
    </>
  );
}
