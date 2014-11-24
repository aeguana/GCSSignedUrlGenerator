import base64
import datetime
import md5
import sys
import time

import Crypto.Hash.SHA256 as SHA256
import Crypto.PublicKey.RSA as RSA
import Crypto.Signature.PKCS1_v1_5 as PKCS1_v1_5
import OpenSSL
import OpenSSL.crypto as SSL_Crypto
import urllib

class GCSSignedUrlGenerator(object):
	def __init__(self, client_id_email, gcs_api_endpoint='https://storage.googleapis.com', key_der=None):
		"""Creates a CloudStorageURLSigner that can be used to access signed URLs.
		Args:
			key_der: A PyCrypto private key in der format.
			client_id_email: GCS service account email.
			gcs_api_endpoint: Base URL for GCS API.
		"""
		self._key_der = key_der
		self._client_id_email = client_id_email
		self._gcs_api_endpoint = gcs_api_endpoint

	def _base64Sign(self, plaintext):
		"""Signs and returns a base64-encoded SHA256 digest."""
		shahash = SHA256.new(plaintext)
		priv_key = RSA.importKey(self._key_der)
		signer = PKCS1_v1_5.new(priv_key)
		signature_bytes = signer.sign(shahash)

		return base64.b64encode(signature_bytes)

	def _makeSignatureString(self, verb, path, content_md5, content_type):
		"""Creates the signature string for signing according to GCS docs."""
		signature_string = ('{verb}\n'
			'{content_md5}\n'
			'{content_type}\n'
			'{expiration}\n'
			'{resource}')
		
		return signature_string.format(
			verb=verb,
			content_md5=content_md5,
			content_type=content_type,
			expiration=self._expiration,
			resource=path
		)

	def _makeUrl(self, verb, path, content_type='', content_md5=''):
		"""Forms and returns the full signed URL to access GCS."""
		base_url = '%s%s' % (self._gcs_api_endpoint, path)
		signature_string = self._makeSignatureString(verb, path, content_md5, content_type)
		signature_signed = self._base64Sign(signature_string)
		query_params = {
			'GoogleAccessId': self._client_id_email,
			'Expires': str(self._expiration),
			'Signature': signature_signed
		}

		return base_url, query_params

	def importP12Key(self, p12_key, p12_passphrase):
		"""Translating default p12 formatted priv key to der format."""
		p = SSL_Crypto.load_pkcs12(p12_key, p12_passphrase)
		self._key_der = OpenSSL.crypto.dump_privatekey(SSL_Crypto.FILETYPE_ASN1, p.get_privatekey())

	def makeSignedUrl(self, path, method='GET', expiration=None):
		"""Creates expiration timestamp for signed url and return ready signed url."""
		if method not in ['GET', 'PUT', 'DELETE']:
			raise Exception('Error', "Available methods: ['GET', 'PUT', 'DELETE']")

		if not expiration or not self._expiration:
			self._expiration = expiration or (datetime.datetime.now() + datetime.timedelta(days=1))
			self._expiration = int(time.mktime(self._expiration.timetuple()))

		base_url, query_params = self._makeUrl(method, path)

		return '%s?%s'%(base_url, urllib.urlencode(query_params))
