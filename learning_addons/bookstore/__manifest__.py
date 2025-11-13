# -*- coding: utf-8 -*-
{
    "name": "Bookstore",
    "version": "1.0",
    "summary": "Bookstore Management System",
    "sequence": 10,
    "description": """
Bookstore Management System
    """,
    "depends": ["product", "mail", "portal", "website"],
    "data": [
        "security/account_security.xml",
        "security/ir.model.access.csv",
        "views/bookstore_author_views.xml",
        "views/bookstore_book_views.xml",
        "views/bookstore_order_views.xml",
        "views/bookstore_menus.xml",
        "views/portal_templates.xml",
        "reports/book_inventory_report.xml",
        "reports/book_sales_report.xml",
        "reports/templates/inventory_report_template.xml",
        "reports/templates/sales_report_template.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bookstore/static/src/css/*.css",
        ],
        "web.assets_frontend": [
            "bookstore/static/src/js/portal_book_order.js",
        ],
    },
    "category": "Management/Bookstore",
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
