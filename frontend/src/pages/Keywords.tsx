import React, { useEffect, useState } from 'react';
import { Card, Table, Button, Modal, Form, Input, Select, Tag, Popconfirm, Space, message } from 'antd';
import { PlusOutlined, DeleteOutlined, SyncOutlined } from '@ant-design/icons';
import api from '../api';

interface KeywordGroup {
  id: number;
  name: string;
  keywords: string[];
  exclude_keywords: string[];
  platform: string;
  crawl_interval: string;
  is_active: boolean;
  created_at: string;
}

const Keywords: React.FC = () => {
  const [groups, setGroups] = useState<KeywordGroup[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const fetchGroups = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/keywords');
      setGroups(Array.isArray(data) ? data : []);
    } catch (err) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchGroups(); }, []);

  const handleCreate = async (values: any) => {
    try {
      await api.post('/keywords', {
        ...values,
        keywords: values.keywords.split(',').map((s: string) => s.trim()),
        exclude_keywords: (values.exclude_keywords || '').split(',').map((s: string) => s.trim()).filter(Boolean),
      });
      message.success('关键词组已创建');
      setModalOpen(false);
      form.resetFields();
      fetchGroups();
    } catch (err) {
      message.error('创建失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/keywords/${id}`);
      message.success('已删除');
      fetchGroups();
    } catch (err) {
      message.error('删除失败');
    }
  };

  const handleToggleActive = async (group: KeywordGroup) => {
    try {
      await api.put(`/keywords/${group.id}`, { is_active: !group.is_active });
      message.success(group.is_active ? '已停用' : '已启用');
      fetchGroups();
    } catch (err) {
      message.error('操作失败');
    }
  };

  const columns = [
    { title: '名称', dataIndex: 'name', key: 'name', width: 200 },
    {
      title: '关键词',
      dataIndex: 'keywords',
      key: 'keywords',
      render: (kws: string[]) => kws.map((k: string) => <Tag key={k}>{k}</Tag>),
    },
    { title: '平台', dataIndex: 'platform', key: 'platform', width: 120 },
    { title: '采集频率', dataIndex: 'crawl_interval', key: 'crawl_interval', width: 100 },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (is_active: booleanYP, record: KeywordGroup) => (
        <Button
          type={is_active ? 'primary' : 'default'}
          size="small"
          onClick={() => handleToggleActive(record)}
        >
          {is_active ? '运行中' : '已停用'}
        </Button>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_: any, record: KeywordGroup) => (
        <Popconfirm title="确定删除?" onConfirm={() => handleDelete(record.id)}>
          <Button type="link" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div>
      <Card
        title="关键词组管理"
        extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>新建关键词组</Button>}
        style={{ marginBottom: 24 }}
      >
        <p style={{ color: '#888', marginBottom: 16 }}>
          配置关键词组合，系统将按关键词定时搜索小红书帖子，并通过 DeepSeek 自动识别海外营销线索。
        </p>
        <Table
          columns={columns}
          dataSource={groups}
          rowKey="id"
          loading={loading}
          pagination={false}
        />
      </Card>

      <Modal
        title="新建关键词组"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="name" label="名称" rules={[{ required: true }]}>
            <Input placeholder="如: 海外达人营销" />
          </Form.Item>
          <Form.Item name="keywords" label="搜索关键词（逗号分隔）" rules={[{ required: true }]}>
            <Input.TextArea placeholder="海外达人, 海外KOL, 海外红人合作" rows={3} />
          </Form.Item>
          <Form.Item name="exclude_keywords" label="排除词（逗号分隔）">
            <Input placeholder="招聘, 培训" />
          </Form.Item>
          <Form.Item name="platform" label="平台" initialValue="xiaohongshu">
            <Select>
              <Select.Option value="xiaohongshu">小红书</Select.Option>
              <Select.Option value="douyin">抖音</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="crawl_interval" label="采集频率" initialValue="daily">
            <Select>
              <Select.Option value="hourly">每小时</Select.Option>
              <Select.Option value="6hourly">每6小时</Select.Option>
              <Select.Option value="daily">每天</Select.Option>
              <Select.Option value="weekly">每周</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Keywords;
