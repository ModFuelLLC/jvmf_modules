# -*- coding: utf-8 -*-
from . import models

# Function should update the data base by pulling user_id(Salesperson)
# from parent_id(company) into individual conact.

def pre_init_salesperson_update(cr):
    cr.execute("""UPDATE res_partner rp1
        SET user_id = rp2.user_id
        FROM res_partner rp2
        WHERE rp1.parent_id = rp2.id;""")
    return True
