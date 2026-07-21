import React, { useEffect, useState } from 'react';
import { Card, Descriptions, Tag, List, Spin, Button, Input, Select, message, Space, Typography, Divider } from 'antd';
import { ArrowLeftOutlined, LinkOutlined, RobotOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import dayjs from 'dayjs';

const { Text, Title } = Typography;

interface LeadDetailData {
  id: number;
  post_id: number;
  lead_type: string;
  confidence: number;
  reason: string;
  status: string;
  priority: number;
  created_at: string;
  post: {
    platform: string;
    title: string;
    content: string;
    author: string;
    author_avatar: string;
    published_at: string;
    likes: number;
    collects: number;
    comments_count: number;
    permalink: string;
 stretch: string[];
  } | null;
  comments: Array<{ id: number; author: string; content: string; likes: number; published_at: string }>;
  follow_ups: Array<{ id: number; user_id: number; content: string; created_at: string }>;
}

const leadTypeColors: Record<string, string> = { '找资源': 'orange', '咨询求助': 'blue', '经验分享': 'geekblue', '资源展示': 'purple' };

const LeadDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [lead, setLead] = useState<LeadDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [followUpText, setFollowUpText] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get(`/leads/${id}`);
        setLead(data);
      } catch (err) {
        message.error('加载线索失败');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const updateStatus = async (newStatus: string) => {
    try {
      await api.put(`/leads/${id}/status`, { status: newStatus });
      setLead((prev) => prev ? { ...prev, status: newStatus } : prev);
      message.success('状态已更新');
    } catch (err) {
      message.error('更新失败');
    }
  };

  const addFollowUp = async () => {
    if (!followUpText.trim()) return;
    try {
      await api.post(`/leads/${id}/follow-ups`, { content: followUpText });
      setFollowUpText('');
      const { data } = await api.get(`/leads/${id}`);
      setLead(data);
      message.success('跟进记录已添加');
    } catch (err) {
      message.error('添加失败');
    }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: 100 }}><Spin size="large" /></div>;
  if (!lead) return <div>线索不存在</div>;

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')} style={{ marginBottom: 16 }}>返回列表</Button>

      <Row gutter={24}>
        {/* Left: Post Content */}
        <Col span={16}>
          <Card title={<Title level={4} style={{ margin: 0 }}>{lead.post?.title || '无标题'}</Title>}
            extra={
              lead.post?.permalink ? (
                <a href={lead.post.permalink} target="_blank" rel="noopener noreferrer">
                  <Button icon={<LinkOutlined />} size="small">查看原文</Button>
                </a>
              ) : null
            }>
            <Space style={{ marginBottom: 16 }}>
              <Tag color={leadTypeColors[lead.lead_type] || 'default'}>{lead.lead_type}</Tag>
              <Text type="secondary">发布人: {lead.post?.author || '未知'}</Text>
              <Text type="secondary">{lead.post?.published_at ? dayjs(lead.post.published_at).format('YYYY-MM-DD HH:mm') : ''}</Text>
              <Text type="secondary">👍 {lead.post?.likes || 0}</Text>
              <Text type="secondary">💬 {lead.post?.comments_count || 0}</Text>
            </Space>
            <div style={{
              background: '#fafafa',
              padding: 16,
              borderRadius: 8,
              whiteSpace: 'pre-wrap',
              lineHeight: 1.8,
              fontSize: 14,
            }}>
              {lead.post?.content || '无内容'}
            </div>
          </Card>
        </Col>

        {/* Right: Comments + AI Analysis + Follow-ups */}
        <Col span={8}>
          {/* AI Analysis */}
          <Card
            title={<span><RobotOutlined /> AI 线索识别</span>}
            style={{ marginBottom: 16 }}
          >
            <Descriptions column={1} size="small">
              <Descriptions.Item label="判定类型">
                <Tag color={leadTypeColors[lead.lead_type] || 'default'}>{lead.lead_type}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="置信度">
                <Text style={{ color: lead.confidence >= 0.9 ? '#52c41a' : '#faad14', fontWeight: 600 }}>
                  {(lead.confidence * 100).toFixed(0)}%
                </Text>
              </Descriptions.Item>
              <Descriptions.Item label="判定理由">
                <Text type="secondary">{lead.reason}</Text>
              </Descriptions.Item>
            </Descriptions>
          </Card>

          {/* Status */}
          <Card title="线索状态" style={{ marginBottom: 16 }}>
            <Space>
              <Select
                value={lead.status}
                onChange={updateStatus}
                style={{ width: 120 }}
                options={['新线索', '已查看', '已联系', '已转化', '无效'].map(s => ({ label: s, value: s }))}
              />
            </Space>
          </Card>

          {/* Follow-ups */}
          <Card title="跟进记录" style={{ marginBottom: 16 }}>
            {lead.follow_ups.length === 0 ? (
              <Text type="secondary">暂无跟进记录</Text>
            ) : (
              <List
                size="small"
                dataSource={lead.follow_ups}
                renderItem={(item) => (
                  <List.Item>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {dayjs(item.created_at).format('MM-DD HH:mm')}
                    </Text>
                    <div>{item.content}</div>
                  </List.Item>
                )}
              />
            )}
            <Divider />
            <Space.Compact style={{ width: '100%' }}>
              <Input
                placeholder="添加跟进备注..."
                value={followUpText}
                onChange={(e) => setFollowUpText(e.target.value)}
                onPressEnter={addFollowUp}
              />
              <Button type="primary" onClick={addFollowUp}>添加</Button>
            </Space.Compact>
          </Card>

          {/* Comments */}
          <Card title={`评论 (${lead.comments?.length || 0})`}>
            {lead.comments?.length === 0 ? (
              <Text type="secondary">暂无评论</Text>
            ) : (
              <List
                size="small"
                dataSource={lead.comments}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      title={<Text strong>{item.author}</Text>}
                      description={item.content}
                    />
                  </List.Item>
                )}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default LeadDetail;
