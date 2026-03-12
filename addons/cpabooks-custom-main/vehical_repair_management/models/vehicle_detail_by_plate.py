from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError

class VehicleByPlate(models.Model):
    _name = "vehicle.detail.by.plate"
    _rec_name = "plate_no"

    plate_no = fields.Char(string='Plate No')
    customer_id = fields.Many2one('res.partner', 'Customer')
    phone = fields.Char(string='Phone', related="customer_id.phone", readonly=False)
    email = fields.Char(string="Email", related="customer_id.email", readonly=False)
    vehicle_type_id = fields.Many2one("vehicle.vehicle.type", ondelete="restrict")
    brand_id = fields.Many2one("vehicle.brand", ondelete="restrict")
    model = fields.Char(string='Model')
    color = fields.Char(string='Color')
    transmission_type = fields.Selection([("auto", "Automatic"), ("manual", "Manual")])
    fuel_type_id = fields.Many2one('fuel.type', string='Fuel Type', ondelete="restrict")
    year_of_manufacturing = fields.Char(string="Year of Manufacturing")
    vin_no = fields.Char('VIN No')
    vehicle_src_id = fields.Many2one('vehicle.src', 'Vehicle Source')
    cat_id = fields.Many2one('vehicle.cat')

    def name_get(self):
        result = []
        for rec in self:
            # Case 1: Both vehicle_src_id and cat_id are present
            if rec.vehicle_src_id and rec.cat_id:
                result.append((rec.id, '%s - %s - %s' % (rec.vehicle_src_id.name, rec.plate_no, rec.cat_id.name)))

            # Case 2: Only vehicle_src_id is present
            elif rec.vehicle_src_id and not rec.cat_id:
                result.append((rec.id, '%s - %s' % (rec.vehicle_src_id.name, rec.plate_no)))

            # Case 3: Only cat_id is present
            elif rec.cat_id and not rec.vehicle_src_id:
                result.append((rec.id, '%s - %s' % (rec.plate_no, rec.cat_id.name)))

            # Case 4: Neither vehicle_src_id nor cat_id are present
            else:
                result.append((rec.id, '%s' % (rec.plate_no)))

        return result

    @api.model
    def create(self, vals_list):
        res = super(VehicleByPlate, self).create(vals_list)
        if res.customer_id and res not in res.customer_id.vehicle_ids:
            res.cusomer_id.write({
                'vehicle_ids': [(6,0,res)]
            })
        return res


    # @api.onchange("plate_no")
    # def fetch_details_by_plate(self):
    #     if self.plate_no:
    #         plate_no = self.plate_no.replace(" ", "")
    #         self.plate_no = plate_no.upper()


class VehicleSource(models.Model):
    _name = 'vehicle.src'
    _description = 'Vehicle Source'

    name = fields.Char('Name')

class VehicleCat(models.Model):
    _name = 'vehicle.cat'
    _description = 'Vehicle Category'

    name = fields.Char('Name')