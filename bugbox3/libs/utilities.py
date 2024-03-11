
import json

from django.core.serializers.json import DjangoJSONEncoder


def encode_json(data):
    return json.dumps(data, cls=DjangoJSONEncoder)


def get_json_context(context_dict):
    if isinstance(context_dict, dict):
        thejson = encode_json(context_dict)
        return '<script id="json_context" type="application/json">%s</script>' % thejson
    else:
        return None
