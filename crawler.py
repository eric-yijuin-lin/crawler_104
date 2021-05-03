import requests
import time
import csv
import json
import copy
import datetime
import case_translator

# sample result: [{'des': '屏東縣屏東市', 'no': '6001018001'}, {...}]
def get_place_code_tw():
    resp = requests.get('https://top.104.com.tw/api/staticArea')
    data = resp.json()
    area_code_dict = {}
    for area in data[0]['n']:
        key = area['no']
        value = area['des']
        area_code_dict[key] = value

    return area_code_dict

def get_case_type_code():
    return {
        '1001001': '伴讀',
        '1002000': '學科',
        '1002001': '國文',
        '1002002': '數學',
        '1002003': '理化',
        '1002004': '物理',
        '1002005': '化學',
        '1002006': '歷史',
        '1002007': '地理',
        '1002008': '公民',
        '1002009': '自然科學',
        '1002010': '生物',
        '1002011': '地球科學',
        '1002012': '科展指導',
        '1003000': '語文',
        '1003001': '英文',
        '1003002': '英文寫作',
        '1003003': '日文',
        '1003004': '韓文',
        '1003005': '德文',
        '1003006': '法文',
        '1003007': '西班牙文',
        '1003008': '俄文',
        '1003009': '粵語',
        '1003010': '泰語',
        '1003011': '越語',
        '1003012': '中文(華語)',
        '1003099': '其他語言',
        '1006000': '術科/職場技能',
        '1006001': '文書處理',
        '1006002': '財會/金融類',
        '1006003': '行銷廣告類',
        '1006004': '資訊軟體系統類',
        '1006005': '設計類',
        '1006006': '電子/機械類',
        '1006007': '專案管理類',
        '1006008': 'EMBA/MBA',
        '1006009': '美妝技巧',
        '1006010': '檢定考試',
        '1006099': '其他技能',
    }

def get_case_list(target_page):
    url = 'https://top.104.com.tw/api/caseList/search'
    search_params = {
        'cats': '1002000,1003001,1003002,1006004'
    }

    resp = requests.get(url, search_params)
    data = resp.json()
    cases = data['data']
    total_count = data['total']
    case_per_page = len(cases)
    print('got case list, total ' + str(total_count) + 'cases')

    craw_page = int(total_count / case_per_page)
    if target_page != None and target_page > 0:
        craw_page = target_page
    for i in range(2, craw_page + 1):
        print('crawling page' + str(i))
        search_params['pageNum'] = i
        resp = requests.get(url, search_params)
        data = resp.json()
        cases += data['data']
        resp.close()
        time.sleep(0.2)

    return cases

def save_case_list_csv(case_list):
    replace_code_with_name(case_list)

    file_name = '.\\104家教職缺' + datetime.datetime.today().strftime('%Y-%m-%d') + '.csv'
    column_names = case_list[0].keys()
    with open(file_name, 'w', encoding='utf-8', newline='') as csvFile:
        dictWriter = csv.DictWriter(csvFile, fieldnames=column_names)
        dictWriter.writeheader()
        for case in case_list:
            try:
                dictWriter.writerow(case)
            except Exception as e:
                print('fail to write row: exception: ' + str(e))
                print(str(case))
                print('=' * 10)

    with open('D:\\104家教職缺.csv', encoding='utf-8') as f:
        content = f.read()
        content_with_bom = 'ufeff' + content 
        with open('D:\\104家教職缺.csv', 'w', encoding='utf-8') as f2:    
            f2.write(content_with_bom)

def replace_code_with_name(case_list):
    place_dict = get_place_code_tw()
    type_dict = get_case_type_code()
    for case_data in case_list:
        case_data['basicId'] = '##' + case_data['basicId'] # excel 會把數字變科學符號，用這個當 placeholder 取代
        case_data['assignPlace'] = get_concated_places(case_data, place_dict)
        case_data['demandCategory'] = get_concated_categories(case_data, type_dict)


    
    print('replace done')
    #print('first row: ' + str(case_list[0]))

def get_concated_places(case_data, place_dict):
    if case_data['assignPlace'] == None:
        return '未指定'
    else:
        concated_places = ''
        for place_code in case_data['assignPlace']:
            place_code = int(int(place_code) / 1000) * 1000
            place_code = str(place_code)
            if place_code in place_dict:
                place_name = place_dict[place_code]
            else:
                place_name = place_code
            concated_places += (place_name + ';')
    return concated_places

def get_concated_categories(case_data, type_dict):
    if case_data['demandCategory'] == None:
        return '未指定'
    else:
        concated_categories = ''
        for type_code in case_data['demandCategory']:
            if type_code in type_dict:
                type_name = type_dict[type_code]
            else:
                type_name = type_code
            concated_categories += (type_name + ';')
    return concated_categories

def query_and_append_details(case_list):
    key_path_dict = { # {'final_key': 'nested_key_path'}
        'educationalStage': 'educationalStage',
        'studentGrade': 'demandTutorInfo:studentGrade',
        'studentSex': 'demandTutorInfo:studentSex',
        'experience': 'demandTutorInfo:experience',
        'jobOccupation': 'demandTutorInfo:jobOccupation',
        'classPlace': 'demandTutorInfo:classPlace',
        'classWay': 'demandTutorInfo:classWay'
    }

    translator = case_translator.translator('.\\translte_dictionary.json')
    total_case_count = len(case_list)
    current_case_counter = 0
    for case in case_list:
        current_case_counter += 1
        print ('craling case detail ' + str(current_case_counter) + '/' + str(total_case_count))
        demand_id = case['demandId']
        basic_id = case['basicId']
        
        try:
            case_info = get_case_detail_info(basic_id, demand_id)
            dict_to_append = extract_values_to_append(key_path_dict, case_info)
            for key in dict_to_append: # translate content
                dict_to_append[key] = translator.get_translation(key, dict_to_append[key])

            # 取完、翻譯完要 append 的值後，把原本巢狀的屬性刪除，再把翻譯完的值加回去，以攤平 object
            # refactor later
            keys_to_remove = get_keys_to_remove(key_path_dict)
            for key in keys_to_remove:
                if key in case_info:
                    del case_info[key]
            for key in dict_to_append:
                case[key] = dict_to_append[key]
        except Exception as ex:
            print('failed to get detail of [' + basic_id + ',' + demand_id +']')
            print(ex)
        
        time.sleep(0.2)

def get_case_detail_info(basic_id, demand_id):
    url = 'https://top.104.com.tw/api/common/demand/caseInfo'
    search_params = {
        'basicId': basic_id,
        'demandId': demand_id
    }

    # if demand_id == 'Demand-3923769633834064':
    #     print()

    try:
        resp = requests.get(url, search_params)
        case_info = resp.json()
    except: 
        raise
    finally:
        if resp != None:
            resp.close()

    return case_info

def extract_values_to_append(key_path_dict, case_info):
    result = {}
    for key in key_path_dict:
        nested_path = key_path_dict[key]
        result[key] = get_nested_json_value(nested_path, case_info)
    return result

def get_keys_to_remove(keys_to_append): # get roots of nested key paths
    result = []
    for key in keys_to_append:
        key_path = key.split(':')
        result.append(key_path[-1])
    return result

def get_nested_json_value(nested_path, json_object):
    result = copy.deepcopy(json_object)
    kyes = nested_path.split(':')
    for key in kyes:
        result = result[key]
    return result
