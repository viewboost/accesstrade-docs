# Đổi mật khẩu

# **🔐 Hướng Dẫn Admin: Quản Lý & Hỗ Trợ Password Management**

## **Techcombank Dashboard - Staff Invite & Auth**

**Phiên bản:** 1.0 **Ngày:** Tháng 2/2026 **Đối tượng:** Admin Team **Nguồn:** PRD Staff Invite Auth

---

## **🎯 TỔNG QUAN TÍNH NĂNG**

### **Hai Flows Chính**

```
┌─────────────────────────────────────────────────────────┐
│ FORGOT PASSWORD (Quên mật khẩu)                        │
│                                                         │
│ User: Nhập email → Nhận email reset → Reset password  │
│ Admin: Monitor rate limit, support nếu cần             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ CHANGE PASSWORD (Đổi mật khẩu)                        │
│                                                         │
│ User: Login → Settings → Security → Đổi password      │
│ Admin: Monitor activities, enforce policies             │
└─────────────────────────────────────────────────────────┘
```

---

## **🔑 QUẢN LÝ FORGOT PASSWORD FLOW**

### **Thao Tác 1: Hiểu Forgot Password Process**

**Định Nghĩa:** Tính năng cho phép staff quên mật khẩu có thể reset lại mà không cần admin intervention

### **Bước 1: User Trigger Forgot Password**

```
User Actions:
1. Click "Quên mật khẩu?" link on login page
2. Redirect to: /forgot-password
3. Enter email: staff@techcombank.com
4. Click "Gửi hướng dẫn"

System Response:
├─ Always shows: "If email exists, you'll receive instructions"
│  (même cho email không tồn tại - prevent enumeration)
├─ Email sent (if account is ACTIVE)
├─ Link expires in: 1 hour
└─ User sees success message regardless
```

### **Bước 2: Email Content**

```
Email được gửi về:

From: noreply@techcombank-dashboard.com
To: staff@techcombank.com
Subject: [Techcombank] Yêu cầu đặt lại mật khẩu

Body:
┌────────────────────────────────────┐
│ Xin chào [Staff Name],              │
│                                    │
│ Chúng tôi nhận được yêu cầu đặt   │
│ lại mật khẩu của bạn.             │
│                                    │
│ [BUTTON: Đặt lại mật khẩu]        │
│ (Link: /reset-password?token=xxx)  │
│                                    │
│ ⚠️ Link sẽ hết hạn sau 1 giờ      │
│                                    │
│ Nếu bạn không yêu cầu này, vui    │
│ lòng bỏ qua email.                │
│                                    │
│ © Techcombank 2026                 │
└────────────────────────────────────┘

Language: Vietnamese
Delivery Time: Within 60 seconds
Token Validity: 1 hour only
Single Use: Token deleted after use
```

### **Bước 3: Admin Monitoring**

```bash
Admin Dashboard → Password Management → Forgot Password Log

Xem các metrics:
├─ Total requests (hôm nay): 45
├─ Successful sends: 43
├─ Failed sends: 2 (invalid email)
├─ Tokens expired (not used): 12
├─ Tokens consumed: 31

Rate Limit Status:
├─ staff1@techcombank.com: 1/3 attempts (normal)
├─ staff2@techcombank.com: 3/3 attempts (LIMIT REACHED)
└─ staff3@techcombank.com: 2/3 attempts (warning)
```

---

### **Thao Tác 2: Monitor Rate Limiting**

**Mục tiêu:** Phát hiện abuse, prevent brute force attacks

### **Rate Limit Rules**

```
Maximum: 3 requests per email per hour

Timeline:
├─ 09:00 - Request 1 ✅
├─ 09:15 - Request 2 ✅
├─ 09:45 - Request 3 ✅
├─ 10:15 - Request 4 ❌ ERROR: "Too many attempts"
├─ 10:30 - Request 5 ❌ ERROR: "Too many attempts"
│
└─ 10:00 (next hour) → Counter resets
   ├─ 10:05 - Request 4 ✅ (new hour)
   └─ Limit counter: 1/3
```

### **Cách Monitor Rate Limiting**

