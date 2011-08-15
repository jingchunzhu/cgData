
import csv
import CGData
import CGData.TSVMatrix

class GenomicMatrix(CGData.TSVMatrix.TSVMatrix):

    def __init__(self):
        CGData.TSVMatrix.TSVMatrix.__init__(self)
        
    def is_link_ready(self):
        if self.attrs.get( ':sampleMap', None ) is None:
            return False
        return True

    def get_probe_list(self):
        return self.get_rows()

    def get_sample_list(self):
        return self.get_cols()

    def sample_rename(self, old_sample, new_sample):
        self.col_rename( old_sample, new_sample )

    def probe_remap(self, old_probe, new_probe):
        self.row_rename( old_probe, new_probe )

    def remap(self, alt_map, skip_missing=False):
        valid_map = {}
        for alt in alt_map:
            valid_map[alt.aliases[0]] = True
            if not skip_missing or alt.name in self.probe_hash:
                self.probe_remap(alt.name, alt.aliases[0])
        if skip_missing:
            remove_list = []
            for name in self.probe_hash:
                if not name in valid_map:
                    remove_list.append(name)
            for name in remove_list:
                del self.probe_hash[name]

    def remove_null_probes(self, threshold=0.0):
        remove_list = []
        for probe in self.probe_hash:
            null_count = 0.0
            for val in self.probe_hash[probe]:
                if val is None:
                    null_count += 1.0
            nullPrec = null_count / float(len(self.probe_hash[probe]))
            if 1.0 - nullPrec <= threshold:
                remove_list.append(probe)
        for name in remove_list:
            del self.probe_hash[name]

    def write_gct(self, handle, missing=''):
        write = csv.writer(handle, delimiter="\t", lineterminator='\n')
        sampleList = self.get_sample_list()
        sampleList.sort(lambda x, y: self.sampleList[x] - self.sampleList[y])
        write.writerow(["#1.2"])
        write.writerow([len(self.probe_hash), len(sampleList)])
        write.writerow(["NAME", "Description"] + sampleList)
        for probe in self.probe_hash:
            out = [probe, probe]
            for sample in sampleList:
                val = self.probe_hash[probe][self.sampleList[sample]]
                if val is None:
                    val = missing
                out.append(val)
            write.writerow(out)
