from verify_rego import verify
import datetime
import time

cck_buses = ("67", "172", "188", "188e", "190", "300", "301", "302", "307", "307A", "307T", "925", "927", "976", "983", "985", "991")
bpj_buses = ("75", "176", "180", "184", "920", "922", "970", "972", "972M", "973", "975", "979")
passing_smrt = ("178", "187", "960", "961")
passing_sbst = ("160", "170", "974")
passing_tts = ("171", "177", "963", "963e", "966")
other_svc = ("61", "167", "506", "staff_ferry")
types_of_svc = [("Choa Chu Kang", cck_buses), ("Bukit Panjang/Gali Batu", bpj_buses), ("Passing Through Services (SMRT)", passing_smrt),\
                ("Passing Through Services (SBST)", passing_sbst), ("Passing Trough Services (TTS)", passing_tts), ("Other Services", other_svc)]

def initialise_new_dict():
    buses_dict = {}
    #initialise new dictionary
    for type_of_svc in types_of_svc:
        bus_svcs = type_of_svc[1]
        for bus_svc in bus_svcs:
            buses_dict[bus_svc] = []
    return buses_dict

def convert_to_dict(deployment_list_filename):
    with open(deployment_list_filename) as f:
        buses_dict = initialise_new_dict()
        curr_type_idx = -1
        curr_svc_idx = -1
        for line in f:
            if len(line) > 1:
                if curr_type_idx == -1 and types_of_svc[0][0] == line[:-1]: #first section not reached yet
                    curr_type_idx = 0
                elif 0 <= curr_type_idx <= len(types_of_svc) - 2 and types_of_svc[curr_type_idx + 1][0] == line[:-1]: #end of current section reached
                    curr_type_idx += 1
                    curr_svc_idx = -1
                elif 0 <= curr_type_idx <= len(types_of_svc) - 1: #in current section
                    bus_svcs = types_of_svc[curr_type_idx][1]
                    if curr_svc_idx == -1 and bus_svcs[0] == line[:-1]: #first bus svc not reached yet
                        curr_svc_idx = 0
                    elif 0 <= curr_svc_idx <= len(bus_svcs) - 2 and bus_svcs[curr_svc_idx + 1] == line[:-1]: #end of current bus svc reached
                        curr_svc_idx += 1
                    elif 0 <= curr_svc_idx <= len(bus_svcs) - 1: #in current bus svc
                        data = line[:-1].split(" ")
                        curr_bus_svc = bus_svcs[curr_svc_idx]
                        rego = data[0]
                        entry = (rego,)
                        if len(data) > 1: #additional info present
                            entry = (rego, "_".join(data[1:]))
                        buses_dict[curr_bus_svc].append(entry)
        f.close()
        return buses_dict

def convert_dict_to_list(buses_dict):
    date_str = str(input("Input today's date: "))
    output_filename = str(datetime.datetime.now())[:19].replace(":", "-").replace(" ", "-") + ".txt"
    w = open(output_filename, "a")
    w.write(date_str + " Confirmed Spottings\n(Community Contributions)\n\n\n")
    for type_of_svc in types_of_svc:
        type_name, bus_svcs = type_of_svc[0], type_of_svc[1]
        w.write(type_name + "\n\n\n")
        for bus_svc in bus_svcs:
            w.write(bus_svc + "\n\n")
            sorted_lst = sorted(buses_dict[bus_svc])
            for rego in sorted_lst:
                rego_entry = rego[0] #rego[0] contains actual rego, rego[1] only exists if it contains additional info
                if len(rego) >= 2:
                    rego_entry += " " + rego[1].replace("_", " ")
                w.write(rego_entry + "\n\n")
            w.write("\n\n")
    w.close()
    return "ouput file on " + output_filename

def make_entry():
    command_type = ""
    while command_type not in ["1", "2"]:
        command_type = str(input("Input 1 to make new list, input 2 to update list: "))
    if command_type == "1":
        buses_dict = initialise_new_dict()
    elif command_type == "2":
        filename = str(input("enter text filename for current list: "))
        buses_dict = convert_to_dict(filename)
        print(buses_dict)
    command = ""
    while command != "quit":
        command = str(input("enter ('quit' to quit, 'list' to create list and quit): "))
        if command == "list":
            print(convert_dict_to_list(buses_dict))
            command = "quit"
        if command != "quit":
            parsed_command = command.split("\n")
            for row in parsed_command:
                parsed_row = row.split(" ")
                entries_for_svc = []
                error = False
                if len(parsed_row) == 2: #(rego) (svc)
                    bus_svc_entry = parsed_row[1]
                    bus_rego_entry = parsed_row[0]
                    entries_for_svc.append((verify(bus_rego_entry),))
                elif len(parsed_row) == 3 and parsed_row[1] in buses_dict: #(rego) (svc) (description)
                    bus_svc_entry = parsed_row[1]
                    bus_rego_entry = parsed_row[0]
                    bus_desc_entry = parsed_row[2]
                    entries_for_svc.append((verify(bus_rego_entry), bus_desc_entry))
                elif parsed_row[-1] in buses_dict: #(rego 1) (rego 2) ... (rego n) (svc)
                    bus_svc_entry = parsed_row[-1]
                    bus_desc_entry = ""
                    for i in range(len(parsed_row) - 1):
                        if parsed_row[-2-i][0] + parsed_row[-2-i][-1] == "()": #description
                            bus_desc_entry = parsed_row[-2-i][1:-1]
                        elif not verify(parsed_row[-2-i]):
                            bus_desc_entry = ""
                        else:
                            bus_rego_entry = parsed_row[-2-i]
                            if bus_desc_entry == "":
                                entries_for_svc.append((verify(bus_rego_entry),))
                            else:
                                entries_for_svc.append((verify(bus_rego_entry), bus_desc_entry))
                            bus_desc_entry = ""
                else:
                    print("format error")
                    error = True
                if not error and bus_svc_entry not in buses_dict:
                    print("invalid svc no", bus_svc_entry)
                    error = True
                if not error:
                    for entry in entries_for_svc:
                        if not entry[0]:
                            print("invalid rego")
                        else:
                            buses_dict[bus_svc_entry].append(entry)

make_entry()
#with open("2023-12-07-22-05-41.txt") as f:
#    for line in f:
#        print(len(line))
#    f.close()
#    print("done")
#print(str(datetime.datetime.now())[:19])