```bash
# Step 1: Vào Admin Panel → Security → Rate Limits
Admin Dashboard
├─ Menu: Security Management
├─ Tab: Rate Limiting Status
└─ Filter by: Forgot Password

# Step 2: Xem real-time violations
Current Hour Rate Limiting:
┌─────────────────────────────────────────────┐
│ Email                  │ Attempts │ Status  │
├─────────────────────────────────────────────┤
│ staff1@techcombank.com │   1/3    │ ✅ OK  │
│ staff2@techcombank.com │   2/3    │ ⚠️ Caution │
│ attacker@test.com      │   3/3    │ 🔴 BLOCKED │
│ hacker2@test.com       │   3/3    │ 🔴 BLOCKED │
└─────────────────────────────────────────────┘

# Step 3: Action nếu phát hiện attack
├─ Alert: Multiple failed attempts from attacker@test.com
├─ Action: Monitor this email
├─ Result: Auto-blocked until 11:00
└─ Report: Log security incident
```

### **Red Flags & Actions**

```
🚨 RED FLAG: Same email 3+ attempts in short time
Action:
├─ Check if legitimate user (stuck with forgotten password)
├─ If legitimate: Offer direct password reset via admin
├─ If suspicious: Monitor for next hour
└─ Log incident

🚨 RED FLAG: Multiple different emails from same IP
Action:
├─ Possible credential enumeration attack
├─ Check server logs for IP address
├─ Consider IP-level rate limiting
└─ Alert security team

✅ NORMAL: 1-2 requests per user per week
Action:
├─ No action needed
└─ Continue monitoring
```

---

### **Thao Tác 3: Support Staff Forgot Password**

**Scenario:** Staff không nhận được reset email hoặc link hết hạn

### **Support Steps**

```
Staff Reports: "Tôi không nhận được email reset"

Step 1: Verify Account Status
├─ Check in: Admin Dashboard → Staff Management
├─ Find: staff@techcombank.com
├─ Verify: Account status = ACTIVE
├─ Verify: Email field = Correct & not empty
└─ Action: If status ≠ ACTIVE, activate account first

Step 2: Check Rate Limit
├─ Go to: Security → Rate Limit Status
├─ Find: This email
├─ Check: How many attempts in last hour
├─ If 3+: Tell user to wait until next hour
└─ If < 3: Proceed to manual reset

Step 3: Manual Password Reset (Admin Action)
├─ Admin can directly reset password for user
├─ Go to: Staff Management → Find staff
├─ Click: "Reset Password" button (admin only)
├─ Generate: New temporary password
├─ Send: Via secure channel to staff
└─ Note: This invalidates ALL sessions (not like user change)

Step 4: Notify Staff
├─ Email/SMS: New temporary password
├─ Message: "Use this to login, then change password in Settings"
├─ Remind: Change password after first login
└─ Note: Login will require Settings → Security → Change Password
```

---

## **🔐 QUẢN LÝ RESET PASSWORD FLOW**

### **Thao Tác 4: Hiểu Reset Password Mechanics**

**Định Nghĩa:** Người dùng truy cập `/reset-password?token=xxx` để set mật khẩu mới

### **Token Mechanics**

```
Token Lifecycle:

1. GENERATION (Lúc user request forgot password)
   ├─ System generates: 32-byte random (crypto/rand)
   ├─ Encode: Base64url format
   ├─ Hash: bcrypt trước khi lưu DB (never plaintext)
   └─ Store: hashed_token in database

2. EMAIL DELIVERY
   ├─ Raw token sent in email link
   ├─ NOT hashed version in email
   ├─ Link format: /reset-password?token=[raw-token]
   ├─ Validity: 1 hour from generation
   └─ Delivery: HTTPS only, no logging of raw tokens

3. USAGE (User clicks link)
   ├─ User enters new password
   ├─ System hashes raw token from URL
   ├─ Compare: hashed(token_from_url) == stored_hash
   ├─ If match: Allow password change
   └─ If no match: Show error "Invalid/Expired link"

4. CONSUMPTION (Token is used)
   ├─ After successful use: Token deleted
   ├─ Cannot be reused (single-use enforcement)
   ├─ Replay attack prevention: Token gone
   └─ User must request new link if needed
```

### **Expiry Logic**

