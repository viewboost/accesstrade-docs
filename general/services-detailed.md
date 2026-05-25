# Backend Services — Detailed Inventory

> Generated: 2026-05-07. LOC + exported functions (Go) per service file across 3 projects.
> Source: `backend/internal/service/<name>.go` ở mỗi repo.
> Method: regex parse `func ... ([A-Z]\w+)\(` — chỉ count exported functions.

**Cách đọc**:
- `LOC` = số dòng code không trống
- `Functions` = các hàm exported (chữ hoa đầu) — methods + standalone functions
- `❌` = service file không tồn tại ở repo đó

---

## User & Auth

### `user.go`

**Existence**: TCB: 653 LOC, 4 fns | vCreator: 443 LOC, 4 fns | Ambassador: 497 LOC, 5 fns

**Shared by all 3** (4): `GenerateUserSocial, UpdateStatistic, UpdateUserPartnerStatistic, User`

**Ambassador-only** (1): `CheckUserIsFullFullProfile`


### `user_social.go`

**Existence**: TCB: 325 LOC, 3 fns | vCreator: 78 LOC, 2 fns | Ambassador: 321 LOC, 3 fns

**Shared by all 3** (2): `RenewAccessToken, UserSocial`

**Ambassador+TCB only** (1): `CheckUserSocialProfile`


### `user_social_partner.go`

**Existence**: TCB: 209 LOC, 3 fns | vCreator: ❌ | Ambassador: 59 LOC, 1 fns

**Ambassador+TCB only** (1): `GenerateUserSocialPartner`

**TCB-only** (2): `CheckStatusUserSocialPartner, GenerateInfluencerWhenCreatePartner`


### `otp.go`

**Existence**: TCB: 129 LOC, 3 fns | vCreator: 129 LOC, 3 fns | Ambassador: 129 LOC, 3 fns

**Shared by all 3** (3): `Otp, SendOTPAccessTrade, VerifyOTP`


---

## Content & Media

### `content.go`

**Existence**: TCB: 481 LOC, 9 fns | vCreator: 521 LOC, 10 fns | Ambassador: 635 LOC, 10 fns

**Shared by all 3** (9): `ActionAfterWhenChangeStatus, ChangeStatus, CheckHashTag, Content, GetStatisticContentIsRewardInDay, RejectListContentByIds, UpdateCashStatistic, UpdateRateViewAndOld, WarningTagContent`

**Ambassador+vCreator only** (1): `UploadImagesFromURLs`


### `content_flow.go`

**Existence**: TCB: 233 LOC, 5 fns | vCreator: 235 LOC, 5 fns | Ambassador: 248 LOC, 5 fns

**Shared by all 3** (5): `ContentFlow, CreateComment, CreateFlow, CreateLike, CreateView`


### `content_analytic_daily.go`

**Existence**: TCB: 447 LOC, 5 fns | vCreator: 517 LOC, 5 fns | Ambassador: 443 LOC, 5 fns

**Shared by all 3** (5): `Audit, ContentAnalyticDaily, DeleteContentFlow, Update, UpdateWhenManualFlowHasCreated`


### `video.go`

**Existence**: TCB: 50 LOC, 2 fns | vCreator: 50 LOC, 2 fns | Ambassador: 50 LOC, 2 fns

**Shared by all 3** (2): `SetIsUse, Video`


### `upload_avatar_social.go`

**Existence**: TCB: 222 LOC, 2 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (2): `NewUploadAvatarSocialService, UploadAvatarSocial`


---

## Campaign & Event

### `event.go`

**Existence**: TCB: 1426 LOC, 11 fns | vCreator: 1064 LOC, 6 fns | Ambassador: 1504 LOC, 12 fns

**Shared by all 3** (4): `Event, UpdateAnalyticEventDaily, UpdateAnalyticUserEventDaily, UpdateStatisticUserEvent`

**Ambassador+TCB only** (4): `CombineBudgetEstimates, UpdateBudgetStatistic, UpdateEventStatistic, WithBudgetLock`

**Ambassador+vCreator only** (2): `UpdateAnalyticOldEventDaily, UpdateUserEventAnalyticDaily`

**TCB-only** (3): `EstimateBudgetByEvent, EstimateBudgetMultiLevel, UpdateAnalyticEventDailyWhenContentChangeStatus`

**Ambassador-only** (2): `EstimateBudget, HandleBudgetExceeded`


### `event_schema.go`

**Existence**: TCB: 836 LOC, 8 fns | vCreator: 716 LOC, 8 fns | Ambassador: 1169 LOC, 9 fns

**Shared by all 3** (8): `CheckPassSchemaByContentMilestone, CheckPassSchemaByStatistic, CheckPassSchemaByViewMilestone, CheckPassSchemaTypeByViewMilestoneWithListSchema, CheckPassSchemaWithContent, EventSchema, RecheckSchemaWithContentWhenChangeStatus, UpdateRewardTypeByStatisticContent`

**Ambassador-only** (1): `RecoverRecheckInProgress`


### `filtered_campaigns.go`

**Existence**: TCB: 119 LOC, 2 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (2): `FilteredCampaigns, GetFilteredCampaigns`


---

## Financial

### `cashflow.go`

**Existence**: TCB: 140 LOC, 7 fns | vCreator: 147 LOC, 7 fns | Ambassador: 139 LOC, 7 fns

**Shared by all 3** (7): `AddCashFlow, CashFlow, GetOptionsInfo, GetPartnerRemaining, GetRemaining, GetTotalCashTaxRewardByEvent, GetTotalRevenueInMonth`


### `withdraw.go`

**Existence**: TCB: 257 LOC, 2 fns | vCreator: 298 LOC, 2 fns | Ambassador: 298 LOC, 2 fns

