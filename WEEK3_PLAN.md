# Week 3 Implementation Plan: API Endpoints & Celery Tasks

## Overview
Week 3 focuses on building the API layer and implementing Celery background tasks to connect the database models (Week 1) with the services (Week 2).

**Goal**: Enable users to create, manage, and execute scheduled reports via REST API and automated background tasks.

---

## What We'll Build This Week

### 1. **Pydantic Schemas** (Validation & Serialization)
Create type-safe schemas for API request/response validation.

**Files to Create**:
- `backend/app/schemas/scheduled_report.py`
- `backend/app/schemas/email_config.py`
- `backend/app/schemas/alert.py` (basic structure for future)

**Schemas Needed**:

#### ScheduledReport Schemas:
```python
# Request schemas
- ScheduleConfigSchema: Validate schedule configuration
  - type: 'daily' | 'weekly' | 'monthly'
  - time: 'HH:MM' (24-hour format)
  - day_of_week: Optional[0-6]
  - day_of_month: Optional[1-31]

- ScheduledReportCreate:
  - name: str (required)
  - description: Optional[str]
  - dashboard_id: Optional[UUID]
  - saved_query_id: Optional[UUID]
  - schedule_config: ScheduleConfigSchema
  - recipients: List[EmailStr] (validated emails)
  - formats: List['excel' | 'csv' | 'pdf' | 'html']
  - email_subject: Optional[str]
  - email_body: Optional[str]
  - is_active: bool = True

  Validators:
  - Exactly one of dashboard_id or saved_query_id must be set
  - At least 1 recipient required
  - At least 1 format required
  - Valid schedule configuration

- ScheduledReportUpdate:
  - All fields optional
  - Same validators as Create

# Response schemas
- ScheduledReportResponse:
  - All fields from model
  - Include next_run_at, last_run_at
  - Include execution summary (last status, etc.)

- ReportExecutionResponse:
  - Execution history with status, files, timestamps
  - Error messages if failed
```

#### EmailConfiguration Schemas:
```python
- EmailConfigCreate:
  - smtp_host: str
  - smtp_port: int (1-65535)
  - use_tls: bool
  - use_ssl: bool
  - smtp_username: str
  - smtp_password: str (will be encrypted)
  - from_email: EmailStr
  - from_name: Optional[str]

  Validators:
  - Validate port range
  - TLS and SSL cannot both be True
  - Valid email format

- EmailConfigResponse:
  - All fields except smtp_password_encrypted
  - Never return decrypted password

- EmailConfigTest:
  - Test connection request/response
```

**Time Estimate**: 2-3 hours

---

### 2. **API Endpoints** (REST API)
Build FastAPI routers for scheduled reports and email configuration.

**Files to Create**:
- `backend/app/api/scheduled_reports.py`
- `backend/app/api/email_config.py`

**Endpoints to Implement**:

#### `/api/scheduled-reports` Router:
```python
POST   /api/scheduled-reports
  - Create new scheduled report
  - Validate schema
  - Calculate initial next_run_at
  - Return ScheduledReportResponse

GET    /api/scheduled-reports
  - List all user's scheduled reports
  - Filter: is_active (query param)
  - Sort: by next_run_at or created_at
  - Return List[ScheduledReportResponse]

GET    /api/scheduled-reports/{id}
  - Get single report details
  - Include execution history (last 10)
  - Verify ownership
  - Return ScheduledReportResponse

PUT    /api/scheduled-reports/{id}
  - Update existing report
  - Recalculate next_run_at if schedule changed
  - Verify ownership
  - Return ScheduledReportResponse

DELETE /api/scheduled-reports/{id}
  - Delete report (cascade deletes executions)
  - Verify ownership
  - Return 204 No Content

POST   /api/scheduled-reports/{id}/run
  - Manual trigger (run immediately)
  - Enqueue Celery task
  - Return task_id and status

POST   /api/scheduled-reports/{id}/test
  - Test run (send to current user only)
  - Override recipients with current user's email
  - Execute immediately (not via Celery)
  - Return success/failure with details

GET    /api/scheduled-reports/{id}/executions
  - Get execution history
  - Pagination (offset, limit)
  - Filter by status
  - Return List[ReportExecutionResponse]
```

