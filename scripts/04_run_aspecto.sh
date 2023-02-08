OTEL_SERVICE_NAME=flask-blog-demo \
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://otelcol.aspecto.io:4317 \
OTEL_EXPORTER_OTLP_HEADERS=Authorization=3cfbccad-f612-4c89-89ff-1621703dbf07 \
opentelemetry-instrument python run.py