**Shared by all 3** (2): `Create, Withdraw`


### `budget.go`

**Existence**: TCB: 172 LOC, 2 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (2): `CheckThresholdByEventID, SendThresholdEmail`


---

## Reconciliation & Audit

### `reconciliation_checklist.go`

**Existence**: TCB: 826 LOC, 13 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (13): `ApplyClassification, ComputeChecklistSummary, ConfirmStatus, EvaluateReconciliation, GetLatestResult, GetLatestResultMap, ManualEvaluateItem, Override, QuickApprove, QuickReject, ReconciliationChecklist, ResetChecklistItem, ValidateStatusFromChecklist`


### `reconciliation_snapshot.go`

**Existence**: TCB: 324 LOC, 6 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (6): `DetectMissingDays, GetLatestSnapshot, GetLatestSnapshotMap, InsertSnapshot, MakeupCrawl, ReconciliationSnapshot`


### `reconciliation_snapshot_job.go`

**Existence**: TCB: 90 LOC, 2 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (2): `ReconciliationSnapshotJob, RunPostExpiryCrawl`


### `audit.go`

**Existence**: TCB: 56 LOC, 3 fns | vCreator: 80 LOC, 4 fns | Ambassador: 56 LOC, 3 fns

**Shared by all 3** (3): `Audit, CreateAudits, CreatePayload`

**vCreator-only** (1): `CreatePayloadWithActorType`


---

## Analytics & Dashboard

### `dashboard_analytics.go`

**Existence**: TCB: 1547 LOC, 12 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (12): `DashboardAnalytics, ExportAnalytics, GetApprovalAnalytics, GetCreatorKPIs, GetCreatorLeaderboard, GetCreatorSegments, GetDashboardKPIs, GetDashboardKPIsWithComparison, GetPlatformBreakdown, GetPlatformBreakdownWithMetrics, GetTimelineTrends, GetTransfers`


### `global_dashboard.go`

**Existence**: TCB: 261 LOC, 2 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (2): `GetGlobalDashboard, GlobalDashboard`


### `rating_aggregation.go`

**Existence**: TCB: 164 LOC, 3 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (3): `GetCachedRating, RatingAggregation, RecalculateProfileRating`


---

## Targeting & Matching

### `segment.go`

**Existence**: TCB: 67 LOC, 2 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (2): `CheckUserInSegmentWithReferralCode, UpdateStatistic`


### `registry_match.go`

**Existence**: TCB: ❌ | vCreator: 391 LOC, 4 fns | Ambassador: ❌

**vCreator-only** (4): `GenerateChanges, LookupSingle, MapMismatchReason, MatchEngine`


### `influencer.go`

**Existence**: TCB: 319 LOC, 3 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (3): `CheckStatusUserSocialFacebook, CheckStatusUserSocialPartner, CheckStatusUserSocialWithConfig`


### `review.go`

**Existence**: TCB: 379 LOC, 5 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (5): `EditReview, GetReview, ListReviews, ReviewService, SubmitReview`


---

## Infrastructure & Misc

### `notification.go`

**Existence**: TCB: 468 LOC, 10 fns | vCreator: 265 LOC, 6 fns | Ambassador: 261 LOC, 6 fns

**Shared by all 3** (6): `GetAppResponse, GetContent, GetNotificationPayload, GetOption, Notification, Push`

**TCB-only** (4): `NotifyReviewSubmitted, SendNotificationAndEmailBudgetToAllUserInEvent, SendNotificationInfluencerChangeStatus, SendRatingReminders`


### `check_rate_limit.go`

**Existence**: TCB: 98 LOC, 2 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (2): `CheckRateLimitAuthExchange, CheckRateLimitRequestOTP`


### `tracking_request_crawl.go`

**Existence**: TCB: 42 LOC, 1 fns | vCreator: ❌ | Ambassador: ❌

**TCB-only** (1): `InsertTrackingRequestCrawl`


### `load_data.go`

**Existence**: TCB: 26 LOC, 2 fns | vCreator: ❌ | Ambassador: 26 LOC, 2 fns

**Ambassador+TCB only** (2): `GetDataDemographic, LoadDataDemographic`


### `staff.go`

**Existence**: TCB: ❌ | vCreator: 51 LOC, 2 fns | Ambassador: ❌

**vCreator-only** (2): `GetRoot, Staff`


### `affiliate.go`

**Existence**: TCB: ❌ | vCreator: ❌ | Ambassador: 361 LOC, 16 fns

**Ambassador-only** (16): `Affiliate, CreateCampaign, GenerateLink, GetAffiliateCampaignsByEvent, GetCampaign, GetContract, GetMappingsByCampaign, GetMappingsByEvent, GetUserContracts, GetUserLinks, JoinCampaign, LinkCampaignToEvent, ListCampaigns, UnlinkCampaignFromEvent, UpdateCampaign, UpdateCampaignStatus`


---

## Summary by group

| Group | TCB total LOC | vCreator total LOC | Ambassador total LOC |
|---|---:|---:|---:|
| User & Auth | 1,316 | 650 | 1,006 |
| Content & Media | 1,433 | 1,323 | 1,376 |
| Campaign & Event | 2,381 | 1,780 | 2,673 |
| Financial | 569 | 445 | 437 |
| Reconciliation & Audit | 1,296 | 80 | 56 |
| Analytics & Dashboard | 1,972 | 0 | 0 |
| Targeting & Matching | 765 | 391 | 0 |
| Infrastructure & Misc | 634 | 316 | 648 |

**Grand total**: TCB 10,366 LOC | vCreator 4,985 LOC | Ambassador 6,196 LOC