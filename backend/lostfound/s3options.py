"""Opsyon ng django-storages para sa isang bucket ng Supabase Storage (S3-compatible).
Hiwalay na module ito para magamit sa settings at sa storage.py nang walang circular import."""


def supabase_s3_options(bucket_name, project_ref, access_key, secret_key, region):
    import os
    from botocore.config import Config
    return {
        'bucket_name': bucket_name,
        'access_key': access_key,
        'secret_key': secret_key,
        'region_name': region,
        # SUPABASE_S3_ENDPOINT: opsyonal, para sa lokal na Supabase o sa pagsubok.
        'endpoint_url': os.environ.get('SUPABASE_S3_ENDPOINT') or f'https://{project_ref}.storage.supabase.co/storage/v1/s3',
        'addressing_style': 'path',
        'signature_version': 's3v4',
        # Hindi sinusuportahan ng Supabase ang ACL at karamihan ng checksum header.
        'default_acl': None,
        'file_overwrite': False,
        'client_config': Config(
            request_checksum_calculation='when_required',
            response_checksum_validation='when_required',
        ),
    }
