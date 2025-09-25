{
    'name': 'Stock QR Tracking (Purchase flow)',
    'version': '1.0.0',
    'summary': 'Generate per-unit QR on PO, print labels, scan to verify and receive stock',
    'category': 'Inventory',
    'author': 'Saka Sakti Inovasi',
    'depends': ['stock','purchase','product_master'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/lot_views.xml',
        'reports/purchase_qr_report.xml',
    ],
    'installable': True,
    'application': False,
}
