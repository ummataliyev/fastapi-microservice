#!/bin/sh

echo 'Waiting for MinIO to be fully ready...'
sleep 10

for i in 1 2 3 4 5; do
    echo "Attempt $i: Setting up MinIO alias..."
    if /usr/bin/mc alias set local http://minio:9000 "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}"; then
        echo 'Alias configured successfully'
        break
    fi
    echo 'Retry in 3 seconds...'
    sleep 3
done

echo 'Creating buckets...'
/usr/bin/mc mb -p local/files || true

echo 'Setting public download policies...'
/usr/bin/mc anonymous set download local/files


# Verify policies
echo 'Verifying policies...'
/usr/bin/mc anonymous get local/files

echo 'All buckets created and configured successfully!'
exit 0
