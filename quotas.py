#!/usr/bin/env python3
import sys
import config
import quotas_cmdline as qc
#import inspect

# Assumptions
#
# Phonetype: 1 = Landline, 2 = Cellphone
# Mode: 1 = Phone, 2 = Email, 3 = Text

class Quota:
    def __init__(self, prefix, quota_name, quota_limit, question_name, question_code, nsize, nsize_override, flex=0, tri=False, raw=False):
        self.name = quota_name
        self.limit = quota_limit
        self.question_name = question_name
        self.q_code = question_code
        self.size = nsize
        self.nsize_override = nsize_override
        self.prefix = prefix
        self.flex = flex
        self.isactive = True
        self.tri = tri
        self.raw = raw
        self.counter_limit = int((len(str(self.size)) + 1) * "9")
        self.fullname = name = self.prefix + " - " + self.name
        if (self.flex > 0):
            self.fullname += " - Flex " + str(self.flex) + "%"

    def validify(self):
        if (self.limit == 0):
            self.isactive = False
        elif(self.limit == -1):
            self.isactive = False
            self.limit = self.counter_limit

    def calculate_limit(self, nsize_index=None):
        self.validify()
        if (self.raw):
            return
        if (self.limit == self.counter_limit):
            return
        size = self.size
        if (nsize_index != None):
            size = config.trimode_nsize[nsize_index]
        self.limit = round(size * (self.limit/100))
        # flex
        if (self.flex > 0):
            self.limit += int((self.flex / 100) * size)

    def display(self):
        simple = "Simple"
        if (self.tri):
            self.isactive = False
        quota_settings = '"{""action"":""1"",""autoload_url"":""1"",""active"":""' + str(int(self.isactive)) + '"",""qls"":[{""quotals_language"":""en"",""quotals_name"":""x"",""quotals_url"":"""",""quotals_urldescrip"":"""",""quotals_message"":""Sorry your responses have exceeded a quota on this survey.""}]}"'
        quota_settings_dnq = '"{""action"":""1"",""autoload_url"":""1"",""active"":""' + str(int(self.isactive)) + '"",""qls"":[{""quotals_language"":""en"",""quotals_name"":""x"",""quotals_url"":"""",""quotals_urldescrip"":"""",""quotals_message"":""Thank and Terminate.""}]}"'
        quota_settings_dnq_online = '"{""action"":""1"",""autoload_url"":""1"",""active"":""' + str(int(self.isactive)) + '"",""qls"":[{""quotals_language"":""en"",""quotals_name"":""x"",""quotals_url"":"""",""quotals_urldescrip"":"""",""quotals_message"":""Thank you for your time.""}]}"'
        quota_settings_reschedule = '"{""action"":""1"",""autoload_url"":""1"",""active"":""' + str(int(self.isactive)) + '"",""qls"":[{""quotals_language"":""en"",""quotals_name"":""x"",""quotals_url"":"""",""quotals_urldescrip"":"""",""quotals_message"":""Reschedule and end call.""}]}"'

        data = ""
        nlow = self.fullname.lower()
        if (self.fullname.__contains__("DNQ")):
            self.limit = 0
        if (nlow.__contains__("reschedule")):
            data =(self.fullname + "," + simple + "," + self.question_name + "," + str(self.q_code) + "," +
            str(self.limit) + "," + quota_settings_reschedule)
        elif (self.fullname.__contains__("DNQ")):
            if (nlow.find("email") != -1 or nlow.find("text") != -1 or nlow.find("online") != -1):
                data = (self.fullname + "," + simple + "," + self.question_name + "," + str(self.q_code) + "," +
                str(self.limit) + "," + quota_settings_dnq_online)
            else:
                data = (self.fullname + "," + simple + "," + self.question_name + "," + str(self.q_code) + "," +
                str(self.limit) + "," + quota_settings_dnq)
        else:
            data = (self.fullname + "," + simple + "," + self.question_name + "," + str(self.q_code) + "," +
            str(self.limit) + "," + quota_settings)
        return data + "\n"

