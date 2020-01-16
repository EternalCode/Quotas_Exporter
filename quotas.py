#!/usr/bin/env python3
import sys
import config
import quotas_cmdline as qc

# Assumptions
#
# Phonetype: 1 = Landline, 2 = Cellphone
# Mode: 1 = Phone, 2 = Email, 3 = Text
def rd(x):
    val = str(x).split(".")
    if (len(val) == 1):
        return val
    elif (int(val[1][0]) >= 5):
        return int(x) + 1
    else:
        return int(x)


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
        self.calculated = False
        self.max = 0
        self.delta = 0
        self.is_duplicate = False

        if (self.flex > 0 and (self.max + self.delta) > 0):
            self.fullname += " - Flex " + str(self.flex) + "% " + " +/-" + str(self.delta)

    def validify(self):
        if (self.limit == 0):
            self.isactive = False
        elif(self.limit == -1):
            self.isactive = False
            self.limit = self.counter_limit
        if (self.fullname.lower().find("offsetter") != -1):
            self.isactive = False

    def calculate_limit(self, nsize=None):
        self.validify()

        if(self.calculated):
            return
        if (self.raw):
            return
        if (self.limit == self.counter_limit):
            return
        size = self.size
        if (nsize != None):
            size = nsize
        self.limit = (size * (self.limit / 100))
        self.max = self.limit;
        # flex
        if (self.flex > 0):
            self.delta = rd((self.flex / 100) * size)
            self.limit += self.delta
            self.fullname += " - Flex " + str(self.flex) + "% " + " +/-" + str(self.delta)
        self.limit = rd(self.limit)
        self.calculated = True

    def display(self):
        simple = "Simple"
        data = ""
        nlow = self.fullname.lower()
        self.limit = int(self.limit)
        if (self.fullname.lower().__contains__("dnq")):
            self.limit = 0
        elif(self.limit < 5):
            self.isactive = False
        if (self.tri):
            self.isactive = False

        quota_settings = '"{""action"":""1"",""autoload_url"":""1"",""active"":""' + str(int(self.isactive)) + '"",""qls"":[{""quotals_language"":""en"",""quotals_name"":""x"",""quotals_url"":"""",""quotals_urldescrip"":"""",""quotals_message"":""Sorry your responses have exceeded a quota on this survey.""}]}"'
        quota_settings_dnq = '"{""action"":""1"",""autoload_url"":""1"",""active"":""' + str(int(self.isactive)) + '"",""qls"":[{""quotals_language"":""en"",""quotals_name"":""x"",""quotals_url"":"""",""quotals_urldescrip"":"""",""quotals_message"":""Thank and Terminate.""}]}"'
        quota_settings_dnq_online = '"{""action"":""1"",""autoload_url"":""1"",""active"":""' + str(int(self.isactive)) + '"",""qls"":[{""quotals_language"":""en"",""quotals_name"":""x"",""quotals_url"":"""",""quotals_urldescrip"":"""",""quotals_message"":""Thank you for your time.""}]}"'
        quota_settings_reschedule = '"{""action"":""1"",""autoload_url"":""1"",""active"":""' + str(int(self.isactive)) + '"",""qls"":[{""quotals_language"":""en"",""quotals_name"":""x"",""quotals_url"":"""",""quotals_urldescrip"":"""",""quotals_message"":""Reschedule and end call.""}]}"'

        if (nlow.lower().__contains__("reschedule")):
            data =(self.fullname + "," + simple + "," + self.question_name + "," + str(self.q_code) + "," +
            str(self.limit) + "," + quota_settings_reschedule)
        elif (self.fullname.lower().__contains__("dnq")):
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
    def __init__(self, group_name, trisplit, flex, raw, cli, nsize, tri_sizes, dual):
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
        self.dual = dual
        self.splitQuotas = False;

    def get_name(self):
        return self.group_name

    def add_quota(self, quota_name, quota_limit, question_name, question_code, nsize_override, expand=True):
        flex = 0
        if (self.flex > 0):
            flex = self.flex
        if (config.client == "tulchin"):
            # for the same quota, Tulchin wants a online, cell, and landline if it is a DNQ
            if (self.get_name().lower().__contains__("dnq")):
                q = Quota(self.get_name(), quota_name, float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = not(expand)
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + " - Landline", float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = not(expand)
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + " - Cell", float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = not(expand)
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + " - Online", float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = not(expand)
                self.quotas.append(q)
                # add the mode specifiers only once
                if (expand):
                    q = Quota(self.get_name(), quota_name + " - Landline", float(quota_limit), "pMode", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    q.is_duplicate = True
                    self.quotas.append(q)
                    q = Quota(self.get_name(), quota_name + " - Landline", float(quota_limit), "PhoneType", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    q.is_duplicate = True
                    self.quotas.append(q)
                    q = Quota(self.get_name(), quota_name + " - Cell", float(quota_limit), "pMode", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    q.is_duplicate = True
                    self.quotas.append(q)
                    q = Quota(self.get_name(), quota_name + " - Cell", float(quota_limit), "PhoneType", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    q.is_duplicate = True
                    self.quotas.append(q)
                    q = Quota(self.get_name(), quota_name + " - Online", float(quota_limit), "pMode", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    q.is_duplicate = True
                    self.quotas.append(q)
                    q = Quota(self.get_name(), quota_name + " - Online", float(quota_limit), "pMode", 3, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                    q.is_duplicate = True
                    self.quotas.append(q)
            else:
                q = Quota(self.get_name(), quota_name, float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = not(expand)
                self.quotas.append(q)
            if (expand):
                self.limits.append(float(quota_limit))
        elif (self.dual == True):
            # Dual modes are Phone and Email. Split Quotas are
            q = Quota(self.get_name(), quota_name + "- Phone", float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            q.calculate_limit(config.dualmode[0])
            q.is_duplicate = not(expand)
            self.quotas.append(q)
            q = Quota(self.get_name(), quota_name + " - Phone", float(quota_limit), "pMode", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            q.calculate_limit(config.dualmode[0])
            q.is_duplicate = not(expand)
            self.quotas.append(q)
            q = Quota(self.get_name(), quota_name + "- Email", float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            q.calculate_limit(config.dualmode[1])
            q.is_duplicate = not(expand)
            self.quotas.append(q)
            q = Quota(self.get_name(), quota_name + " - Email", float(quota_limit), "pMode", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            q.calculate_limit(config.dualmode[1])
            q.is_duplicate = not(expand)
            self.quotas.append(q)
            # if show split quotas, then generate them
            if (config.splitab == True and self.splitQuotas):
                # Phone split A
                q = Quota(self.get_name(), quota_name + "- Phone SplitA", float(quota_limit / 2), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[0])
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + "- Phone SplitA", float(quota_limit / 2), "SplitAB", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[0])
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + "- Phone SplitA", float(quota_limit / 2), "pMode", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[1])
                q.is_duplicate = True
                self.quotas.append(q)
                # Phone splt B
                q = Quota(self.get_name(), quota_name + "- Phone SplitB", float(quota_limit / 2), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[0])
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + "- Phone SplitB", float(quota_limit / 2), "SplitAB", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[0])
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + "- Phone SplitB", float(quota_limit / 2), "pMode", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[1])
                q.is_duplicate = True
                self.quotas.append(q)
                # Email Split A
                q = Quota(self.get_name(), quota_name + "- Email SplitA", float(quota_limit / 2), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[1])
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + "- Email SplitA", float(quota_limit / 2), "SplitAB", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[1])
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + "- Email SplitA", float(quota_limit / 2), "pMode", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[1])
                q.is_duplicate = True
                self.quotas.append(q)
                # Email Split B
                q = Quota(self.get_name(), quota_name + "- Email SplitB", float(quota_limit / 2), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[1])
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + "- Email SplitB", float(quota_limit / 2), "SplitAB", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[1])
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + "- Email SplitB", float(quota_limit / 2), "pMode", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.calculate_limit(config.dualmode[1])
                q.is_duplicate = True
                self.quotas.append(q)
            if (expand):
                self.limits.append(float(quota_limit))
        elif (self.trisplit == False and self.splitQuotas):
            # Regular split quotas for single mode projects
            q = Quota(self.get_name(), quota_name, float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            q.is_duplicate = not(expand)
            self.quotas.append(q)
            if (expand):
                self.limits.append(float(quota_limit))
            if (config.splitab == True):
                q = Quota(self.get_name(), quota_name + " Split A", float(quota_limit / 2), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + " Split A", float(quota_limit / 2), "SplitAB", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + " Split B", float(quota_limit / 2), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = True
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + " Split B", float(quota_limit / 2), "SplitAB", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = True
                self.quotas.append(q)
        elif (self.trisplit == False):
            # Regular quotas
            q = Quota(self.get_name(), quota_name, float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            q.is_duplicate = not(expand)
            self.quotas.append(q)
            if (expand):
                self.limits.append(float(quota_limit))
        else:
            # tri split quotas include (Phone, email, text)->(self)(pMode)
            # TODO: Split Quotas
            if (expand):
                self.limits.append(float(quota_limit))
            q = Quota(self.get_name(), quota_name + "- Phone", float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            q.is_duplicate = not(expand)
            q.calculate_limit(config.trimode_nsize[0])
            self.quotas.append(q)
            q = Quota(self.get_name(), quota_name + "- Email", float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            q.is_duplicate = not(expand)
            q.calculate_limit(config.trimode_nsize[1])
            self.quotas.append(q)
            q = Quota(self.get_name(), quota_name + "- Text", float(quota_limit), question_name, question_code, self.nSize, nsize_override, flex, self.trisplit, self.raw)
            q.is_duplicate = not(expand)
            q.calculate_limit(config.trimode_nsize[2])
            self.quotas.append(q)
            # add mode specifiers only once
            if (expand):
                q = Quota(self.get_name(), quota_name + "- Phone", float(quota_limit), "pMode", 1, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = True
                q.calculate_limit(config.trimode_nsize[0])
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + "- Email", float(quota_limit), "pMode", 2, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = True
                q.calculate_limit(config.trimode_nsize[1])
                self.quotas.append(q)
                q = Quota(self.get_name(), quota_name + "- Text", float(quota_limit), "pMode", 3, self.nSize, nsize_override, flex, self.trisplit, self.raw)
                q.is_duplicate = True
                q.calculate_limit(config.trimode_nsize[2])
                self.quotas.append(q)



    def validate_quotas(self):
        warnings = []
        for quota in self.quotas:
            count = 0
            # check quota names are unique
            for i in range(0, len(self.quotas)):

                if (quota.fullname == self.quotas[i].fullname and self.quotas[i].is_duplicate == False):
                    # repeats are only fine if qname and qcode don't match as well
                    if ((quota.question_name == self.quotas[i].question_name)):
                        count += 1
            if (count > 1):
                warnings.append("WARNING: Quota with the name " + quota.fullname + " repeated in group " + self.get_name())

            # quotas with 0% quota limit must be set to a counter
            if (quota.limit == 0 and not (quota.fullname.lower().__contains__("dnq"))):
                warnings.append("WARNING: Quota " + quota.name + " in group " + self.get_name() + " limit percentage is 0. Quota limit will be set to 0 and made inactive")
        # check percentages add up to 100, if group isn't a DNQ/Reschedule
        if (not((self.group_name.lower().__contains__("dnq") or self.group_name.lower().__contains__("reschedule")))):
            sum = 0
            for limit in self.limits:
                if (limit != -1):
                    sum += limit
            if (sum != 100):
                if (not self.raw):
                    warnings.append("WARNING: Sum of percentages in quota: " + self.get_name() + " Do not add up to 100% at: " + str(sum) +"%")
                else:
                    sum = 0
                    for quota in self.quotas:
                        sum += quota.limit
                    if (sum != config.nSize):
                        warnings.append("WARNING: Sum of raw limits don't add to the end size of " + str(config.nSize) + " at " + str(sum))

        for i in range(0, len(self.quotas)):
            self.quotas[i].calculate_limit()
        warnings.sort()
        for warning in warnings:
            print(warning, file=sys.stderr)
        return len(warnings)


    def display_quotas(self):
        # sort quotas by Question name
        #print("display Quotas for group: " + self.get_name());
        self.quotas.sort(key=lambda x: x.question_name, reverse=False)
        # sort quotas by Question code
        self.quotas.sort(key=lambda x: int(x.q_code), reverse=False)
        #sort quotas by Quota name
        self.quotas.sort(key=lambda x: x.fullname, reverse=False)
        group_data = ""
        for quota in self.quotas:
            group_data += quota.display()
        return group_data


# Program
if __name__ == "__main__":
    # Program logic vars
    trisplit = False
    isdual = False
    gflex = 0
    is_raw = False
    q_prefix = ""
    isSplit = True

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
            isdual = False
            gflex = 0
            is_raw = False
            q_prefix = ""
            isSplit = True
            line = line.split("\t");
            # if a line contains only 1 thing, attempt to parse a Quota group
            if (len(line) == 1):
                line = line[0]
                # tri mode
                if (line.find("(tri)") != -1):
                    line = line.replace("(tri)", "")
                    trisplit = True
                # dual mode
                if (line.find("(dual)") != -1):
                    line = line.replace("(dual)", "")
                    isdual = True
                # un-split
                if (line.find("(us)") != -1):
                    line = line.replace("(us)", "")
                    isSplit = False
                # flex
                if (line.find("(flex ") != -1):
                    index = line.find("(flex ")
                    line = line.replace("(flex ", "")
                    val = "";
                    for i in range(index, len(line)):
                        if (line[i] == ")"):
                            break
                        else:
                            val += line[i]
                    line = line[:index] + line[index+len(val)+1:]
                    gflex = int(val)
                # raw
                if (line.find("(raw)") != -1):
                    line = line.replace("(raw)", "")
                    is_raw = True
                # group name
                q_prefix = line.split(" ")[0]
                gQuota_groups.append(QuotaGroup(q_prefix, trisplit, gflex, is_raw, config.client, config.nSize, config.trimode_nsize, isdual))
                if (config.splitab == True):
                    gQuota_groups[len(gQuota_groups)-1].splitQuotas = isSplit
                continue
            else:
                # Empty percentage means 0
                if (line[1] == ""):
                    line[1] = 0
                #print(line)
                question_code = line[3].replace(" ", "").split(",")
                #add_quota(self, quota_name, quota_limit, question_name, question_code, nsize_override, expand=True)
                quota_grp = gQuota_groups[len(gQuota_groups)-1]
                if (len(question_code) == 1):
                    quota_grp.add_quota(line[0], float(line[1]), line[2], question_code[0], trisplit)
                else:
                    for i in range(0, len(question_code)):
                        gQuota_groups[len(gQuota_groups)-1].add_quota(line[0], float(line[1]), line[2], question_code[i], trisplit, i==0)
                        if (i != 0):
                            quota_grp.quotas[len(quota_grp.quotas) - 1].is_duplicate = True

    print("DATA VALIDATION RESULTS:\n")
    sum = 0
    for group in gQuota_groups:
        sum += group.validate_quotas()
    if (sum == 0):
        print("All OK.")
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
        with open(config.outname, "w") as f:
            f.write(full_data)
