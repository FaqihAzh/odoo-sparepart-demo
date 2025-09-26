from odoo import models, fields, api

class InstallationChecklist(models.Model):
    _name = "installation.checklist"
    _description = "Installation checklist line for FSM order"

    fsm_order_id = fields.Many2one('fsm.order', string='FSM Order', ondelete='cascade')
    name = fields.Char(string='Checklist Item', required=True)
    is_done = fields.Boolean(string='Done', default=False)
    done_by = fields.Many2one('res.users', string='Done By')
    done_date = fields.Datetime(string='Done Date', default=False)

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        # set done_date if is_done
        if rec.is_done and not rec.done_date:
            rec.sudo().write({'done_date': fields.Datetime.now()})
        return rec

    def write(self, vals):
        res = super().write(vals)
        if 'is_done' in vals:
            for r in self:
                if r.is_done and not r.done_date:
                    r.sudo().write({'done_date': fields.Datetime.now()})
        return res