```
Token Generation Time: 09:00:00
Expiry Time: 10:00:00 (1 hour later)

Timeline:
├─ 09:15:00 - User clicks link ✅ Valid
├─ 09:45:00 - User clicks link ✅ Valid
├─ 09:59:59 - User clicks link ✅ Valid (1 second before expiry)
├─ 10:00:00 - User clicks link ❌ Expired
├─ 10:00:01 - User clicks link ❌ Expired
└─ Expired message: "Link has expired. Request new link."
```

---

### **Thao Tác 5: Monitor Password Resets**

```bash
Admin Dashboard → Password Management → Reset History

Current Status:
├─ Successful resets today: 23
├─ Failed attempts: 5
├─ Expired tokens: 12
├─ In-progress resets: 2

Last 10 Resets:
┌──────────────────────────────────────────────────────┐
│ Email            │ Requested │ Reset? │ Session Kill? │
├──────────────────────────────────────────────────────┤
│ staff1@bank.com  │ 10:30     │ ✅ Yes │ ✅ Yes       │
│ staff2@bank.com  │ 10:25     │ ✅ Yes │ ✅ Yes       │
│ staff3@bank.com  │ 10:15     │ ⏳ No  │ -            │
│ staff4@bank.com  │ 10:10     │ ❌ Failed │ -         │
│ (invalid)@test   │ 10:05     │ ❌ Failed │ -         │
└──────────────────────────────────────────────────────┘

Filters:
├─ Date range
├─ Email
├─ Status (Completed/Failed/Pending)
└─ Session invalidation confirmed
```

---

### **Thao Tác 6: Understand Session Invalidation After Reset**

**Critical Behavior:** Khi user reset password qua forgot-password flow, ALL sessions invalidated

### **What Happens**

```
BEFORE Reset:
├─ Device A (Laptop): Logged in ✅
├─ Device B (Mobile): Logged in ✅
├─ Device C (Tablet): Logged in ✅

USER CLICKS RESET LINK → Changes password

AFTER Reset:
├─ Device A: Session destroyed, redirected to login ❌
├─ Device B: API requests return 401 Unauthorized ❌
├─ Device C: Session expired, must re-login ❌

Required:
└─ All devices must re-authenticate with new password
```

### **Why This Matters**

```
Security Purpose:
├─ If attacker has password, they can't use old sessions
├─ Invalidating all sessions forces re-auth
├─ Prevents simultaneous attacker & legitimate access
└─ Forces password update to be "immediate" & "global"

Admin Perspective:
├─ This is EXPECTED behavior for forgot-password
├─ This is DIFFERENT from user-initiated change password
│  (which keeps user logged in)
└─ Tell staff: They need to login again after reset
```

---

## **⚙️ QUẢN LÝ CHANGE PASSWORD FLOW**

### **Thao Tác 7: Hiểu Change Password**

**Định Nghĩa:** Authenticated user tự đổi mật khẩu từ Settings → Security

### **Access & Location**

```
User navigates to:
├─ Dashboard → Click user profile menu
├─ Select: "Cài đặt" (Settings)
├─ Click: "Bảo mật" (Security)
└─ Find: "Đổi mật khẩu" button

Access Control:
├─ ONLY logged-in users can access
├─ No email links needed
├─ No token required
└─ Current password = verification method
```

### **Form & Validation**

```
┌─────────────────────────────────────────────────────┐
│ CHANGE PASSWORD FORM                                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Mật khẩu hiện tại *                                │
│ [________________] (must be correct)               │
│                                                     │
│ Mật khẩu mới *                                      │
│ [________________] (min 8 characters)              │
│ ✓ Ít nhất 8 ký tự                                  │
│                                                     │
│ Xác nhận mật khẩu mới *                            │
│ [________________] (must match)                    │
│                                                     │
│ [BUTTON: Thay đổi mật khẩu]                        │
│                                                     │
└─────────────────────────────────────────────────────┘

Validation Rules:
├─ Current password must match (no typos allowed)
├─ New password: minimum 8 characters
├─ New & confirm must match exactly
└─ Cannot be same as current password
```

### **Key Difference: Session Behavior**

