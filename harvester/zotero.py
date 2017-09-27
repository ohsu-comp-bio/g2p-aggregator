from pyzotero.zotero import Zotero
import os

smmart_library = 1405957
api_key = os.environ.get("ZOTERO_API_KEY")

z = Zotero(smmart_library, 'group', api_key)
