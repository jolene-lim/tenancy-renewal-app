import pymongo
import datetime
from bson.decimal128 import Decimal128
from bson.objectid import ObjectId

class mongodb():

    _default_connect_info = {
        'host': 'localhost',
        'port': '27017'
    }

    _collections = {
        'payslip': 'payslip'
    }

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://{}:{}/".format(self._default_connect_info['host'], self._default_connect_info['port']))
        self.db = self.client["tenancy-app"]
        self.payslip_col = self.db[self._collections['payslip']]

    def insert_record(self, name, nric, age, income, cpf, addr, lease_id, img_str, detected_income = None, img_highlight=None, verified=False, renewable=False, verify_fail=None, renew_fail=None):
        record = {
            'person': {
                'nric': nric,
                'first_name': name,
                'age': age,
                'income': {
                    'declared': Decimal128(income),
                    'cpf': Decimal128(cpf)
                }
            },
            'property': {
                'address': addr,
                'lease_id': lease_id
            },
            'date': datetime.datetime.utcnow(),
            'original': img_str,
            'verified': verified,
            'renewable': renewable
        }

        if img_highlight is not None:
            record['annotated'] = img_highlight

        if detected_income is not None:
            record['detected_income'] = Decimal128(detected_income)

        if verified == False and verify_fail is not None:
            record['verify_fail'] = verify_fail
        
        if renewable == False and renew_fail is not None:
            record['renew_fail'] = renew_fail

        self.payslip_col.insert_one(record)

    def get_records(self):
        records = self.payslip_col.find({'archived': {'$exists': False}}).sort([('verified', pymongo.ASCENDING), ('renewable', pymongo.ASCENDING)])
        return list(records)

    def update_record(self, id, income, verified, renew):
        try:
            resp = self.payslip_col.update_one(
                {'_id': ObjectId(id)}, 
                {'$set': {
                    'detected_income': Decimal128(income),
                    'verified': self._str_to_bool(verified),
                    'renewable': self._str_to_bool(renew)
                    }
                }
            )
            if resp.matched_count == 0:
                return "Error: Record Not Found"
            else:
                return "Successfully Updated Record. Refresh Page to View Updates."
        except Exception as e:
            return str(e)

    def _str_to_bool(self, str):
        if str == 'true':
            return True
        return False

    def archive(self, id):
        try:
            resp = self.payslip_col.update_one({'_id': ObjectId(id)}, {'$set': { 'archived': True }})
            if resp.matched_count == 0:
                return "Error: Record Not Found"
            else:
                return "Successfully Archived Record. Refresh Page to View Updates."
        except Exception as e:
            return str(e)