#### `/api/email-config` Router:
```python
GET    /api/email-config
  - Get current user's SMTP config
  - Return EmailConfigResponse or 404

POST   /api/email-config
  - Create or update SMTP config
  - Encrypt password before saving
  - Return EmailConfigResponse

PUT    /api/email-config
  - Update SMTP config
  - Re-encrypt password if changed
  - Return EmailConfigResponse

DELETE /api/email-config
  - Delete SMTP configuration
  - Return 204 No Content

POST   /api/email-config/test
  - Test SMTP connection
  - Send test email to user
  - Return connection status and any errors

GET    /api/email-config/presets
  - Return SMTP presets (Gmail, Outlook, etc.)
  - Public endpoint (no auth required)
```

**Authentication**: All endpoints require JWT authentication (`get_current_user` dependency)

**Time Estimate**: 4-5 hours

---

### 3. **Celery Task Implementation**
Implement the actual background tasks that execute reports.

**Files to Update**:
- `backend/app/tasks/reports.py` (replace stubs with real implementation)

**Tasks to Implement**:

#### `check_and_run_scheduled_reports()` - Periodic Task
```python
@shared_task(bind=True)
def check_and_run_scheduled_reports(self):
    """
    Runs every 5 minutes via Celery Beat.
    Finds reports due to run and spawns execution tasks.
    """
    Implementation:
    1. Create async session
    2. Query ScheduledReport where:
       - is_active = True
       - next_run_at <= now()
       - Within tolerance window (5 minutes)
    3. For each report:
       - Spawn run_scheduled_report_task.delay(report_id)
       - Log: "Enqueued report {name} for execution"
    4. Return count of reports enqueued
```

#### `run_scheduled_report_task(report_id)` - Execution Task
```python
@shared_task(bind=True)
def run_scheduled_report_task(self, scheduled_report_id: str):
    """
    Execute a specific scheduled report.
    This is the main workhorse task.
    """
    Implementation:
    1. Load ScheduledReport from database
    2. Validate it exists and is active
    3. Create ReportExecution record (status='running')

    4. Generate report data:
       - If dashboard_id: Use ReportService.execute_dashboard_queries()
       - If saved_query_id: Use ReportService.execute_saved_query()

    5. Generate files in requested formats:
       - Use ReportService.generate_all_formats()
       - Save to: data/exports/reports/{report_id}/{execution_id}/

    6. Send email:
       - Get user's EmailConfiguration
       - Generate HTML email body (or use custom template)
       - Attach generated files
       - Use EmailService.send_report_email()

    7. Update ReportExecution:
       - status = 'success' or 'failed'
       - generated_files = {format: path}
       - sent_to = recipients
       - execution_time_ms
       - row_count
       - error_message (if failed)

    8. Calculate next run time:
       - Use ScheduleService.calculate_next_run()
       - Update ScheduledReport.next_run_at
       - Update ScheduledReport.last_run_at

    9. Commit to database

    Error Handling:
    - Try/except around each major step
    - Mark execution as 'failed' on error
    - Log error details
    - Still update next_run_at (don't skip next execution)
```

**Error Handling Strategy**:
- Catch exceptions and log them
- Mark execution as failed but don't crash task
- Retry on transient errors (DB connection, etc.)
- Don't retry on validation errors (bad config)

**Time Estimate**: 5-6 hours

---

### 4. **Testing & Validation**
Ensure everything works end-to-end.

**Manual Testing Checklist**:
```
1. Email Configuration:
   ☐ POST /api/email-config (create)
   ☐ GET /api/email-config (retrieve)
   ☐ POST /api/email-config/test (send test email)
   ☐ Verify password is encrypted in database
   ☐ Verify test email received

2. Scheduled Reports:
   ☐ POST /api/scheduled-reports (create daily report)
   ☐ Verify next_run_at calculated correctly
   ☐ GET /api/scheduled-reports (list)
   ☐ GET /api/scheduled-reports/{id} (details)

3. Manual Execution:
   ☐ POST /api/scheduled-reports/{id}/test
   ☐ Verify report generated (Excel, CSV, PDF)
   ☐ Verify email received with attachments
   ☐ Check execution record created

4. Automated Execution:
   ☐ Create report with next_run_at in past
   ☐ Wait for Celery Beat to trigger (max 5 min)
   ☐ Verify task executed
   ☐ Verify email sent
   ☐ Verify next_run_at updated

5. Edge Cases:
   ☐ Invalid schedule config (should fail validation)
   ☐ No recipients (should fail validation)
   ☐ Invalid email format (should fail validation)
   ☐ Dashboard/Query not found (should handle gracefully)
   ☐ SMTP error (should mark execution as failed)
```

**Integration Test Script**:
Create `backend/test_week3_integration.py` to automate testing.

**Time Estimate**: 3-4 hours

