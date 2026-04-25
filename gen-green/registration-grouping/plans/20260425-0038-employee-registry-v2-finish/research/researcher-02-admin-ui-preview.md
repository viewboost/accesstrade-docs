# Admin UI Preview Pattern Research — Gen-Green Employee Registry V2

## 1. Detail-of-Detail Page Pattern

**Files:** `config/routes.ts`, `segment/detail/index.tsx`, `event/detail/index.tsx`

**Pattern hiện tại:**
- Route: `/segment/:id`, `/event/:id` (không nested sub-route, chỉ 1 level)
- Lấy param từ **DVA model state** (dispatch action `getDetail` với `payload.id`, state store `detail`)
- Component dùng `connect(({segmentModel}) => ({segmentModel}))` wrapper, không dùng `useParams`
- Layout: PageContainer + header with back link + TabView component (nested tabs component)
- Không có nested preview route kiểu `/imports/:importId/preview` trong vcreator

**Code snippet:**
```tsx
// segment/detail/index.tsx
const CampaignDetail: React.FC<Props> = (props) => {
  const { segmentModel } = props;
  const { detail } = segmentModel;
  
  return (
    <PageContainer pageHeaderRender={helper.renderHeader}>
      <Link to={`/segment`}><Space>← {detail?.name}</Space></Link>
      <TabView /> {/* tabs component */}
    </PageContainer>
  );
};
export default connect(({ segmentModel }: Props) => ({ segmentModel }))(CampaignDetail);
```

**Áp dụng cho `/employee-registry/imports/:importId/preview`:**
- Thêm route: `/employee-registry/imports/:importId/preview` → `./components/import-preview`
- Dùng DVA model, dispatch `employeeRegistryModel/getImportDetail` với `importId` từ URL params (cần inject via hook hoặc model middleware)
- **CAVEAT:** DVA connect dùng state, không dùng `useParams` trực tiếp — cần custom hook hoặc inject từ URL parser

---

## 2. Sort + Filter Table Pattern (Large Dataset)

**Files:** `segment/components/table.tsx`, `segment/components/filter.tsx`, `segment/model.ts`

**Pattern hiện tại:**
- **Dùng ProTable từ Ant Design Pro** (RcTableNew = ProTable wrapper)
  - `sortDirections={['descend', 'ascend']}` — both directions enabled
  - `search={false}` — no built-in search (filter bar external)
  - `onChange={onTableChange}` — server-side sort/pagination via handler
- **Filter:** External FilterBar component, dispatch `segmentModel/getList` với `body: {...filter, page, pageSize}`
- **Columns:** ProColumns[] với dataIndex nested support `['partner', 'name']`
- **Pagination:** Custom GetPagination() wrapper, viVNIntl locale

**Code snippet:**
```tsx
// segment/components/table.tsx
const columns: ProColumns<Segment.Info>[] = [
  { title: 'Name', dataIndex: 'name', renderText: ... },
  { title: 'Partner', dataIndex: ['partner', 'name'] },
  { title: 'Status', dataIndex: 'status', align: 'center', renderText: ... }
];

return (
  <RcTableNew<Segment.Info>
    dataSource={list}
    columns={columns}
    pagination={pagination}
    onChange={onTableChange} // → server call
    scroll={{ x: 500 }}
  />
);

// segment/model.ts (DVA)
*getList({ payload }, { call, put }) {
  const response = yield call(serviceSegment.getList, payload.body);
  yield put({
    type: 'updateState',
    payload: { list: data.data, filter: {...payload.body, total: data.total} }
  });
}
```

**Áp dụng cho 9-column table (pageSize=50):**
- Dùng ProTable + RcTableNew wrapper (consistent với existing)
- Columns: action_type (renderText → badge color), workplace, field_1-6 (nested dataIndex), impact_count
- Sort: impact_priority (8 categories), server-side dispatch via `onChange`
- Filter: Select mode="multiple" cho action_type, text input cho workplace, search
- Pagination: `pageSize: 50` (default 20) — set ở component level `pagination.pageSize`

---

## 3. Counter Cards Header Pattern

**Files:** `event-statistic/index.tsx` (lines 625-700)

**Pattern hiện tại:**
- **Ant Design Statistic component** (không custom card)
- Layout: `<Row gutter={[20,20]} wrap>` → `<Col span={12|24|xl={12}>` → `<Statistic title="" value="" prefix={icon} />`
- Icon: `BookOutlined`, `DollarCircleOutlined`, `EyeOutlined` từ `@ant-design/icons`
- Grouping: Typography.Title level=4 + Row/Col grid (2 cols, responsive)
- Data mapping: array of `{_id: 'label.xxx', name: '123'}` → render loop

**Code snippet:**
```tsx
// event-statistic
const dataList = useMemo(() => ({
  content: [{_id: 'label.approved', name: 'x'}, ...],
  cash: [{_id: 'label.cashback', name: '$xxx'}, ...]
}), [statistic]);

return (
  <Row gutter={[40, 40]}>
    <Col span={12}>
      <Typography.Title level={4}>Content</Typography.Title>
      <Row gutter={[20, 20]} wrap>
        {dataList.content.map((item) => (
          <Col key={item._id} span={12}>
            <Statistic title={intl(item._id)} value={item.name} prefix={<BookOutlined />} />
          </Col>
        ))}
      </Row>
    </Col>
  </Row>
);
```

**Áp dụng cho 8 action types counter:**
- Array data: `[{type: 'cancelled_mismatch', count: 15, color: 'red'}, ...]`
- Render: `<Row gutter={[24,24]}> {data.map(item => <Col span={6|8}>` + `<Statistic title={item.type} value={item.count} />`)
- Color coding: Badge or wrapper `<div style={{borderLeft: `3px solid ${statusColorMap[item.type]}`}}>`
- No icons needed (action type text is label)

---

## Implementation Checklist

- [x] Detail route (not nested preview) — DVA model + PageContainer
- [x] ProTable with sort/filter — existing pattern in segment
- [x] Counter cards — Statistic + Row/Col grid from event-statistic
- [x] Use RcTableNew wrapper for consistency
- [x] Pagination pageSize=50 (configurable via column definition)

---

## Unresolved Questions

1. **URL params injection in DVA:** How to extract `:importId` from URL in model effect? (Need middleware or custom hook bridge?)
2. **Multi-select filter for 8 action types:** Should use `Select mode="multiple"` or Checkbox group in FilterBar? (vcreator precedent?)
3. **Table column sort: server-side or client-side?** Check if ProTable's `onChange` handler already sends `sort` field to backend.
