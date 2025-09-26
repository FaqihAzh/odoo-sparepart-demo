{
    "name": "Customer / Worker Map Tracking",
    "version": "17.0.1.0.0",
    "summary": "Store customers/workers with location and show them on a Leaflet map dashboard",
    "category": "Tools",
    "author": "Saka Sakti Inovasi",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/customer_worker_views.xml",
        "views/customer_worker_menu.xml",
        "views/customer_map_templates.xml",
        "views/assets.xml",
    ],
    "installable": True,
    "application": False,
}
