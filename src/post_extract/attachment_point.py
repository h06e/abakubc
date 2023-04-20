import __main__
import csv

def compute_index(side,cylinder_number):
    possible_sides=['B','R','T','L']
    side_number=possible_sides.index(side)
    return int(cylinder_number)*__main__.DOF+side_number*__main__.DOF*__main__.N_CY

def clean_out(out):
    values={
        'RF1':[],'RF2':[],'RF3':[],'RM1':[],'RM2':[],'RM3':[],
        'U1':[],'U2':[],'U3':[],'UR1':[],'UR2':[],'UR3':[]
    }
    time_list=[]
    flag_get_time=False
    for k in out.keys():
        for instant in out[k].data:
            values[k].append(instant[1])
            if not flag_get_time:
                time_list.append(instant[0])
        flag_get_time=True

    return values,time_list

def add_data(d,i,type_of_point,extracted_disp_and_force,flag_first_step):
    extracted_disp_and_force[type_of_point][i]=   extracted_disp_and_force[type_of_point][i]+d['RF1'][1*flag_first_step:]
    extracted_disp_and_force[type_of_point][i+1]= extracted_disp_and_force[type_of_point][i+1]+d['RF2'][1*flag_first_step:]
    extracted_disp_and_force[type_of_point][i+2]= extracted_disp_and_force[type_of_point][i+2]+d['RF3'][1*flag_first_step:]
    extracted_disp_and_force[type_of_point][i+3]= extracted_disp_and_force[type_of_point][i+3]+d['RM1'][1*flag_first_step:]
    extracted_disp_and_force[type_of_point][i+4]= extracted_disp_and_force[type_of_point][i+4]+d['RM2'][1*flag_first_step:]
    extracted_disp_and_force[type_of_point][i+5]= extracted_disp_and_force[type_of_point][i+5]+d['RM3'][1*flag_first_step:]

    extracted_disp_and_force[type_of_point][i+6]= extracted_disp_and_force[type_of_point][i+6]+d['U1'][1*flag_first_step:]
    extracted_disp_and_force[type_of_point][i+7]= extracted_disp_and_force[type_of_point][i+7]+d['U2'][1*flag_first_step:]
    extracted_disp_and_force[type_of_point][i+8]= extracted_disp_and_force[type_of_point][i+8]+d['U3'][1*flag_first_step:]
    extracted_disp_and_force[type_of_point][i+9]= extracted_disp_and_force[type_of_point][i+9]+d['UR1'][1*flag_first_step:]
    extracted_disp_and_force[type_of_point][i+10]=extracted_disp_and_force[type_of_point][i+10]+d['UR2'][1*flag_first_step:]
    extracted_disp_and_force[type_of_point][i+11]=extracted_disp_and_force[type_of_point][i+11]+d['UR3'][1*flag_first_step:]
    return

def save_into_csv(FILE_NAME,data_list,time_step):
    with open(FILE_NAME, "wb") as f:
        writer = csv.writer(f)
        writer.writerow(time_step)
        writer.writerows(data_list)
    return
