{
    'name': 'Customer Map Tracking',
    'version': '1.0.0',
    'summary': 'Track customers/workers on a map; pick coords by clicking map; dashboard with markers and modal details.',
    'category': 'Tools',
    'author': 'Saka Sakti Inovasi',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_views.xml',
        'views/customer_dashboard.xml',
        'views/wizards/customer_detail_wizard_views.xml',
    ],
    'assets': {
        'web.assets_web': [
            # Leaflet (CDN) + our CSS/JS
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'customer_map_tracking/static/src/css/map.css',
            'customer_map_tracking/static/src/js/map_widget.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
