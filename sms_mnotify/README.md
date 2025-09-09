# mNotify SMS Provider for Odoo 17

Send SMS messages from Odoo using your mNotify account instead of expensive IAP credits.

## Why Use This Module?

- **Works everywhere** - Integrates with all Odoo SMS features (Marketing, Notifications, Contacts)
- **Reliable** - Automatically falls back to IAP if mNotify fails
- **Easy setup** - Simple 3-step configuration

## Installation

1. Install the module from Odoo Apps
2. Go to **Settings → mNotify SMS** (You will find it on the top bar)
3. Follow the configuration steps below

## Quick Setup

### Step 1: Configure Your Gateway
1. Edit the "mNotify SMS" gateway (or create a new one)
2. Fill in these fields:
   - **API Key**: Get this from your mNotify dashboard
   - **Sender ID**: Your preferred sender name (e.g., "YourCompany")
   - **Country Prefix**: "+233" for Ghana (optional)
   - **Test Number**: Your phone number for testing (e.g., +2332********)
   - **Active**: Check this box to enable the gateway

### Step 2: Test Your Setup
1. Click **"Test Gateway"** button
2. Check your phone for the test SMS
3. If you receive it, you're ready to go!

### Step 3: Enable mNotify
1. Go to **Settings → Technical → System Parameters**
2. Create a new parameter:
   - **Key**: `sms_mnotify.use_mnotify`
   - **Value**: `True`
3. Save

That's it! All SMS from Odoo will now use your mNotify account.

## How to Get mNotify API Key

1. Sign up at [mNotify.com](https://bms.mnotify.com/developer/api_v2)
2. Go to your dashboard
3. Find "API Key" section
4. Copy your API key
5. Paste it in the gateway configuration

## Troubleshooting

**SMS still using IAP credits?**
- Check that Step 3 is completed (system parameter set to True)
- Verify your gateway is Active
- Check your API key is correct

**Test gateway fails?**
- Verify your mNotify account has sufficient balance
- Check to make sure your API key is enabled after creating
- Ensure test number includes country code (+233XXXXXXXXX)

**Need help?**
- Check **Settings → Technical → Logging** for error messages
- Contact your system administrator

## Phone Number Support

The module automatically formats Ghana phone numbers:
- `0541509394` becomes `233541509394`
- `+233541509394` stays the same
- Works with various input formats

## Multiple Countries

You can set up different gateways for different countries:
1. Create separate gateways
2. Set different country prefixes (+233, +234, etc.)
3. The module automatically selects the right gateway

## Requirements

- Odoo 17.0+
- mNotify account with API access
- Internet connection

## License

LGPL-3 License