import { Layout, Menu, Dropdown, Avatar, Space } from 'antd';
import { DatabaseOutlined, FundOutlined, CodeOutlined, DashboardOutlined, UserOutlined, LogoutOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

const { Header: AntHeader } = Layout;

export default function Header() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const clearAuth = useAuthStore((state) => state.clearAuth);

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: user?.full_name || user?.username || 'User',
      disabled: true,
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: handleLogout,
    },
  ];

  return (
    <AntHeader style={{ display: 'flex', alignItems: 'center', background: '#001529', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold', marginRight: '50px' }}>
          BI Platform
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          defaultSelectedKeys={['catalog']}
          onClick={({ key }) => navigate(`/${key}`)}
          items={[
            { key: 'catalog', icon: <DatabaseOutlined />, label: 'Semantic Catalog' },
            { key: 'dashboards', icon: <DashboardOutlined />, label: 'Dashboards' },
            { key: 'query-builder', icon: <CodeOutlined />, label: 'Query Builder' },
            { key: 'data-sources', icon: <FundOutlined />, label: 'Data Sources' },
          ]}
        />
      </div>

      <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
        <Space style={{ cursor: 'pointer', color: 'white' }}>
          <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
          <span>{user?.username}</span>
        </Space>
      </Dropdown>
    </AntHeader>
  );
}
