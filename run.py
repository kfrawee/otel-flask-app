from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider

from flaskblog import app, db

FlaskInstrumentor().instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=db.engine)
Psycopg2Instrumentor().instrument()


provider = TracerProvider()
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create(
        {SERVICE_NAME: "flask-blog-demo"}))
)


if __name__ == "__main__":
    # export FLASK_APP=flaskblog.py
    # export FLASK_ENV=development
    # export FLASK_DEBUG=1
    # flask run

    # create db:
    # run python shell
    # >>> from flaskblog import add, db
    # >>> app.app_context().push()
    # >>> db.create_all
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False)
    # trace.get_tracer_provider().shutdown()
