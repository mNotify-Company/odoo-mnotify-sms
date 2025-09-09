from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json
import requests
import logging

_logger = logging.getLogger(__name__)


class SmsGateway(models.Model):
    _name = 'sms.gateway'
    _description = 'SMS Gateway Configuration'
    _order = 'sequence, name'

    name = fields.Char(
        string='Gateway Name',
        required=True,
        help='Name of the SMS gateway'
    )
    
    provider = fields.Selection([
        ('mnotify', 'mNotify'),
    ], string='Provider', required=True, default='mnotify')
    
    api_key = fields.Char(
        string='API Key',
        help='Your mNotify API key'
    )
    
    sender_id = fields.Char(
        string='Sender ID',
        required=True,
        default='',
        help='Default sender name/number for SMS messages'
    )
    
    country_prefix = fields.Char(
        string='Country Prefix',
        help='Country code prefix (e.g., +233 for Ghana). Leave empty for global use.',
        placeholder='+233'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Lower sequence number = higher priority'
    )
    
    test_number = fields.Char(
        string='Test Number',
        help='Phone number for testing (including country code)'
    )

    @api.constrains('api_key', 'active')
    def _check_api_key(self):
        """Validate API key when gateway is active"""
        for record in self:
            if record.active and not record.api_key:
                raise UserError(_('API key is required when the gateway is active.'))
            if record.api_key and len(record.api_key) < 10:
                raise UserError(_('API key seems too short. Please check your API key.'))

    def action_test_gateway(self):
        """Test the gateway connection"""
        self.ensure_one()
        if not self.api_key:
            raise UserError(_('Please configure your API key first.'))
        if not self.test_number:
            raise UserError(_('Please configure a test number first.'))
        
        test_message = f'Test message from Odoo mNotify integration at {fields.Datetime.now()}'
        
        try:
            
            result = self._send_test_sms(self.test_number, test_message)
            
            if result.get('success'):
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Test SMS sent successfully!'),
                        'sticky': False,
                        'type': 'success'
                    }
                }
            else:
                raise UserError(_('Test failed: %s') % result.get('error', 'Unknown error'))
                
        except Exception as e:
            raise UserError(_('Test failed: %s') % str(e))

    def _send_test_sms(self, number, message):
        """Send test SMS through mNotify API"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'API key not configured'
            }
            
        # Clean and format phone number
        clean_number = ''.join(filter(str.isdigit, str(number)))
        
        # Add country code if not present (assuming Ghana +233)
        if len(clean_number) == 9 and not clean_number.startswith('233'):
            clean_number = '233' + clean_number
        elif len(clean_number) == 10 and clean_number.startswith('0'):
            clean_number = '233' + clean_number[1:]
        
        # Prepare mNotify payload
        payload = {
            'recipient': [clean_number],
            'sender': self.sender_id or 'mNotify',
            'message': message,
            'is_schedule': False,
            'schedule_date': '',
        }
        
        url = f"https://api.mnotify.com/api/sms/quick?key={self.api_key}"
        headers = {
            'Content-Type': 'application/json',
        }
        
        try:
            _logger.info(f"Sending test SMS via mNotify to {number}")
            
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Check if the API returned success
            if result.get('status') == 'success' or response.status_code == 200:
                _logger.info(f"Test SMS sent successfully via mNotify: {result}")
                return {
                    'success': True,
                    'message_id': result.get('message_id', ''),
                    'response': result
                }
            else:
                error_msg = result.get('message', 'Unknown error occurred')
                _logger.error(f"mNotify API error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'response': result
                }
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"Network error while sending test SMS via mNotify: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'response': None
            }
        except json.JSONDecodeError as e:
            _logger.error(f"Invalid JSON response from mNotify: {str(e)}")
            return {
                'success': False,
                'error': f'Invalid JSON response: {str(e)}',
                'response': None
            }
        except Exception as e:
            _logger.error(f"Unexpected error while sending test SMS via mNotify: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'response': None
            }