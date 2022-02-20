import datetime
import json
def calculate_fee(template_id,vars,go_in_time,now_time):
    if template_id == "AXSJF":
        return AXSJF(vars,go_in_time,now_time)
    elif template_id == "FSDAXSJF":
        return FSDAXSJF(vars,go_in_time,now_time)
    elif template_id == "FSDHHJF":
        return FSDHHJF(vars,go_in_time,now_time)
    elif template_id == "FSDYQJAXSJF":
        return FSDYQJAXSJF(vars,go_in_time,now_time)
    elif template_id == "YQJAXSJF":
        return YQJAXSJF(vars,go_in_time,now_time)
    elif template_id == "YQJAXSYFDJF":
        return YQJAXSYFDJF(vars,go_in_time,now_time)
    else:
        return 0.01

#按小时计费
def AXSJF(vars,go_in_time,now_time):
    vars = json.loads(vars)
    free_time = vars["free_time"]
    after_pay_free_time = vars["after_pay_free_time"]
    cost_per_hour = vars["cost_per_hour"]
    round_up = vars["round_up"]

    total_times = now_time - go_in_time
    if total_times.total_seconds() < free_time * 60:
        return 0.0

    if round_up == "yes":
        cost_time = round(total_times.total_seconds()/3600)
    else:
        cost_time = total_times.total_seconds()/3600

    fee_1 = cost_time * cost_per_hour

    return fee_1



#分时段按小时计费
def FSDAXSJF(vars,go_in_time,now_time):
    return 0.0
#分时段混合计费
def FSDHHJF(vars,go_in_time,now_time):
    return 0.0
#分时段有起价按小时计费
def FSDYQJAXSJF(vars,go_in_time,now_time):
    return 0.0
#有起价按小时计费
def YQJAXSJF(vars,go_in_time,now_time):
    return 0.0
#有起价按小时有封顶计费
def YQJAXSYFDJF(vars,go_in_time,now_time):
    return 0.0


if __name__ == "__main__":
    print(datetime.datetime.now() - datetime.datetime(2022, 1, 20, 22, 6, 40))
    a = AXSJF('{"free_time":15,"after_pay_free_time":15,"cost_per_hour":3,"round_up":"yes"}',datetime.datetime(2022, 1, 20, 22, 6, 40),datetime.datetime.now())
    print(a)