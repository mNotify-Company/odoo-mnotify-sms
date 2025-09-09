# sms_mnotify/models/sms_sms.py
import json
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    def _find_suitable_gateway(self, number):
        """Find the most suitable gateway for the given number"""
        gateways = self.env['sms.gateway'].search([('active', '=', True)], order='sequence')
        
        # Clean number for comparison
        clean_number = ''.join(filter(str.isdigit, str(number)))
        
        # Try to find a gateway with matching country prefix
        for gateway in gateways:
            if gateway.country_prefix:
                # Remove + and any spaces from prefix
                prefix = gateway.country_prefix.replace('+', '').replace(' ', '')
                if clean_number.startswith(prefix):
                    return gateway
        
        # If no prefix match, return the first active gateway
        return gateways[0] if gateways else None

    def _prepare_mnotify_payload(self, gateway):
        """Prepare the payload for mNotify API"""
        # Get the phone number from the SMS record
        number = self.number
        message = self.body
        
        # Clean and format phone number
        clean_number = ''.join(filter(str.isdigit, str(number)))
        
        # Add country code if not present (assuming Ghana +233)
        if len(clean_number) == 9 and not clean_number.startswith('233'):
            clean_number = '233' + clean_number
        elif len(clean_number) == 10 and clean_number.startswith('0'):
            clean_number = '233' + clean_number[1:]
        
        return {
            'recipient': [clean_number],
            'sender': gateway.sender_id or 'mNotify',
            'message': message,
            'is_schedule': False,
            'schedule_date': '',
        }

    def _send_sms_mnotify(self, gateway):
        """Send SMS through mNotify API"""
        if not gateway.api_key:
            raise UserError(_('mNotify API key is not configured for gateway: %s') % gateway.name)
            
        url = f"https://api.mnotify.com/api/sms/quick?key={gateway.api_key}"
        payload = self._prepare_mnotify_payload(gateway)
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        try:
            _logger.info(f"Sending SMS via mNotify to {self.number}")
            
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
                _logger.info(f"SMS sent successfully via mNotify: {result}")
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
            _logger.error(f"Network error while sending SMS via mNotify: {str(e)}")
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
            _logger.error(f"Unexpected error while sending SMS via mNotify: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'response': None
            }

    def _send(self, unlink_failed=True, unlink_sent=True, auto_commit=False, raise_exception=False):
        """Override the base send method to use mNotify when configured"""
        
        # DEBUG: Always log this  
        _logger.info("=== mNotify _send() method called ===")
        print("MNOTIFY DEBUG: _send method called!")  # This will show in server logs
        
        # Check if mNotify integration is enabled
        use_mnotify = self.env['ir.config_parameter'].sudo().get_param('sms_mnotify.use_mnotify', False)
        _logger.info(f"=== mNotify enabled: {use_mnotify} ===")
        
        if use_mnotify:
            mnotify_sent = self.env['sms.sms']
            
            for sms in self:
                if sms.state != 'outgoing':
                    continue
                    
                try:
                    # Find suitable gateway
                    gateway = sms._find_suitable_gateway(sms.number)
                    _logger.info(f"Found gateway: {gateway.name if gateway else 'None'}")
                    
                    if gateway and gateway.provider == 'mnotify' and gateway.api_key:
                        result = sms._send_sms_mnotify(gateway)
                        
                        if result['success']:
                            sms.sudo().write({
                                'state': 'sent',
                            })
                            mnotify_sent |= sms
                            _logger.info(f"SMS {sms.id} sent successfully via mNotify")
                            continue
                        else:
                            _logger.warning(f"mNotify SMS failed for {sms.id}: {result['error']}")
                            # Will fall back to default method below
                    else:
                        if gateway and not gateway.api_key:
                            _logger.warning(f"mNotify gateway {gateway.name} has no API key configured, falling back to IAP")
                        # Will fall back to default method below
                            
                except Exception as e:
                    _logger.warning(f"mNotify SMS failed for {sms.id} with exception: {str(e)}")
            
            remaining_sms = self - mnotify_sent
            
            if remaining_sms:
                
                return super(SmsSms, remaining_sms)._send(
                    unlink_failed=unlink_failed, 
                    unlink_sent=unlink_sent, 
                    raise_exception=raise_exception
                )
            
            return mnotify_sent
        
        
        return super()._send(
            unlink_failed=unlink_failed, 
            unlink_sent=unlink_sent, 
            raise_exception=raise_exception
        )