from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible
from storages.backends.s3boto3 import S3Boto3Storage


@deconstructible
class PublicMediaStorage(Storage):
    """
    Storage backend for public media files. Uses S3 when configured, or if not, falls back to local file storage.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if S3 is configured
        bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME_MEDIA', '')
        if bucket_name:
            # Use S3 storage
            self._storage = S3Boto3Storage(
                bucket_name=bucket_name,
                default_acl='public-read'
            )
        else:
            # Use local file storage for development
            self._storage = FileSystemStorage(
                location=settings.MEDIA_ROOT,
                base_url=settings.MEDIA_URL
            )

    def url(self, name):
        """Get URL for the file"""
        try:
            return self._storage.url(name)
        except Exception:
            # If S3 fails and we're using local, return local URL
            if isinstance(self._storage, FileSystemStorage):
                return self._storage.url(name)
            # Otherwise, try to construct a basic URL
            return f"{settings.MEDIA_URL}{name}"

    def _open(self, name, mode='rb'):
        """Open the file"""
        return self._storage._open(name, mode)

    def _save(self, name, content):
        """Save the file"""
        return self._storage._save(name, content)

    def exists(self, name):
        """Check if file exists"""
        return self._storage.exists(name)

    def delete(self, name):
        """Delete the file"""
        return self._storage.delete(name)

    def size(self, name):
        """Get file size"""
        return self._storage.size(name)

    def path(self, name):
        """Get local file path (only for local storage)"""
        if hasattr(self._storage, 'path'):
            return self._storage.path(name)
        raise NotImplementedError("This backend doesn't support absolute paths.")
