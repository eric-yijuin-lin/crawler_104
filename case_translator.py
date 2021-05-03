import json
class translator:

    def __init__(self, json_path):
        with open('./translate_dictionary.json', encoding='utf-8') as f:
            self.trans_dict = json.load(f)

    def get_translation(self, propty_key, propty_value):
        if type(propty_value) is list:
            translation = self.get_translated_list(propty_key, propty_value)
        else:
            translation = self.get_translated_value(propty_key, propty_value)
        return translation

    def get_translated_list(self, property_name,  value_list, concatenator=';'):
        translation = ''
        for value in value_list:
            trans_section = self.trans_dict[property_name]
            trans_key = str(value)
            if trans_key in trans_section:
                translation += self.trans_dict[property_name][str(value)] + ';'
            else:
                translation += trans_key + ';'
        return translation

    def get_translated_value(self, property_name, propty_value):
        trans_section = self.trans_dict[property_name]
        trans_key = str(propty_value)
        if trans_key in trans_section:
            translation = self.trans_dict[property_name][str(propty_value)]
        else:
            translation = trans_key
        return translation
