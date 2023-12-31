.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License LGPL-3

Purchase Request
================

You use this module if you wish to give notification of requirements of
materials and/or external services and keep track of such requirements.

Requests can be created either directly or indirectly. "Directly" means that
someone from the requesting department enters a purchase request manually.

The person creating the requisition determines what and how much to order,
and the requested date.

"Indirectly" means that the purchase request initiated by the application
automatically, for example, from procurement orders (the module
purchase_request_procurement is also needed for this feature).

A purchase request is an instruction to Purchasing to procure a certain
quantity of materials services, so that they are available at a
certain point in time.

A line of a requisition contains the quantity and requested date of the
material to be supplied or the quantity of the service to be performed. You
can indicate the service specifications if needed.

Usage
=====

Purchase requests are accessible though a new menu entry 'Purchase
Requests', and also from the 'Purchase' menu.

Users can access to the list of Purchase Requests or Purchase Request Lines.

It is possible to filter requests by its approval status.

Bug Tracker
===========

Bugs are tracked in Odoo Helpdesk
<https://www.modfuelwholesasle.com/pages/ticket-home`>_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>
* Jonathan Nemry <jonathan.nemry@acsone.eu>
* Aaron Henriquez <ahenriquez@eficent.com>
* Adrien Peiffer <adrien.peiffer@acsone.eu>
* Lois Rilo <lois.rilo@eficent.com>
* Cristin Meravi <cmeravi@modfuelwholesasle.com>

Maintainer
----------

Modfuel LLC.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
