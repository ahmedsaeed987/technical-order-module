{
    'name': "Technical_Order_Module",
    'author': "ahmed",
    'sequence': -14,
    'category': '',
    'summary': '',
    'depends': ['sale','base'],
    'data': ["Data/sequence.xml"

,"reports/technical_order_report_views.xml"
         ,"security/group.xml"
        ,"views/res_partner.xml"
        ,"views/technical_order.xml"
        , "wizard/rejection_reason_views.xml"
             ]
    ,
    'installable': True,
    'application': True,
    'auto_install': False,

}




