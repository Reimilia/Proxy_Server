from flask.ext.restful import Resource,Api,abort,reqparse
from flask import Flask
from resources import Fhir_Resource,Privacy,PrivacyList

app = Flask(__name__)
api = Api(app)

api.add_resource(Privacy, '/Privacy')
api.add_resource(PrivacyList, '/Privacy/<privacy_id>')
api.add_resource(Fhir_Resource, '/<resource_type>/<resource_id>')


if __name__ == '__main__':
    app.run(debug=True)