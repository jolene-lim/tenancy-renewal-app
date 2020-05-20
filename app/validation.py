import pytesseract
import cv2
import re
from decimal import Decimal
import numpy as np
import base64

class Validator():

    def __init__(self):
        # status
        self.status_code = 400
        self.error = None
        self.renewable = False # whether tenancy is renewable
        self.name_verified = False
        self.verify_fail = []
        self.renew_fail = None

        # data
        self.income = None
        self._income_idx = -1
        self._name_idx = -1

        # options
        self._INCOME_THRESHOLD = 3000
        self._CPF_RATES = {
            50: {'below 50': None, '50-750': 0.16, '750': 0.36},
            55: {'below 50': None, '50-750': 0.14, '750': 0.352},
            60: {'below 50': None, '50-750': 0.105, '750': 0.235},
            65: {'below 50': None, '50-750': 0.07, '750': 0.145},
            70: {'below 50': None, '50-750': 0.065, '750': 0.115}
        }
        self._RGB = (0, 242, 255) # yellow 
        self._ALPHA = 0.4 # opacity of highlight

    def validate(self, url, name, income, age, cpf):
        try:
            self.name = name
            self.url = url
            self._validate_img(self.url, self.name)
            if status_code != 400:
                self.verified = self._check_verified(age, cpf, income)
                self.renewable = self._check_renewable()
                self.highlight = self._get_highlight()

        except Exception as e:
            self.status_code = 500
            self.error = e

    def _check_verified(self, age, cpf, income):
        name_ok = self.name_verified
        if name_ok == False:
            self.verify_fail.append("Name Not Verified")
        income_ok = self._check_income(income)
        if income_ok:
            cpf_ok = self._check_cpf(age, cpf)
            if cpf_ok == False:
                self.verify_fail.append("CPF Contradicts Income Declared")
        else:
            self.verify_fail.append("Income Detected Contradicts Income Declared")
            cpf_ok = False

        return name_ok and income_ok and cpf_ok

    def _check_renewable(self):
        if self.verified == False:
            self.renew_fail= "Income not verified"
            return False

        renewable = self.income <= self._INCOME_THRESHOLD
        if renewable == False:
            self.renew_fail = "Income above threshold"
        return renewable

    def _check_income(self, income):  # check if declared income = OCR detected income (allow rounding error)
        if self.income is not None:
            return abs(round(self.income - Decimal(income))) <= 1
        return False

    """
    incomplete, using estimated rates only - but idea is to check if expected cpf (based on income)
    but idea is the calculate expected cpf based on declared income
    """
    def _check_cpf(self, age, cpf):
        age_key = self._get_age_key(int(age))
        income_range = self._get_income_range(self.income)

        expected_cpf = Decimal(self._CPF_RATES[age_key][income_range]) * self.income
        if abs(round(expected_cpf - Decimal(cpf))) <= 1:
            return True
        return False

    def _get_age_key(self, age):
        if age <= 50:
            return 50
        if age <= 55:
            return 55
        if age <= 60:
            return 60
        if age <= 65:
            return 65
        return 70
    
    def _get_income_range(self, income):
        if income <= 50:
            return "below 50"
        if income < 750:
            return "50-750"
        return "750"

    def _validate_img(self, url, name):

        self.img = self._decode(self.url)
        #self.img = self._preprocess_img(img)
        self.d = self._run_OCR(self.img)
        result = self._scan(self.d)

        if result[0] != -1:
            self.status_code = 200 # OK- OCR detected income
            self._income_idx = result[0]
            self.income = Decimal(re.sub(',', '', result[1]))

    def _decode(self, url): # converts img bytes to cv2 img
        jpg_original = base64.b64decode(url)
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)
        return img

    def _preprocess_img(self, img): # incomplete - should scale/fix skew of img etc to optimize OCR performance
        return img

    def _run_OCR(self, img):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        return pytesseract.image_to_data(img, lang='eng', output_type=pytesseract.Output.DICT)

    def _scan(self, d):
        for i in range(0, len(d['text'])):
            word = d['text'][i]

            if word != word: # if word is None
                continue

            # find name
            if word.lower() == self.name.lower():
                self.name_verified = True
                self._name_idx = i

            # find net income
            if word.lower() in ['net', 'nett']:
                for j in range(i+1, len(d['text'])):
                    word = d['text'][j]
                    income = re.search('[0-9]*[,]?[0-9]+[.][0-9]{0,2}', word)

                    if income:
                        return j, income.group(0)
        return (-1, None)

    def _get_highlight(self):
        return self._highlight(self.img, self.d, self._name_idx, self._income_idx)

    def _highlight(self, img, d, name, income):

        if name != -1: # add name highlight
            name_overlay = self._create_highlight(img, d, name, self._RGB)
            img = cv2.addWeighted(name_overlay, self._ALPHA, img, 1 - self._ALPHA, 0)

        if income != -1: # add income highlight
            income_overlay = self._create_highlight(img, d, income, self._RGB)
            img = cv2.addWeighted(income_overlay, self._ALPHA, img, 1 - self._ALPHA, 0)    
    
        imencoded = cv2.imencode(".jpg", img)[1]
        jpg_as_text = encode(imencoded)

        return jpg_as_text

    def _create_highlight(self, img, d, i, rgb):
        overlay = img.copy()
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(overlay, (x, y), (x + w, y + h), rgb, -1)
        return overlay

def encode(img):
    jpg_as_text = base64.b64encode(img)
    jpg_as_text = jpg_as_text.decode('utf-8')
    return jpg_as_text