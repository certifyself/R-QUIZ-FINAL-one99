# Email Service Setup Guide for SocraQuest

## Current Status
✅ Email invite API endpoint is ready and working
⚠️ Email service provider is NOT configured yet
✅ WhatsApp invite button is fully functional

## Why Emails Aren't Being Sent

The `/api/groups/{group_id}/invite` endpoint currently:
- ✅ Validates the request
- ✅ Checks group membership
- ✅ Prepares invitation details
- ❌ Does NOT send actual emails (no email service configured)

Currently returns:
```json
{
  "success": true,
  "message": "Invitation details prepared (email service not configured)",
  "invite_details": {
    "to": "friend@example.com",
    "group_name": "My Group",
    "group_code": "ABC123",
    "invite_url": "https://socraquest.preview.emergentagent.com/groups/join/ABC123"
  }
}
```

## How to Enable Email Sending

### Option 1: SendGrid (Recommended)
1. Sign up at https://sendgrid.com (Free tier: 100 emails/day)
2. Get API key
3. Use Integration Agent to set up SendGrid
4. Update backend code to use SendGrid API

### Option 2: AWS SES (Amazon Simple Email Service)
1. Sign up for AWS account
2. Verify your domain
3. Get AWS credentials (Access Key, Secret Key)
4. Use Integration Agent for AWS SES setup

### Option 3: Gmail SMTP (Simple, but limited)
1. Enable "Less secure app access" or use App Password
2. Configure SMTP settings in backend
3. Limited to ~500 emails/day

### Option 4: Mailgun, Postmark, or Other Services
Similar process - get API keys and integrate via Integration Agent

## Temporary Solutions (Currently Available)

### ✅ WhatsApp Invite (Working Now!)
- Click "WhatsApp" button on any group
- Opens WhatsApp with pre-filled message
- Contains group name, code, and join link
- Works instantly, no configuration needed

### Manual Group Code Sharing
- Copy group code from group card
- Share via any messaging app
- Friends use "Join Group" feature with code

## To Implement Email Sending

Run this command and ask Integration Agent:
```
"Set up email sending for SocraQuest using SendGrid. 
I need to send group invitations with:
- Recipient email
- Group name and code
- Invite URL
- Custom message from sender"
```

The Integration Agent will:
1. Provide SendGrid setup instructions
2. Generate code for sending emails
3. Show how to test email delivery
4. Configure error handling

## Backend Code Location

File: `/app/backend/server.py`
Endpoint: `POST /api/groups/{group_id}/invite` (line ~1578)

To add email sending, replace the TODO comment with actual email service call.
