{
    'name': 'mNotify SMS Gateway',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Cost-effective SMS sending through mNotify instead of expensive IAP credits',
    'description': """
mNotify SMS Provider for Odoo 17

Send SMS messages from Odoo using your mNotify account instead of expensive IAP credits.

Features:
- Cost-effective SMS sending using your own mNotify account
- Multiple gateway support for different countries  
- Automatic gateway selection based on phone number prefix
- Built-in testing functionality
- Automatic fallback to IAP if mNotify fails
- Works with all Odoo SMS features (Marketing, Notifications, Contacts)

Perfect for businesses in Ghana and other regions where mNotify operates.
    """,
    'author': 'mNotify',
    'website': 'https://mnotify.com',
    'license': 'LGPL-3',
    'depends': ['sms'],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/sms_gateway_data.xml',
        'views/sms_gateway_views.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}