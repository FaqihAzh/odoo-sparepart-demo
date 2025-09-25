{
    'name': 'Product Master Data',
    'version': '1.0.0',
    'summary': 'Master data product enhancements: auto item code, brand, supplier default, min/max per warehouse',
    'category': 'Inventory',
    'author': 'Saka Sakti Inovasi',
    'depends': ['product','stock','purchase'],
    'data': [
        'data/ir_sequence_product_code.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/product_threshold_views.xml',
    ],
    'installable': True,
    'application': False,
}
