# -*- coding: utf-8 -*-
{
    'name': 'Customer Map Tracking',
    'version': '1.0.0',
    'category': 'Extra Tools',
    'summary': 'Track customers / workers on map with PostGIS integration',
    'description': """
Customer Map Tracking with PostGIS
==================================

This module allows you to:
* Track customer locations using PostGIS geometry fields
* Set locations using geoengine map picker
* View all customers on a geoengine map
* Full PostGIS integration like Field Service

Features:
* PostGIS geometry fields
* GeoEngine map views
* Interactive map editing
* Spatial queries support

Requirements:
* PostgreSQL with PostGIS extension
* base_geoengine module
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'base_geoengine',  # Required for PostGIS integration
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        # Security (must come first)
        'security/security.xml',
        'security/ir.model.access.csv',

        # Base Views (define views before referencing them)
        'views/customer_map_views.xml',
        'views/customer_map_geoengine_views.xml',

        # GeoEngine Data (layers, etc) - after views are defined
        'data/geoengine_data.xml',

        # Actions (reference views defined above)
        'views/customer_map_actions.xml',

        # Menus (reference actions defined above)
        'views/customer_map_menus.xml',

        # Demo data (last)
        'demo/customer_map_demo.xml',
    ],
    'demo': [
        'demo/customer_map_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 50,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}