#!/bin/sh
set -e

# Run database migrations if configured
if [ "$RUN_MIGRATIONS" = "true" ] || [ "$RUN_MIGRATIONS" = "1" ]; then
    echo "Running database migrations with Alembic..."
    alembic upgrade head
    echo "Database migrations completed successfully."
fi

# Execute the primary container command
exec "$@"
