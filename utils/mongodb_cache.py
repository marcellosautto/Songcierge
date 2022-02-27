import discord
import spotipy
import logging
import collections
import uuid
from spotipy import cache_handler


logger = logging.getLogger(__name__)

# class CacheHandler():
#     """
#     An abstraction layer for handling the caching and retrieval of
#     authorization tokens.
#     Custom extensions of this class must implement get_cached_token
#     and save_token_to_cache methods with the same input and output
#     structure as the CacheHandler class.
#     """

#     def get_cached_token(self):
#         """
#         Get and return a token_info dictionary object.
#         """
#         # return token_info
#         raise NotImplementedError()

#     def save_token_to_cache(self, token_info):
#         """
#         Save a token_info dictionary object to the cache and return None.
#         """
#         raise NotImplementedError()
#         return None


class MongoDBCacheHandler(cache_handler.CacheHandler):
    
    def __init__(self, connection, document_name, key):
        self.db = connection[document_name]
        self.logger = logging.getLogger(__name__)
        self.key = None

    # Getters and Setters
    def get_cached_token(self):
        return self.find_cached_token()

    def save_token_to_cache(self, dict):
        return self.insert_token(dict)

    #Functions
    def find_cached_token(self):
        if not self.db.find_one({"_id": self.key}):
            return

    def insert_token(self, dict):
        if not isinstance(dict, collections.abc.Mapping):
            raise TypeError("Expected Dictionary.")

        # Always use your own _id
        if not dict['_id']:
            raise KeyError("_id not found in supplied dict.")

        self.db.insert_one(dict)