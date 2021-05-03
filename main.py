import crawler
import datetime

case_list = crawler.get_case_list(0)
crawler.query_and_append_details(case_list)
crawler.save_case_list_csv(case_list)

#case_list = get_case_list(0)
#save_case_list_csv(case_list)