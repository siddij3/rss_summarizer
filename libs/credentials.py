def get_db_creds() -> dict:
    creds = {  "host":"localhost",
                "user":"junaid",
                "password":"junaid",
                "database":"rss_feeds",
                "auth_plugin":'mysql_native_password'}
    
    return creds