```
FORGOT PASSWORD (Reset via email) → All sessions killed
CHANGE PASSWORD (From Settings) → Current session STAYS ACTIVE ✅

Why the difference?
├─ Reset: User lost access, device might be compromised
│  → Need to force re-auth everywhere
│
├─ Change: User actively in Settings, intentional action
│  → No need to kick them out (good UX)
│  → But if they logout, they must re-login with new password
│
└─ Admin perspective: This is EXPECTED behavior

Example:
User on Laptop, clicks Change Password:
├─ Enters old & new password
├─ Password updated ✅
├─ Laptop session continues ✅
├─ User NOT kicked out
├─ But Mobile session: Next API call = 401 & re-login needed
│  (Because password hash changed in database)
└─ Different from Reset, where mobile also kicked out immediately
```

---

### **Thao Tác 8: Monitor Password Changes**

```bash
Admin Dashboard → User Activity → Password Changes

Filter Options:
├─ Date range
├─ User/email
├─ Department
└─ Status (Success/Failed/Attempted)

Log Entries:
┌──────────────────────────────────────────────────┐
│ User              │ Time    │ Action  │ Status  │
├──────────────────────────────────────────────────┤
│ staff1@bank.com   │ 10:30   │ Change  │ ✅ Success │
│ staff2@bank.com   │ 10:25   │ Change  │ ✅ Success │
│ staff3@bank.com   │ 10:20   │ Reset   │ ✅ Success │
│ hacker@test.com   │ 10:15   │ Change  │ ❌ Failed (wrong pwd) │
│ hacker@test.com   │ 10:10   │ Change  │ ❌ Failed (wrong pwd) │
└──────────────────────────────────────────────────┘

Red Flags:
├─ Multiple failed attempts (same user) → Brute force?
├─ Password changes at odd hours → Suspicious?
└─ Review & investigate as needed
```

---

## **👨‍💼 ADMIN SUPPORT OPERATIONS**

### **Thao Tác 9: Admin Can Directly Reset User Password**

**Scenario:** User forgot password & can't access account. Admin helps directly.

### **Admin Reset Steps**

```
Step 1: Access Admin Panel
├─ Go to: Admin Dashboard
├─ Menu: Staff Management / User Management
├─ Find: User account to reset
└─ Click: User profile

Step 2: Find Reset Option
├─ Look for: "Security Actions" or "Password Management"
├─ Button: "Reset Password" or "Force Password Reset"
├─ Click: This option
└─ Confirmation: "Are you sure? This will invalidate all sessions."

Step 3: Generate Temporary Password
├─ System generates: Random 12-character password
│  (Example: Temp-2026-0225)
├─ Show in: Popup or modal
├─ Copy: Admin copies password
└─ Warning: Password shown only once (not retrievable)

Step 4: Communicate to User
├─ Send via: Secure channel (WhatsApp Business, SMS, etc.)
├─ Message template:
│  "Your temporary password is: [TEMP_PASSWORD]
│   Please login and change it immediately in Settings > Security"
│
├─ DO NOT: Send via email (might be intercepted)
├─ DO NOT: Send via unencrypted channels
└─ VERIFY: User confirmed receipt

Step 5: User Login & Change Password
├─ User: Logs in with temporary password
├─ Dashboard: Forces redirect to Settings > Security
│  OR: Shows banner "Please change your password"
├─ User: Sets own permanent password
├─ Result: Password changed, can use dashboard normally
└─ Sessions: ALL invalidated (like forgot-password flow)

Step 6: Verify Success
├─ Admin: Checks user can login with new password
├─ Confirm: In staff management: "Last password change" timestamp updated
└─ Document: Log this admin action for audit trail
```

---

### **Thao Tác 10: Handle Locked Accounts**

**Scenario:** User locked out due to too many failed login attempts

### **Unlock Steps**

```
User Locked Out:
├─ Caused by: 5+ wrong password attempts in 15 minutes
├─ Message shown: "Account locked. Try again in 15 minutes."
└─ Duration: 15-minute cooldown

Admin Options:

Option A: Wait 15 Minutes
├─ User: Wait until 15-min window passes
├─ System: Auto-unlock
└─ Best for: Non-urgent cases

Option B: Admin Force Unlock
├─ Admin Dashboard → User Management
├─ Find: Locked account
├─ Click: "Unlock Account" button
├─ Confirm: Action logged for audit
└─ User: Can immediately retry login

Option C: Admin Reset Password (Recommended)
├─ Same as above steps
├─ Send temporary password
├─ User: Can login & change password
└─ More secure than just unlocking
```

