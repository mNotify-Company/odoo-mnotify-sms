from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_mnotify = fields.Boolean(
        string='Use mNotify SMS Gateway',
        config_parameter='sms_mnotify.use_mnotify',
        help='Enable mNotify SMS gateway instead of default IAP SMS'
    )
    
    mnotify_gateway_count = fields.Integer(
        string='mNotify Gateways',
        compute='_compute_mnotify_gateway_count'
    )

    @api.depends()
    def _compute_mnotify_gateway_count(self):
        for record in self:
            record.mnotify_gateway_count = self.env['sms.gateway'].search_count([('provider', '=', 'mnotify')])

    def action_open_sms_gateways(self):
        """Open SMS gateways configuration"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('SMS Gateways'),
            'res_model': 'sms.gateway',
            'view_mode': 'tree,form',
            'domain': [('provider', '=', 'mnotify')],
            'context': {'default_provider': 'mnotify'},
        }