import React, { useEffect, useState, useCallback } from 'react';
import { Table, Card, Row, Col, Statistic, Tag, Space, Input, Select, Button, DatePicker, message } from 'antd';
import { SearchOutlined, ReloadOutlined, ExportOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import dayjs from 'dayjs';

interface LeadItem {
  id: number;
  title: string;
  author: string;
  platform: string;
  lead_type: string;
  confidence: number;
  status: string;
  reason: string;
  likes: number;
  comments_count: number;
  created_at: string;
}

const leadTypeColors: Record<string, string> = {
  '找资源': 'orange',
  '咨询求助': 'blue',
  '经验分享': 'geekblue',
  '资源展示': 'purple',
};

const statusColors: Record<string, string> = {
  '新线索': 'processing',
  '已查看': 'warning',
  '已联系': 'success',
  '已转化': 'purple',
  '无效': 'default',
};

const Dashboard: React.FC = () => {
  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [keyword, setKeyword] = useState('');
  const [leadType, setLeadType] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [stats, setStats] = useState<any>({});
  const navigate = useNavigate();

  const fetchLeads = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = { page, page_size: pageSize };
      if (keyword) params.keyword = keyword;
      if (leadType) params.lead_type = leadType;
      if (status) params.status = status;

      const { data } = await api.get('/leads', { params });
      setLeads(data.items);
      setTotal(data.total);
    } catch (err) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, keyword, leadType, status]);

  const fetchStats = async () => {
    try {
      const { data } = await api.get('/stats/dashboard');
      setStats(data);
    } catch (err) {}
  };

  useEffect(() => { fetchLeads(); fetchStats(); }, [fetchLeads]);

  const exportCSV = () => {
    message.info('导出功能开发中...');
  };

  const updateStatus = async (id: number, newStatus: string) => {
    try {
      await api.put(`/leads/${id}/status`, { status: newStatus });
      message.success('状态已更新');
      fetchLeads();
      fetchStats();
    } catch (err) {
      message.error('更新失败');
    }
  };

  const columns = [
    {
      title: '帖子标题',
      dataIndex: 'title',
      key: 'title',
      width: 300,
      ellipsis: true,
      render: (text: string, record: LeadItem) => (
        <a onClick={() => navigate(`/leads/${record.id}`)} style={{ fontWeight: 500 }}>
          {text}
        </a>
      ),
    },
    {
      title: '发布人',
      dataIndex: 'author',
      key: 'author',
      width: 100,
    },
    {
      title: '线索类型',
      dataIndex: 'lead_type',
      key: 'lead_type',
      width: 110,
      render: (type: string) => (
        <Tag color={leadTypeColors[type] || 'default'}>{type}</Tag>
      ),
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 80,
      render: (v: number) => <span style={{ color: v >= 0.9 ? '#52c41a' : v >= 0.7 ? '#faad14' : '#ff4d4f' }}>{(v * 100).toFixed(0)}%</span>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 支90,
      render: (s: string, record: LeadItem) => (
        <Select
          value={s}
          size="small"
          style={{ width: 90 }}
          onChange={(val) => updateStatus(record.id, val)}
          options={['新线索', '已查看', '已联系', '已转化', '无效'].map(s => ({ label: s, value: s }))}
        />
      ),
    },
    {
      title: '采集时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (v: string) => v ? dayjs(v).format('YYYY-MM-DD HH:mm') : '-',
    },
  ];

  return (
    <div>
      {/* Stats Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="总线索数" value={stats.total_leads || 0} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="今日新增" value={stats.today_new || 0} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="待处理" value={stats.status_counts?.['新线索'] || 0} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="已转化" value={stats.status_counts?.['已转化'] || 0} /></Card>
        </Col>
      </Row>

      {/* Filter Bar */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input
            placeholder="搜索标题/内容/发布人..."
            prefix={<SearchOutlined />}
            value={keyword}
            onChange={(e) => { setKeyword(e.target.value); setPage(1); }}
            style={{ width: 250 }}
            allowClear
          />
          <Select
            placeholder="线索类型"
            value={leadType || undefined}
            onChange={(v) => { setLeadType(v || ''); setPage(1); }}
            style={{ width: 120 }}
            allowClear
          >
            <Select.Option value="找资源">找资源</Select.Option>
            <Select.Option value="咨询求助">咨询求助</Select.Option>
            <Select.Option value="经验分享">经验分享</Select.Option>
            <Select.Option value="资源展示">资源展示</Select.Option>
          </Select>
          <Select
            placeholder="状态"
            value={status || undefined}
            onChange={(v) => { setStatus(v || ''); setPage(1); }}
            style={{ width: 100 }}
            allowClear
          >
            <Select.Option value="新线索">新线索</Select.Option>
            <Select.Option value="已查看">已查看</Select.Option>
            <Select.Option value="已联系">已联系</Select.Option>
            <Select.Option value="已转化">已转化</Select.Option>
            <Select.Option value="无效">无效</Select.Option>
          </Select>
          <Button icon={<ReloadOutlined />} onClick={() => { setKeyword(''); setLeadType(''); setStatus(''); setPage(1); }}>
            重置
          </Button>
          <Button type="primary" icon={<ExportOutlined />} onClick={exportCSV}>
            导出 Excel
          </Button>
        </Space>
      </Card>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={leads}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize,
            total,
            showTotal: (total) => `共 ${total} 条线索`,
            onChange: (p) => setPage(p),
          }}
          scroll={{ x: 1000 }}
        />
      </Card>
    </div>
  );
};

export default Dashboard;