---

## Implementation Order

### Day 1: Schemas & Basic Endpoints (6-7 hours)
1. ✅ Create Pydantic schemas
2. ✅ Create email config endpoints
3. ✅ Test email config CRUD
4. ✅ Create scheduled report endpoints (CRUD only)

### Day 2: Manual Execution (5-6 hours)
1. ✅ Implement `/test` endpoint (manual execution)
2. ✅ Test report generation end-to-end
3. ✅ Debug any issues with services
4. ✅ Verify email delivery works

### Day 3: Celery Tasks (5-6 hours)
1. ✅ Implement `run_scheduled_report_task`
2. ✅ Implement `check_and_run_scheduled_reports`
3. ✅ Test background execution
4. ✅ Verify next_run_at updates correctly

### Day 4: Testing & Polish (3-4 hours)
1. ✅ Run full integration tests
2. ✅ Fix any bugs discovered
3. ✅ Add error handling improvements
4. ✅ Document API in OpenAPI/Swagger

**Total Time Estimate**: 19-23 hours (3-4 days)

---

## Files Summary

### Files to Create (7 new files):
1. `backend/app/schemas/scheduled_report.py` (~200 lines)
2. `backend/app/schemas/email_config.py` (~100 lines)
3. `backend/app/api/scheduled_reports.py` (~400 lines)
4. `backend/app/api/email_config.py` (~200 lines)
5. `backend/test_week3_integration.py` (~300 lines)

### Files to Update (2 files):
1. `backend/app/tasks/reports.py` (replace stubs)
2. `backend/app/main.py` (register new routers)

**Total New Code**: ~1,200 lines

---

## Dependencies

**Already Available**:
- ✅ Database models (Week 1)
- ✅ Services (Week 2)
- ✅ Celery configured (Week 1)

**No New Dependencies Required**

---

## Success Criteria

Week 3 is complete when:
- ✅ All API endpoints working (CRUD for reports & email config)
- ✅ Manual execution works (`/test` endpoint)
- ✅ Celery tasks execute reports automatically
- ✅ Reports generate in all formats (Excel, CSV, PDF)
- ✅ Emails deliver with attachments
- ✅ Execution history tracked
- ✅ Next run times calculate correctly
- ✅ Error handling graceful (no crashes)
- ✅ Integration tests pass

---

## API Documentation Preview

Once complete, users will be able to:

**Via Swagger UI (http://localhost:8000/docs)**:

1. Configure SMTP settings
2. Create scheduled reports
3. Test reports immediately
4. View execution history
5. Update/delete reports
6. Trigger manual runs

**Example Request**:
```json
POST /api/scheduled-reports
{
  "name": "Daily Sales Report",
  "description": "Sales summary sent every morning",
  "saved_query_id": "uuid-here",
  "schedule_config": {
    "type": "daily",
    "time": "08:00"
  },
  "recipients": ["manager@company.com", "sales@company.com"],
  "formats": ["excel", "pdf"],
  "email_subject": "Daily Sales Report - {{date}}",
  "email_body": "Please find attached today's sales report.",
  "is_active": true
}
```

**Example Response**:
```json
{
  "id": "uuid",
  "name": "Daily Sales Report",
  "next_run_at": "2026-01-13T08:00:00Z",
  "last_run_at": null,
  "is_active": true,
  "created_at": "2026-01-12T10:30:00Z"
}
```

---

## Risk & Mitigation

**Potential Issues**:
1. **Large reports timeout**: Add task time limits (30 min)
2. **Email server blocks**: Implement retry logic with backoff
3. **File storage fills up**: Add cleanup task (delete old executions)
4. **Concurrent executions**: Add locking mechanism

**Mitigations Built-In**:
- Task timeout: 30 minutes
- Result expiry: 1 hour
- Error logging to database
- Graceful failure handling

---

## Next Steps After Week 3

**Week 4: Frontend UI** (Not part of this week)
- React components for scheduled reports
- Schedule configuration UI
- Execution history viewer
- Email settings page

---

## Questions Before Starting?

1. Should we implement rate limiting? (e.g., max 10 reports per user)
2. Should we add file cleanup? (delete reports older than 30 days)
3. Should we support CC/BCC in emails?
4. Should we add report templates (pre-configured schedules)?

---

**Ready to proceed with Week 3?**

This plan gives us:
- ✅ Complete API layer
- ✅ Working background tasks
- ✅ End-to-end functionality
- ✅ Testable system
- ✅ Foundation for frontend (Week 4+)