class QuotaGroup:
    def __init__(self, group_name, trisplit, flex, raw, cli, nsize, tri_sizes):
        self.group_name = group_name
        self.trisplit = trisplit
        self.flex = int(flex)
        self.raw = raw
        self.client = cli
        self.nSize = int(nsize)
        self.tri_sizes = tri_sizes
        self.quotas = []
        self.limits = []
        self.names = []

    def get_name(self):
        return self.group_name

    def add_quota(self, quota_name, quota_limit, question_name, question_code, nsize_override, expand=True):
        flex = 0
        if (self.flex > 0):
            flex = self.flex
        if (config.client == "tulchin"):
            # for the same quota, Tulchin wants a online, cell, and landline if it is a DNQ
            # flex=0, tri=False, raw=False
            q = Quota(self.get_name(), quota_name, int(quota_limit), question_name, int(question_code), self.nSize, nsize_override, flex, self.trisplit, self.raw)
            if (quota_name.lower().__contains__("dnq")):
                q = Quota(self.get_name(), quota_name + " - Landline", int(quota_limit), "pMode", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                self.quotas.append(q)
                if (expand):
                    q = Quota(self.get_name(), quota_name + " - Landline", int(quota_limit), "PhoneType", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    self.quotas.append(q)
                    q = Quota(self.get_name(), quota_name + " - Cell", int(quota_limit), question_name, int(question_code), self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + " - Cell", int(quota_limit), "pMode", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                self.quotas.append(q)
                if (expand):
                    q = Quota(self.get_name(), quota_name + " - Cell", int(quota_limit), "PhoneType", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    self.quotas.append(q)
                    q = Quota(self.get_name(), quota_name + " - Online", int(quota_limit), question_name, int(question_code), self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + " - Online", int(quota_limit), "pMode", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                self.quotas.append(q)
                if (expand):
                    q = Quota(self.get_name(), quota_name + " - Online", int(quota_limit), "pMode", 3, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    self.quotas.append(q)
                    q = Quota(self.get_name(), quota_name, int(quota_limit), question_name, int(question_code), self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    self.quotas.append(q)
            else:
                self.quotas.append(q)
            self.limits.append(int(quota_limit))
        elif (self.trisplit == False):
            q = Quota(self.get_name(), quota_name, int(quota_limit), question_name, int(question_code), self.nSize, nsize_override, flex, self.trisplit, self.raw)
            self.quotas.append(q)
            self.limits.append(int(quota_limit))
        else:
            # tri split quotas include (Phone, email, text)->(self)(pMode)
            q = Quota(self.get_name(), quota_name + "- Phone", int(quota_limit), question_name, int(question_code), self.nSize, nsize_override, flex, self.trisplit, self.raw)
            self.limits.append(int(quota_limit))
            q.calculate_limit(0)
            self.quotas.append(q)
            q = Quota(self.get_name(), quota_name + "- Phone", int(quota_limit), "pMode", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            if (expand):
                q.calculate_limit(0)
                q = Quota(self.get_name(), quota_name + "- Email", int(quota_limit), question_name, int(question_code), self.nSize, nsize_override, flex, self.trisplit, self.raw)
                self.quotas.append(q)
            q.calculate_limit(1)
            self.quotas.append(q)
            q = Quota(self.get_name(), quota_name + "- Email", int(quota_limit), "pMode", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            if (expand):
                q.calculate_limit(1)
                q = Quota(self.get_name(), quota_name + "- Text", int(quota_limit), question_name, int(question_code), self.nSize, nsize_override, flex, self.trisplit, self.raw)
                self.quotas.append(q)
            q.calculate_limit(2)
            self.quotas.append(q)
            q = Quota(self.get_name(), quota_name + "- Text", int(quota_limit), "pMode", 3, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            if (expand):
                q.calculate_limit(2)
                self.quotas.append(q)

    def validate_quotas(self):
        warnings = []
        for quota in self.quotas:
            count = 0
            # check quota names are unique
            for i in range(0, len(self.quotas)):
                if (quota.name == self.quotas[i].name):
                    # repeats are only fine if qname and qcode don't match as well
                    if ((quota.question_name == self.quotas[i].question_name)):
                        count += 1
            if (count > 1 and self.client != "tulchin"):
                warnings.append("WARNING: Quota with the name " + quota.name + " repeated in group " + self.get_name())

            # quotas with 0% quota limit must be set to a counter
            if (quota.limit == 0):
                warnings.append("WARNING: Quota " + quota.name + " in group " + self.get_name() + " limit percentage is 0. Quota limit will be set to 0 and made inactive")
        # check percentages add up to 100
        sum = 0
        for limit in self.limits:
            if (limit != -1):
                sum += limit
        if (sum != 100):
            if (not self.raw):
                warnings.append("WARNING: Sum of percentages in quota: " + self.get_name() + " Do not add up to 100% at: " + str(sum) +"%")
        for i in range(0, len(self.quotas)):
            self.quotas[i].calculate_limit()
        warnings.sort()
        for warning in warnings:
            print(warning, file=sys.stderr)

    def display_quotas(self):
        # sort quotas by Question name
        self.quotas.sort(key=lambda x: x.question_name, reverse=False)
        # sort quotas by Question code
        self.quotas.sort(key=lambda x: x.q_code, reverse=False)
        #sort quotas by Quota name
        #self.quotas.sort(key=lambda x: x.fullname, reverse=False)
        group_data = ""
        for quota in self.quotas:
            group_data += quota.display()
        return group_data


# Program
if __name__ == "__main__":
    # Program logic vars
    trisplit = False
    gflex = 0
    q_prefix = ""
    is_raw = False

    # init command line arg buffers
    config.init()
    qc.parse_commandline_args()

    gQuota_groups = []

    #attempt to open file
    with open(config.filename, "r") as f:
        contents = f.read().replace("%", "").split("\n")
        for i in range(0, len(contents)):
            # if a line is empty, toss it
            line = contents[i].strip("\n")
            if (line == ""):
                continue
            # reset logic globals
            trisplit = False
            gflex = 0
            is_raw = False
            q_prefix = ""
            line = line.split("\t");
            # if a line contains only 1 thing, attempt to parse a Quota group
            if (len(line) == 1):
                line = line[0]
                # tri mode
                if (line.find("(tri)") != -1):
                    line = line.replace("(tri)", "")
                    trisplit = True
                # flex
                if (line.find("(flex ") != -1):
                    index = line.find("(flex ")
                    line = line.replace("(flex ", "")
                    gflex = int(line[index])
                    line = line[:index] + line[index+2:]
                # group name
                q_prefix = line.split(" ")[0]
                # raw
                if (line.find("(raw)") != -1):
                    line = line.replace("(raw)", "")
                    is_raw = True
                gQuota_groups.append(QuotaGroup(q_prefix, trisplit, gflex, is_raw, config.client, config.nSize, config.trimode_nsize))
                continue
            else:
                # Empty percentage means 0
                if (line[1] == ""):
                    line[1] = 0
                question_code = line[3].replace(" ", "")
                question_code = question_code.split(",")
                #add_quota(self, quota_name, quota_limit, question_name, question_code, nsize_override, expand=True)
                if (len(question_code) == 1):
                    gQuota_groups[len(gQuota_groups)-1].add_quota(line[0], int(line[1]), line[2], int(question_code[0]), trisplit)
                else:
                    for i in range(0, len(question_code)):
                        gQuota_groups[len(gQuota_groups)-1].add_quota(line[0], int(line[1]), line[2], int(question_code[i]), trisplit, i==0)

    print("DATA VALIDATION RESULTS:\n")
    for group in gQuota_groups:
        group.validate_quotas()
    full_data = '"Quota Name",Type,"Question Code","Option Code","Quota Limit","Quota Settings"' + "\n"
    for group in gQuota_groups:
        full_data += group.display_quotas()
    dispmode = input("\n\nDisplay in console: press C\nWrite to " + config.filename.split(".")[0] + "_quotas_csv.csv" + ": press F\nBoth, press B\n").lower()
    if (dispmode == "c"):
        print(full_data)
    if (dispmode == "b"):
        dispmode = "f"
        print(full_data)
    if (dispmode == "f"):
        with open(config.filename.split(".")[0] + "_quotas.csv", "w") as f:
            f.write(full_data)
