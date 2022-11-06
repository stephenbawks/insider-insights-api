# variables for database and url configuration
import os

from supabase import Client, create_client


class SupabaseDB:
    """
    class instance for database connection to supabase
    :str: url: configuration for database url for data inside supafast project
    :str: key: configuration for database secret key for authentication
    :object: supabase: Supabase instance for connection to database environment
    """

    url: str = os.environ.get("supabase_api_url")
    key: str = os.environ.get("supabase_api_key")
    supabase: Client = create_client(url, key)