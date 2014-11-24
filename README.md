#CGSSignedUrlGenerator

Authors:

* (c) 2014-2014 Marcin Kawa, kawa@aeguana.com

See sources:

* [storage-signedurls-python](https://github.com/GoogleCloudPlatform/storage-signedurls-python) for basic methods of creating signed URLs
* [GCS](https://cloud.google.com/storage/docs/accesscontrol) for Google Cloud Services Signed URLs documentation


CGSSignedUrlGenerator class provides easy method to generate signed URL's for Google Cloud. You can use private key provided by google in .p12 format or .der format.

-------------------------------------------------------------------------------

###Install

```
$ mkdir GCSSigner
$ virtualenv .
$ source bin/activate
$ git clone https://github.com/aeguana/GCSSignedUrlGenerator.git
$ cd GCSSignedUrlGenerator
$ pip install -r requirements.txt
```

###How to use

It is straight forward, if you have your private key saved in `.der` format

```python
from GCSSignedUrlGenerator import GCSSignedUrlGenerator

GC_KEY_FILE_NAME_DER = '<priv_key>.der' # file path to .der file with private key
GC_EMAIL = '<google-email>@developer.gserviceaccount.com' # provided by google

# open file and read content
gc_key_file_der = open(GC_KEY_FILE_NAME_DER, 'rb+')
private_key_der = gc_key_file_der.read()

# file path to object inside your google cloud
file_path = '/%s/%s' % ('test-bucket', 'test-file.txt')

# create signer to generate signed URLs
signer = GCSSignedUrlGenerator(GC_EMAIL, private_key_der)

# generate signed url
signed_url = signer.makeSignedUrl(file_path)

print signed_url
'https://storage.googleapis.com/test-bucket/test-file.txt?Expires=1416389894&GoogleAccessId=896388671115-fhb4f9o9k520c084tlj7r8g71ddsdi1n%40developer.gserviceaccount.com&Signature=Rshs1Acg5VXYsMtwEdQrAWGldLU9eCLb3bW5JN7xDkj7dzIaRIV8e4AoOjVisZ1JY%2BXHbO8RRDTZT4ubVHXdhoCWbmkcegnIXztAArWQeKoHTXmoayZEmcC72HAnFz9nPK23AYOmzo5scdn53yweJ8NWPtYgTdCQOb%2Fqve7PhFc%3D'

```

By default google is giving us key in `.p12` format. If we have this format we need to import key before use.
Remember to provide the keyword to unpack `.p12` file. It is available for you when the key is being downloaded from google.

```python
from GCSSignedUrlGenerator import GCSSignedUrlGenerator

GC_KEY_FILE_NAME_P12 = '<priv_key>.p12' # file path to .p12 file with private key
GC_EMAIL = '<google-email>@developer.gserviceaccount.com' # provided by google

# open file and read content
gc_key_file_p12 = open(GC_KEY_FILE_NAME_P12, 'rb+')
private_key_p12 = gc_key_file_p12.read()

# file path to object inside your google cloud
file_path = '/%s/%s' % ('test-bucket', 'test-file.txt')

# create signer to generate signed URLs
signer = GCSSignedUrlGenerator(GC_EMAIL)

# import key to the signer by passing the key content and keyword to unpack key
signer.importP12Key(private_key_p12, 'notasecret')

# generate signed url
signed_url = signer.makeSignedUrl(file_path)

print signed_url
'https://storage.googleapis.com/test-bucket/test-file.txt?Expires=1416417941&GoogleAccessId=896388671115-fhb4f9o9k520c084tlj7r8g71ddsdi1n%40developer.gserviceaccount.com&Signature=VlHv671%2FMKvP0nesU3EJu3yYeZnfQjorsD5YnVIi2yoZPLqSADWDTmFSV1wSJjKnlx8O5T7UbTyJdJUois8VCfjkgIk3kBIhXIaDihenulCyf37fzO7Nun0h54huG%2BkSha7t1TvJMTX%2FLWiswWw%2BTUvzoyrv%2F7mLMpTh7rrntVQ%3D'
```

### Defaults

1. Endpoint:

	By default the endpoint for GCS is set to

    ```python
    gcs_api_endpoint='https://storage.googleapis.com'
    ```
  
    You can change it when creating new object
    
    ```python
    signer = GCSSignedUrlGenerator(GC_EMAIL, gcs_api_endpoint='something else')
    ```
  
2. Expiration

	By default set to one day from the moment url was created.
    You can set it when creating the url
    
    ```python
    expire = datetime.datetime.now() + datetime.timedelta(days=3)
    signed_url = signer.makeSignedUrl(file_path, expiration=expire)
    
    # when you change it once it will be saved inside the object
    # so the value of 'expire' will be set as default for that object
    # you can change it whenever you want
    ```
3. Method

	You have three choices ['GET', 'PUT', 'DELETE'], by default `GET` is set.
    You can change it when generating URL. It is not saved inside the object so if you want to generate few urls with `PUT` permission you need to pass `PUT` each time.
    
    ```python
    signed_url_get = signer.makeSignedUrl(file_path)
    signed_url_put = signer.makeSignedUrl(file_path, method='PUT')
    signed_url_delete = signer.makeSignedUrl(file_path, method='DELETE')
    ```