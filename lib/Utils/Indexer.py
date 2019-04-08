# Special Indexer for Narrative Objects
import json
import os

from Utils.WorkspaceAdminUtils import WorkspaceAdminUtils


class Indexer:
    def __init__(self, config):
        self.ws = WorkspaceAdminUtils(config)
        self.schema_dir = config['schema-dir']

    def _tf(self, val):
        if val == 0:
            return False
        else:
            return True

    def _guid(self, upa):
        (wsid, objid, ver) = upa.split('/')
        return "WS:%s:%s:%s" % (wsid, objid, ver)

    def _mapping(self, filename):
        with open(os.path.join(self.schema_dir, filename)) as f:
            schema = json.loads(f.read())
        return schema['schema']

    def attributemapping_index(self, upa):
        obj = self.ws.get_objects2({'objects': [{'ref': upa}]})['data'][0]
        data = obj['data']
        rec = {
            "attributes": [],
            "attribute_ontology_ids": [],
            "attribute_units": [],
            "attribute_unit_ontology_ids": [],
            "attribute_values": [],
            "attribute_value_ontology_ids": [],
            "instances": data['instances'],
            "num_attributes": len(data['attributes']),
            "num_instances": len(data['instances']),
        }
        for attr in data['attributes']:
            rec['attributes'].append(attr['attribute'])
            if 'attribute_ont_id' in attr:
                rec['attribute_ontology_ids'].append(attr['attribute_ont_id'])
            if 'unit' in attr:
                rec['attribute_units'].append(attr['unit'])
            if 'attribute_ont_id' in attr:
                rec['attribute_unit_ontology_ids'].append(attr['attribute_ont_id'])
            if 'categories' in attr:
                rec['attribute_values'].extend(attr['categories'].keys())
                rec['attribute_value_ontology_ids'].extend(
                    x['attribute_ont_id'] for x in attr['categories'] if 'attribute_ont_id' in x)

        schema = self._mapping('attributemapping_schema.json')
        return {'data': rec, 'schema': schema}

    def kbasematrices_index(self, upa):
        obj = self.ws.get_objects2({'objects': [{'ref': upa}]})['data'][0]
        data = obj['data']
        rec = {
            "matrix_type": obj['info'][2],
            "row_attributes": [],
            "col_attributes": [],
            "row_attribute_ontology_ids": [],
            "col_attribute_ontology_ids": [],
            "row_attribute_values": [],
            "col_attribute_values": [],
            "row_ids": data['data']['row_ids'],
            "col_ids": data['data']['col_ids'],
            "num_rows": len(data['data']['row_ids']),
            "num_columns": len(data['data']['col_ids']),
            "attributes": [f'{k}|{v}' for k, v in data['attributes'].items()]
               }

        am_keys = ('attributes', 'attribute_ontology_ids', 'attribute_values')
        if 'row_attributemapping_ref' in data:
            row_data = self.attributemapping_index(data['row_attributemapping_ref'])
            rec.update({f'row_{x}': row_data[x] for x in am_keys})
        if 'col_attributemapping_ref' in data:
            col_data = self.attributemapping_index(data['col_attributemapping_ref'])
            rec.update({f'col_{x}': col_data[x] for x in am_keys})

        schema = self._mapping('kbasematrices_schema.json')
        return {'data': rec, 'schema': schema}
