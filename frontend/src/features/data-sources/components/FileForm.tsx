import { Form, Input, Upload, Select, Button } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { DataSourceType } from '@/types/dataSource';

interface Props {
  sourceType: DataSourceType;
}

export default function FileForm({ sourceType }: Props) {
  return (
    <>
      <Form.Item
        name={['config', 'file_path']}
        label="File Path"
        rules={[{ required: true, message: 'Please enter the file path!' }]}
        tooltip="Enter the full path to the file on the server"
      >
        <Input placeholder="/path/to/your/file.csv" />
      </Form.Item>

      {sourceType === 'excel' && (
        <Form.Item
          name={['config', 'sheet_name']}
          label="Sheet Name"
          tooltip="Leave empty to use the first sheet"
        >
          <Input placeholder="Sheet1" />
        </Form.Item>
      )}

      {sourceType === 'csv' && (
        <>
          <Form.Item
            name={['config', 'delimiter']}
            label="Delimiter"
            initialValue=","
          >
            <Select>
              <Select.Option value=",">Comma (,)</Select.Option>
              <Select.Option value=";">Semicolon (;)</Select.Option>
              <Select.Option value="\t">Tab</Select.Option>
              <Select.Option value="|">Pipe (|)</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name={['config', 'encoding']}
            label="Encoding"
            initialValue="utf-8"
          >
            <Select>
              <Select.Option value="utf-8">UTF-8</Select.Option>
              <Select.Option value="latin1">Latin-1</Select.Option>
              <Select.Option value="ascii">ASCII</Select.Option>
            </Select>
          </Form.Item>
        </>
      )}

      <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
        <p style={{ margin: 0, fontSize: 12, color: '#666' }}>
          <strong>Note:</strong> For file-based data sources, the file must be accessible from the backend server.
          Upload functionality will be added in a future update.
        </p>
      </div>
    </>
  );
}
