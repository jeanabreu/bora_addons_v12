# -*- coding: utf-8 -*-

{
    "name": "Activity Management | Activity Dashboard | Activity Monitoring | Activity Views",
    "version":"12.0.1",
    "license": "OPL-1",
    "support": "relief.4technologies@gmail.com",  
    "author" : "Relief Technologies",  
    "live_test_url": "https://youtu.be/0WBDPO9kqPM",       
    "category": "Extra Tools",
    "summary": "schedule activity management Mail Activity Board daily to do management to do list crm activity management sale activity management",
    "description": """

    """,
    "depends": ["mail"],
    "data": [
        
        "security/activity_security.xml",
        "security/ir.model.access.csv",
        "views/activity_tag.xml",
        "views/assets_backend.xml",
        "views/mail_activity.xml",

    ],
    "qweb": [
        "static/src/xml/dashboard.xml",       
    ],
    
    "images": ["static/description/background.png",],              
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 35,
    "currency": "EUR"   
}
