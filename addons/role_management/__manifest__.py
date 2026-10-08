{
    "name": "Role Management",
    "version": "19.0.1.0.0",
    "category": "Administration",
    "summary": "Reusable Role Management app: a focused shortcut to assign roles to users.",
    "description": """
Role Management
================

A small, project-agnostic app that gives a "Role Management" entry in the
navbar for assigning roles to users, without needing full Settings access.
Any other module can depend on this one and imply its `group_role_manager`
group from their own manager-level group, so that role gets the menu too.
""",
    "author": "Ashiqur Zayed",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/security.xml",
        "views/res_users_views.xml",
        "views/res_groups_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
}