---

## **🔒 SECURITY MANAGEMENT**

### **Thao Tác 11: Password Policy Enforcement**

**Current Policy (từ PRD):**

```
Requirement                    │ Status │ Notes
─────────────────────────────────────────────────────
Minimum 8 characters          │ ✅ YES │ Enforced in validation
Complexity (upper+lower+num)  │ ❓ OPEN │ Not yet specified
Special characters required   │ ❓ OPEN │ Not yet specified
Password history (prevent reuse) │ ❓ OPEN │ Not yet specified
Expiration (force change periodically) │ ❓ OPEN │ Not yet specified

Admin Can:
├─ Monitor password changes
├─ Enforce minimum length
├─ Review weak password attempts
└─ Document password policy in system
```

### **Recommend Enhancement**

```
Admin Recommendation:
├─ Add complexity requirement (upper + lower + number)
│  Examples:
│  ❌ "password" (no numbers, same case)
│  ❌ "password123" (no upper case)
│  ✅ "Password123" (mixed case + number)
│
├─ Add password history (prevent reuse)
│  → User cannot reuse last 3 passwords
│  → Prevent: User changes password twice, then changes back
│
├─ Optional: Set expiration policy
│  → Force change every 90 days
│  → But: Only if security risk assessment warrants
│
└─ Document: In staff onboarding & security policy
```

---

### **Thao Tác 12: Token Security Audit**

**Ensure tokens are handled securely:**

```
✅ VERIFY: Token Generation
├─ Tokens generated with: crypto/rand (32 bytes)
├─ Encoding: Base64url (URL-safe)
└─ Check: No predictable patterns

✅ VERIFY: Token Storage
├─ Never stored in plaintext ❌ WRONG
├─ Always hashed with bcrypt ✅ CORRECT
├─ Database query: SELECT * FROM reset_tokens
│  → Should show: id, user_id, hashed_token, expires_at
│  → Should NOT show: raw token
└─ Check: Logs never contain raw tokens

✅ VERIFY: Token in Email
├─ Email contains: Raw token in URL (safe, will be deleted after use)
├─ NOT hashed in email (user needs to send to server)
└─ HTTPS only (not HTTP)

✅ VERIFY: Single-Use Enforcement
├─ After successful use: Token deleted from database
├─ Replay attempt: No matching token found → Error
├─ Check database: Old tokens should be gone
└─ Verify: Cannot use same token twice

✅ VERIFY: Rate Limiting
├─ Forgot password: max 3/email/hour
├─ Check: HTTP 429 when exceeded
└─ Test: Try 4th request → Should be blocked
```

---

## **📊 MONITORING & LOGGING**

### **Thao Tác 13: Set Up Monitoring**

**What to Monitor:**

```
┌─────────────────────────────────────────────────────┐
│ REAL-TIME MONITORING DASHBOARD                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Password Reset Requests (Last 24 hours)             │
│ ├─ Successful: 156 ✅                              │
│ ├─ Failed: 8 ❌                                     │
│ ├─ Expired (not used): 23                           │
│ └─ In-progress: 2                                   │
│                                                     │
│ Password Change Requests (Last 24 hours)            │
│ ├─ Successful: 342 ✅                              │
│ ├─ Failed (wrong password): 5 ❌                    │
│ └─ Failed (mismatch): 3 ❌                          │
│                                                     │
│ Rate Limiting Status                                │
│ ├─ Emails blocked this hour: 0 ✅                  │
│ ├─ At limit (3/3): 0                               │
│ └─ Near limit (2/3): 2                             │
│                                                     │
│ Account Locks (Last 24 hours)                       │
│ ├─ Locked (due to 5 failed attempts): 3             │
│ ├─ Unlocked by admin: 1                            │
│ └─ Auto-unlocked after timeout: 2                  │
│                                                     │
│ Security Incidents                                  │
│ ├─ Suspicious patterns: 0                          │
│ ├─ IP-based attacks: 0                             │
│ └─ Token abuse attempts: 0                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

###