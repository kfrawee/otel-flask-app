OTEL_SERVICE_NAME=flask-blog-demo \
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://otelcol.aspecto.io:4317 \
OTEL_EXPORTER_OTLP_HEADERS=Authorization=YOUR_KEY \
opentelemetry-instrument python run.py
